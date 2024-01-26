from uta.config import *
import json


class _TaskUIChecker:
    def __init__(self, model_manager):
        self.__model_manager = model_manager

        # Initialize the base prompt template
        self.__action_prompt = 'This UI is proved to be related to the task "{task}". ' \
                               'Determine the appropriate action for completing the task in the current UI. \n' \
                               '!!!Answer the following questions:\n' \
                               '1. Action - one of the following types: Click; Input (Input text); ' \
                               'Scroll (Vertically scroll the element); Swipe (Horizontally swipe the element).\n' \
                               '2. Element id: the id of the target element to perform the action.\n' \
                               '3. Reason: short explanation why you do the action.\n' \
                               '4. Input Text - optional, only if the Action type is Input.\n' \
                               '!!!Notes:\n' \
                               '1. ONLY use this JSON format to provide your answer: {{"Action": "<type>", "Element": "<id>", "Input Text": "<text>", "Reason": "<why>"}}. \n' \
                               '2. This UI has been proved as a related UI to the task, you have to perform one of the given action.\n' \
                               '3. Select "Input" only if the keyboard is active; otherwise, first activate the keyboard by clicking a relevant element (e.g., input bar).\n' \
                               '4. Ensure the chosen element supports the intended action (clickable to click or scrollable to scroll). \n' \
                               '!!!Examples:\n' \
                               '1. {{"Action": "Click", "Element": "3", "Reason": "Open Settings to access task settings"}}. \n' \
                               '2. {{"Action": "Input", "Element": "4", "Input Text": "Download Trump", "Reason": "Type in the name to follow the account."}}.\n' \
                               '3. {{"Action": "Scroll", "Element": "3", "Reason": "Scroll down to view more elements"}}\n'

        self.__back_prompt = 'Is there an element in the current UI that can be clicked to navigate back and assist in completing the task "{task}"? \n' \
                             '!!!Answer the following three questions:\n' \
                             '1. "Yes" or "No" - whether such a go-back element exists. \n' \
                             '2. Element Id - provide the ID if "Yes", else "None". \n' \
                             '3. Reason - a brief explanation. \n' \
                             '!!!Notes: \n' \
                             '1. ONLY use this JSON format to provide your answer: {{"Can": "<Yes or No>", "Element": "<ID or None>", "Description": "<description>"}}.\n' \
                             '2. Select a clickable element from the UI hierarchy. \n' \
                             '!!!Examples: \n' \
                             '1. {{"Can": "Yes", "Element": 2, "Reason": "Navigates to the previous screen", "Description": "Click on the \'Back\' button"}}.\n' \
                             '2. {{"Can": "No", "Element": "None", "Reason": "No back button present", "Description": "None"}}.\n'

        self.__relation_prompt = 'What is the relation between this UI and the task "{task}" and why? Choose from the four options.\n' \
                                 '!!!Options: \n' \
                                 '1. Directly related: This UI has an element directly related to the task or its sub-tasks and steps. \n' \
                                 '2. Indirectly related: This UI has no direct element, but it has some elements leads to a related UI for the task or its subtasks. \n' \
                                 '3. Unrelated: This UI does not relate to the task or sub-tasks at all. \n' \
                                 '4. Completed: The task is already completed. \n' \
                                 '!!!Notes: \n' \
                                 '1. ONLY use this JSON format to provide your answer: {{"Relation": "<relation>", "Reason": "<reason>"}}.\n' \
                                 '2. Some elements may be related to the task, but they might be "selected", which means the task is already completed and the relation should be "Completed".\n' \
                                 '3. Also pay attention to the navigation-bar/multi-tab menu that may have tab or option potentially leading to related pages. \n'

    @staticmethod
    def wrap_task_info(task):
        """
        Wrap up task info to put in the fm prompt
        Args:
            task (Task)
        Return:
            prompt (str): The wrapped prompt
        """
        prompt = '!!!Context:\n'
        prompt += '(Keyboard active: ' + str(task.keyboard_active) + ').\n'
        if len(task.user_clarify) > 0:
            prompt += '(Additional information and commands for the task:' + str(task.user_clarify) + ')\n'
        if len(task.subtasks) > 0:
            prompt += '(Potential subtasks and steps to complete the task: ' + str(task.subtasks) + '.)\n'
        if len(task.actions) > 0:
            prompt += '(Action history for this task - avoid repetition: ' + str(task.actions) + '.)\n'
        if len(task.except_elements_ids) > 0:
            prompt += '(Elements with the following IDs have been proved to be unrelated to this task, exclude them: ' \
                      + str(task.except_elements_ids) + '.)\n'
        return prompt

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
            prompt = self.wrap_task_info(task)
            prompt += self.__relation_prompt.format(task=task.task_description)
            # Ask FM
            resp = self.check_ui_task(ui_data=ui_data, task=task, prompt=prompt, printlog=printlog)
            task.res_relation_check = json.loads(resp['content'])
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
            FM response (dict): {"Action":"Input", "Element":3, "Description":, "Reason":, "Input Text": "Download Trump"}
        """
        try:
            print('* Check UI Action and Target Element *')
            # Format base prompt
            prompt = self.wrap_task_info(task)
            prompt += self.__action_prompt.format(task=task.task_description)
            # Ask FM
            resp = self.check_ui_task(ui_data=ui_data, task=task, prompt=prompt, printlog=printlog)
            task.res_action_check = json.loads(resp['content'])
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
            FM response (dict): {"Can":"Yes", "Element": 2, "Reason":, "Description":"Click on the "go back" element"}
        """
        try:
            print('* Check Any Action to Go Back to Related UI *')
            # Format base prompt
            prompt = self.wrap_task_info(task)
            prompt += self.__back_prompt.format(task=task.task_description)
            # Ask FM
            resp = self.check_ui_task(ui_data=ui_data, task=task, prompt=prompt, printlog=printlog)
            task.res_go_back_check = json.loads(resp['content'])
            print(task.res_go_back_check)
            return task.res_go_back_check
        except Exception as e:
            print(resp)
            raise e
