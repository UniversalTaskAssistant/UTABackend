from uta.config import *
import json


class _TaskUIChecker:
    def __init__(self, model_manager):
        self.__model_manager = model_manager

        # Initialize the base prompt template
        self.__action_prompt = 'Determine the appropriate action for completing the task "{task}" using the current ' \
                               'UI. \n' \
                               'Consider the following action types: Click, Scroll Up, Scroll Down, Swipe ' \
                               'Right, Swipe Left, Long Press, Input. \n' \
                               'Note: Use "Input" only if the keyboard is active; activate the keyboard by clicking ' \
                               'a relevant element if necessary. Ensure the chosen element supports the intended' \
                               ' action. \n' \
                               'Provide a single, most effective action. Avoid repeating actions listed in ' \
                               '{action_history}. \n' \
                               'Exclude elements with IDs {except_elements} as they have been tried and proved to ' \
                               'be unrelated to the task. \n' \
                               'Respond in JSON format: {{"Action": "<type>", "Element": "<id>", "Description": ' \
                               '"<desc>", "Input Text": "<text>", "Reason": "<why>"}}. \n' \
                               'Example: {{"Action": "Click", "Element": "3", "Description": "Open Settings", ' \
                               '"Input Text": "N/A", "Reason": "Access task settings"}}. \n' \
                               'Previous actions: {action_history}, Excluded elements: {except_elements}. \n' \
                               'If the current UI is not related to the task, return {{"Action": "N/A", "Element": ' \
                               '"N/A", "Description": "N/A", "Input Text": "N/A", "Reason": "The current UI is not ' \
                               'related to the task."}}'

        self.__back_prompt = 'Is there an element in the current UI that can be clicked to navigate back and assist ' \
                             'in completing the task "{task}"? \n' \
                             'Respond in JSON format: \n' \
                             '1. "Yes" or "No" - whether such an element exists. \n' \
                             '2. Element Id - provide the ID if "Yes", else "None". \n' \
                             '3. Reason - a brief explanation. \n' \
                             '4. Description - a short description of the action. \n' \
                             'Requirements: \n' \
                             ' - Select a clickable element from the UI hierarchy. \n' \
                             ' - Provide only one element. \n' \
                             'Example: {{"Can": "Yes", "Element": 2, "Reason": "Navigates to the previous screen", ' \
                             '"Description": "Click on the \'Back\' button"}} or {{"Can": "No", "Element": "None", ' \
                             '"Reason": "No back button present", "Description": "None"}}.'

        self.__relation_prompt = 'Given the task "{task}", analyze this UI hierarchy. Exclude elements with ' \
                                 'IDs {except_elements}. ' \
                                 'Determine the relation between the UI and the task. Options: \n' \
                                 '1. Directly related: An element can complete the task directly. \n' \
                                 '2. Indirectly related: No direct element, but an element leads to a related UI. \n' \
                                 '3. Unrelated: This UI does not relate to the task. \n' \
                                 '4. Completed: The task is already completed. \n' \
                                 'Note: Exclude any elements that are "selected" or previously interacted with. ' \
                                 'Avoid repeating previous actions. \n' \
                                 'Provide your answer in JSON format: ' \
                                 '{{"Relation": "<relation>", "Reason": "<reason>"}}. \n' \
                                 'Previous actions: {action_history}\n' \
                                 'Excluded elements: {except_elements}'

    def check_ui_task(self, ui_data, task, prompt, printlog=False):
        """
        Check UI and Task by prompt through foundation model
        """
        try:
            if len(task.conversation_automation) == 0:
                task.conversation_automation = [{'role': 'system', 'content': SYSTEM_PROMPT},
                                                {'role': 'user', 'content': 'This is a view hierarchy of a UI containing'
                                                                            ' various UI blocks and elements:\n'
                                                                            + str(ui_data.element_tree) + '\n'
                                                                            + prompt}]
            else:
                task.conversation_automation.append({'role': 'user', 'content': prompt})
            resp = self.__model_manager.send_fm_conversation(task.conversation_automation, printlog=printlog)
            task.conversation_automation.append(resp)
            return resp
        except Exception as e:

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
        print('* Check UI and Task Relation *')
        # Format base prompt
        except_elements = ','.join(task.except_elements_ids)
        action_history = ';'.join(task.actions)
        prompt = self.__relation_prompt.format(task=task.task_description, except_elements=except_elements,
                                               action_history=action_history)
        # Ask FM
        resp = self.check_ui_task(ui_data=ui_data, task=task, prompt=prompt, printlog=printlog)
        task.res_relation_check = json.loads(resp['content'])
        print(task.res_relation_check)
        return task.res_relation_check

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
        print('* Check UI Action and Target Element *')
        # Format base prompt
        except_elements = ','.join(task.except_elements_ids)
        action_history = ';'.join(task.actions)
        prompt = self.__action_prompt.format(task=task.task_description, except_elements=except_elements,
                                             action_history=action_history)
        # Ask FM
        resp = self.check_ui_task(ui_data=ui_data, task=task, prompt=prompt, printlog=printlog)
        task.res_action_check = json.loads(resp['content'])
        print(task.res_action_check)
        return task.res_action_check

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
        print('* Check Any Action to Go Back to Related UI *')
        # Format base prompt
        except_elements = ','.join(task.except_elements_ids)
        action_history = ';'.join(task.actions)
        prompt = self.__back_prompt.format(task=task.task_description, except_elements=except_elements,
                                           action_history=action_history)
        # Ask FM
        resp = self.check_ui_task(ui_data=ui_data, task=task, prompt=prompt, printlog=printlog)
        task.res_go_back_check = json.loads(resp['content'])
        print(task.res_go_back_check)
        return task.res_go_back_check
