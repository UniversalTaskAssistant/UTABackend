from uta.config import *
import json
import re


class _TaskUIChecker:
    def __init__(self, model_manager):
        self.__model_manager = model_manager

        # Initialize the base prompt template
        self.__action_prompt = 'What is the appropriate action to the related element for proceeding the task in the current UI. \n' \
                               '!!!Action Options:\n' \
                               '1. Click; 2.Input (Input text); 3.Scroll (Vertically scroll the element); 4.Swipe (Horizontally swipe the element); 5. None (The task is completed).\n' \
                               '!!!Notes:\n' \
                               '1. Respond only in this JSON format: {{"Action": "<type>", "Element Id": "<id>", "Input Text": "<text>", "Reason": "<why>"}}. \n' \
                               '2. The "Input Text" is the content of Input action, the Element Id is an integer. \n' \
                               '3. This UI has been proved as a related UI to the task, you have to choose one of the given actions.\n' \
                               '4. Ensure the chosen action supports the element (clickable to click or scrollable to scroll). \n' \
                               '5. Select "Input" only if the Keyboard is active; otherwise, first activate the keyboard by clicking a relevant element (e.g., input bar).\n' \
                               '!!!Examples:\n' \
                               '1. {{"Action": "Click", "Element Id": "3", "Reason": "Open Settings to access task settings"}}. \n' \
                               '2. {{"Action": "Input", "Element Id": "4", "Input Text": "wallpaper", "Reason": "use word \"wallpaper\" to search ways of setting background."}}.\n' \
                               '3. {{"Action": "Scroll", "Element Id": "3", "Reason": "Scroll down to view more elements"}}\n'

        self.__back_prompt = 'Is there an element in the current UI that can be clicked to navigate back or close the current unrelated UI to proceed the task "{task}"? \n' \
                             '!!!Answer the following three questions:\n' \
                             '1. "Yes" or "No" - whether such a go-back/close element exists. \n' \
                             '2. Element Id - provide the ID if "Yes", else "None". \n' \
                             '3. Reason - a brief explanation. \n' \
                             '!!!Notes: \n' \
                             '- ONLY use this JSON format to provide your answer: {{"Can": "<Yes or No>", "Element Id": "<ID or None>", "Reason": "<description>"}}.\n' \
                             '- Select a clickable element from the UI hierarchy. \n' \
                             '- If not None, then Element Id must be an integer.\n' \
                             '!!!Examples: \n' \
                             '1. {{"Can": "Yes", "Element Id": 2, "Reason": "Navigates to the previous screen"}}.\n' \
                             '2. {{"Can": "No", "Element Id": "None", "Reason": "No back button present, please search youtube for video watching"}}.\n'

        self.__relation_prompt = 'What is the relation between this UI and the task "{task}" and why? ' \
                                 '!!!Relation Options:\n'\
                                 '1. Directly related: This UI contains a clickable or scrollable element directly related to proceeding the task but has not reached the final page for the task. \n' \
                                 '2. Indirectly related: This UI presents no directly related element to the task, but it has some elements leads to a related UI or elements for the task (e.g., Option button). \n' \
                                 '3. Unrelated: This UI does not relate to the task or sub-tasks at all. \n' \
                                 '4. Almost Complete: The task can be completed with one more action, which should be performed manually by the user. This option should be selected if the next action directly completes the task (e.g., the final step to increase volume).\n' \
                                 '!!!Notes: \n' \
                                 '1. If the relation is related, give the Element Id (int) of the related element, otherwise give "None" for the Element Id.\n' \
                                 '2. Respond only in this JSON format: {{"Relation": "<relation>", "Element Id": "<ID or None>", "Reason": "<one-sentence reason>"}}.\n' \
                                 '3. If in the previous step the search bar is clicked for searching things, then in this step the relation should be "Directly related" and searching keyword should be entered.\n' \
                                 '4. If the UI indicates the task has nearly reached completion (requiring just one final user action), select "Almost Complete".\n' \
                                 '!!!Output Examples: \n' \
                                 '{{"Relation": "Indirectly related", "Element Id": 2, "Reason": "The current UI has a search bar to search for "Turn on voice"."}}.\n'

    '''
    **************
    *** Basics ***
    **************
    '''
    @staticmethod
    def wrap_task_context(task):
        """
        Wrap up task info to put in the fm prompt
        Args:
            task (Task)
        Return:
            prompt (str): The wrapped prompt
        """
        prompt = '!!!Context:\n'
        prompt += 'Keyboard active: ' + str(task.keyboard_active) + '.\n'
        if task.step_hint is not None:
            prompt += "(Additional step hints to proceed the task:" + str(task.step_hint) + ')\n'
            # if len(task.user_clarify) > 0:
        #     prompt += '(Additional information and commands for the task:' + str(task.user_clarify) + ')\n'
        # if len(task.subtasks) > 0:
        #     prompt += '(Potential subtasks and steps to complete the task: ' + str(task.subtasks) + '.)\n'
        return prompt

    @staticmethod
    def wrap_task_history(task):
        """
        Wrap up task info to put in the fm prompt
        Args:
            task (Task)
        Return:
            prompt (str): The wrapped prompt
        """
        prompt = ''
        if len(task.actions) > 0:
            prompt += '!!!Action history for this task - MUST NOT REPEAT PREVIOUS ACTIONS:\n ' + str(task.actions) + '.\n'
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
                                                {'role': 'user', 'content': f'This is a view hierarchy of a UI:\n'
                                                                            f'{str(ui_data.element_tree)}\n\n{prompt}'}]
            else:
                task.conversation_automation.append({'role': 'user', 'content': prompt})
            resp = self.__model_manager.send_fm_conversation(task.conversation_automation, printlog=printlog)
            task.conversation_automation.append(resp)
            return resp
        except Exception as e:
            print(resp)
            raise e

    '''
    *********************
    *** Task-UI Check ***
    *********************
    '''
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
            prompt = self.wrap_task_context(task)
            prompt += self.__relation_prompt.format(task=task.task_description)
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
            prompt = self.__action_prompt.format(task=task.task_description)
            prompt += self.wrap_task_history(task)
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
            prompt = self.__back_prompt.format(task=task.task_description)
            # Ask FM
            resp = self.check_ui_task(ui_data=ui_data, task=task, prompt=prompt, printlog=printlog)
            task.res_go_back_check = self.transfer_to_dict(resp)
            print(task.res_go_back_check)
            return task.res_go_back_check
        except Exception as e:
            print(resp)
            raise e