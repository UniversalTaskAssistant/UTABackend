from uta.config import *
import json
import re


class _TaskUIChecker:
    def __init__(self, model_manager):
        self.__model_manager = model_manager

        # Initialize the base prompt template
        self.__action_prompt = 'This UI is proved to be related to the task "{task}". ' \
                               'The Element Id {element_id} is an element in the UI that should be operated to succeed the task.' \
                               'Determine the appropriate action to the selected element for completing the task in the current UI. \n' \
                               '!!!Answer the following questions:\n' \
                               '1. Action - one of the following types: Click; Input (Input text); ' \
                               'Scroll (Vertically scroll the element); Swipe (Horizontally swipe the element). ' \
                               'None (You believe the task has been almost completed as per the previous actions).\n' \
                               '2. Element Id: the id of the target element to perform the action, just repeat what is given.\n' \
                               '3. Reason: short explanation why you do the action.\n' \
                               '4. Input Text - optional, only if the Action type is Input.\n' \
                               '!!!Notes:\n' \
                               '- ONLY use this JSON format to provide your answer: {{"Action": "<type>", "Element Id": "<id>", "Input Text": "<text>", "Reason": "<why>"}}. \n' \
                               '- This UI has been proved as a related UI to the task, you have to perform one of the given action.\n' \
                               '- Select "Input" only if the keyboard is active; otherwise, first activate the keyboard by clicking a relevant element (e.g., input bar).\n' \
                               '- Ensure the chosen action supports the element (clickable to click or scrollable to scroll). \n' \
                               '- If current UI is related to phone settings, and there is a searching bar, you should firstly try to search relevant options in the searching bar.\n' \
                               '- If not None, then Element Id must in an integer.\n' \
                               '!!!Examples:\n' \
                               '1. {{"Action": "Click", "Element Id": "3", "Reason": "Open Settings to access task settings"}}. \n' \
                               '2. {{"Action": "Input", "Element Id": "4", "Input Text": "Download Trump", "Reason": "Type in the name to follow the account."}}.\n' \
                               '3. {{"Action": "Scroll", "Element Id": "3", "Reason": "Scroll down to view more elements"}}\n'

        self.__back_prompt = 'Is there an element in the current UI that can be clicked to navigate back or close the current unrelated UI to assist in completing the task "{task}"? \n' \
                             '!!!Answer the following three questions:\n' \
                             '1. "Yes" or "No" - whether such a go-back/close element exists. \n' \
                             '2. Element Id - provide the ID if "Yes", else "None". \n' \
                             '3. Reason - a brief explanation. \n' \
                             '!!!Notes: \n' \
                             '- ONLY use this JSON format to provide your answer: {{"Can": "<Yes or No>", "Element Id": "<ID or None>", "Description": "<description>"}}.\n' \
                             '- Select a clickable element from the UI hierarchy. \n' \
                             '- If not None, then Element Id must in an integer.\n' \
                             '!!!Examples: \n' \
                             '1. {{"Can": "Yes", "Element Id": 2, "Reason": "Navigates to the previous screen", "Description": "Click on the \'Back\' button"}}.\n' \
                             '2. {{"Can": "No", "Element Id": "None", "Reason": "No back button present, please search youtube for video watching", "Description": "None"}}.\n'

        self.__relation_prompt = 'What is the relation between this UI and the task "{task}" and why? ' \
                                 '!!!Answer the following three questions:\n' \
                                 '1. whether the UI is related to the task.' \
                                 'Choose from the four options.\n' \
                                 '!!!Options: \n' \
                                 'Directly related: This UI has an element directly related to the task or its sub-tasks and steps. \n' \
                                 'Indirectly related: This UI has no direct element, but it has some elements leads to a related UI for the task or its subtasks. \n' \
                                 'Unrelated: This UI does not relate to the task or sub-tasks at all. \n' \
                                 'Almost Complete: The task can be completed with one more action, which should be performed manually by the user. This option should be selected if the next action directly completes the task (e.g., the final step to increase volume).\n' \
                                 '2. Element Id that should be operated to proceed the task, the supported operation includes Click; Input (Input text); ' \
                                 'Scroll (Vertically scroll the element); Swipe (Horizontally swipe the element), so besides clicking, searching bar and scroll down screen to check more elements can be options.' \
                                 'If the task is "Almost Complete" or "Unrelated", Element Id should be "None".\n' \
                                 '3. Reason that explains your decision.' \
                                 '!!!Notes: \n' \
                                 '- Responses must adhere to this JSON format: {{"Relation": "<relation>", "Element Id": "<ID or None>", "Reason": "<reason>"}}.\n' \
                                 '- If the UI indicates the task has nearly reached completion (requiring just one final user action), select "Almost Complete".\n' \
                                 '- App {involved_app_package} is selected by user to finish this task, and now the app has been opened and current UI is one of the UI in the app.\n' \
                                 '- If current UI is related to phone settings, and there is a searching bar, you should firstly try to search relevant options in the searching bar.\n' \
                                 '- You must return "Relation" and "Element Id" in you returned json format result. If not None, then Element Id must in an integer.\n' \
                                 '!!!Examples: \n' \
                                 '{{"Relation": "Indirectly related", "Element Id": 2, "Reason": "The current UI is the home screen of the messaging app, but there\'s no direct element related to turning off vibration for texts. The task of turning off vibration for texts might require navigating to the settings of the messenger but there\'s no direct option visible in the hierarchy. However, the search bar (Element Id: 2) could possibly lead to settings or options related to vibration, hence it should be clicked to proceed to the task."}}.\n'

    @staticmethod
    def wrap_task_info_before(task):
        """
        Wrap up task info to put in the fm prompt
        Args:
            task (Task)
        Return:
            prompt (str): The wrapped prompt
        """
        prompt = '!!!Context:\n'
        prompt += '(Keyboard active: ' + str(task.keyboard_active) + ').\n'
        # if len(task.user_clarify) > 0:
        #     prompt += '(Additional information and commands for the task:' + str(task.user_clarify) + ')\n'
        # if len(task.subtasks) > 0:
        #     prompt += '(Potential subtasks and steps to complete the task: ' + str(task.subtasks) + '.)\n'
        return prompt

    @staticmethod
    def wrap_task_info_after(task):
        """
        Wrap up task info to put in the fm prompt
        Args:
            task (Task)
        Return:
            prompt (str): The wrapped prompt
        """
        prompt = ''
        if len(task.actions) > 0:
            prompt += '(Action history for this task - avoid repetition: ' + str(task.actions) + '.)\n'
            prompt += 'Given the above actions, suggest a new action that progresses the task without repeating previous actions.\n'
        return prompt

    @staticmethod
    def transfer_to_dict(resp):
        """
        Transfer string model returns to dict format
        Args:
            resp (dict): The model returns.
        Return:
            resp_dict (dict): The transferred dict.
        """
        try:
            return json.loads(resp['content'])
        except Exception as e:
            regex = r'"([A-Za-z ]+?)":\s*(".*?[^\\]"|\'.*?[^\\]\')|\'([A-Za-z ]+?)\':\s*(\'.*?[^\\]\'|".*?[^\\]")'
            attributes = re.findall(regex, resp['content'])
            resp_dict = {}
            for match in attributes:
                key = match[0] if match[0] else match[2]  # Select the correct group for the key
                value = match[1] if match[1] else match[3]  # Select the correct group for the value
                resp_dict[key] = value
            return resp_dict

    def check_ui_task(self, ui_data, task, prompt, printlog=False):
        """
        Check UI and Task by prompt through foundation model
        """
        try:
            if len(task.conversation_automation) == 0:
                task.conversation_automation = [{'role': 'system', 'content': SYSTEM_PROMPT},
                                                {'role': 'user', 'content': f'This is a view hierarchy of a UI '
                                                                            f'containing various UI blocks and elements:\n'
                                                                            f'{str(ui_data.element_tree)}\n{prompt}'}]
            else:
                task.conversation_automation.append({'role': 'user', 'content': prompt})
            resp = self.__model_manager.send_fm_conversation(task.conversation_automation, printlog=printlog)
            task.conversation_automation.append(resp)
            return resp
        except Exception as e:
            print(resp)
            raise e

    def check_ui_relation(self, ui_data, task, printlog=False):
        """
        Checks the relation between a given ui and a task.
        Args:
            ui_data (UIData): UI data
            task (Task): Task object containing task description for which back navigation is being checked.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            FM response (dict): {"Relation":, "Reason":}
        """
        try:
            print('* Check UI and Task Relation *')
            # Format base prompt
            prompt = self.wrap_task_info_before(task)
            prompt += self.__relation_prompt.format(task=task.task_description,
                                                    involved_app_package=task.involved_app_package)
            prompt += self.wrap_task_info_after(task)
            # Ask FM
            resp = self.check_ui_task(ui_data=ui_data, task=task, prompt=prompt, printlog=printlog)
            task.res_relation_check = self.transfer_to_dict(resp)
            print(task.res_relation_check)
            return task.res_relation_check
        except Exception as e:
            print(resp)
            raise e

    def check_element_action(self, ui_data, task, printlog=False):
        """
        Determines the appropriate action and target element in the UI for a given task.
        Args:
            ui_data (UIData): UI data
            task (Task): Task object containing task description for which back navigation is being checked.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            FM response (dict): {"Action":"Input", "Element Id":3, "Description":, "Reason":, "Input Text": "Download Trump"}
        """
        try:
            print('* Check UI Action and Target Element *')
            # Format base prompt
            prompt = self.wrap_task_info_before(task)
            prompt += self.__action_prompt.format(task=task.task_description, element_id=task.res_relation_check['Element Id'])
            prompt += self.wrap_task_info_after(task)
            # Ask FM
            resp = self.check_ui_task(ui_data=ui_data, task=task, prompt=prompt, printlog=printlog)
            task.res_action_check = self.transfer_to_dict(resp)
            print(task.res_action_check)
            return task.res_action_check
        except Exception as e:
            print(resp)
            raise e

    def check_ui_go_back_availability(self, ui_data, task, printlog=False):
        """
        Checks if there is an element in the UI that can be clicked to navigate back in relation to a given task.
        Args:
            ui_data (UIData): UI data
            task (Task): Task object containing task description for which back navigation is being checked.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            FM response (dict): {"Can":"Yes", "Element Id": 2, "Reason":, "Description":"Click on the "go back" element"}
        """
        try:
            print('* Check Any Action to Go Back to Related UI *')
            # Format base prompt
            prompt = self.wrap_task_info_before(task)
            prompt += self.__back_prompt.format(task=task.task_description)
            prompt += self.wrap_task_info_after(task)
            # Ask FM
            resp = self.check_ui_task(ui_data=ui_data, task=task, prompt=prompt, printlog=printlog)
            task.res_go_back_check = self.transfer_to_dict(resp)
            print(task.res_go_back_check)
            return task.res_go_back_check
        except Exception as e:
            print(resp)
            raise e