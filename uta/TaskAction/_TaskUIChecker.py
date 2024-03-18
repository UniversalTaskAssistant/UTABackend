from uta.config import *
import json
import re


class _TaskUIChecker:
    def __init__(self, model_manager):
        self.__model_manager = model_manager

        # Initialize the base prompt template
        self.__relation_prompt = 'What is the relation between this UI and the task "{task}" and why?\n' \
                                 '!!!Relation Options:\n'\
                                 '1. Almost Complete: The UI is at the final stage, with only one action left to complete the task. This status applies if the next action directly concludes the task (e.g., finalizing a setting adjustment).\n' \
                                 '2. Directly related: The UI contains elements (clickable, scrollable, swipeable) that are essential for advancing the task, but it isn\'t the task\'s final step.\n' \
                                 '3. Indirectly related: Although the UI doesn\'t have direct elements for the task, it includes elements that lead to the relevant UI or task (e.g., a settings button, search bar).\n' \
                                 '4. Unrelated: The UI is irrelevant to the task or any sub-tasks.\n' \
                                 '!!!Notes:\n' \
                                 '- For Almost Complete, include the element ID for the final action and a brief reason.\n' \
                                 '- For Directly or Indirectly Related, check if the UI contains:\n' \
                                 '-- UI Modal: Overlay windows (e.g., alerts, confirmations).\n' \
                                 '-- User Permission: Permissions request dialogs.\n' \
                                 '-- Login Page: Login requirements.\n' \
                                 '-- Form: Personal data input forms.\n' \
                                 '-- If present, describe the component, provide a reason, and specify the user\'s required action.\n' \
                                 '- For Unrelated scenarios, try to find which element in the current UI can be clicked to navigate back or close the current unrelated UI to proceed the task, suggest "Back" as the action.\n\n' \
                                 'Response Format:\n' \
                                 '1. If Almost Complete, use:\n' \
                                 '{{"Relation": "<relation>", "Element Id": "<ID>", "Reason": "<reason>"}}\n' \
                                 '2. If Directly or Indirectly Related and components are present, use:\n' \
                                 '{{"Relation": "<relation>", "Element Id": "<ID>", "Reason": "<reason>", "Component": "<component>", "Explanation": "<explanation>", "Required action": "<action>"}}\n' \
                                 '3. If Directly or Indirectly Related without specific components, specify the action to proceed (Click, Input, Scroll, Swipe) and, if applicable, the input text:\n' \
                                 '{{"Relation": "<relation>", "Element Id": "<ID>", "Reason": "<reason>", "Action": "<type>", "Input Text": "<text>"}}\n' \
                                 '4. If Unrelated, use:\n' \
                                 '{{"Relation": "<relation>", "Element Id": "<ID or None>", "Reason": "<reason>", "Action": "Back"}}\n\n' \
                                 'Examples:\n' \
                                 '- Indirectly Related with User Permission Component:\n' \
                                 '{{"Relation": "Indirectly related", "Element Id": "2", "Reason": "The UI has a search bar to find \'Turn on voice\'", "Component": "User Permission", "Explanation": "Asks for photo access permission", "Required action": "Allow or deny"}}\n' \
                                 '- Directly Related with Action:\n' \
                                 '{{"Relation": "Directly related", "Element Id": "3", "Reason": "UI has \'Open Settings\' for task settings access", "Action": "Click"}}\n' \
                                 '- Unrelated with Back Action:\n' \
                                 '{{"Relation": "Unrelated", "Element Id": "3", "Reason": "This element enables returning to the last page.", "Action": "Back"}}\n\n' \
                                 '!!!Additional Notes:\n' \
                                 '1. If the UI indicates the task has nearly reached completion (requiring just one final user action), select "Almost Complete".\n' \
                                 '2. Delete all the words in searching bar before start a new search trying.\n' \
                                 '3. Do NOT try to repeat previous actions as they have been tried.\n' \
                                 '4. If the relation is related/almost complete, give the Element Id (int) of the related element\n' \
                                 '5. If Relation is almost complete, you must provide the Element Id (int) required for the final step and describe its operation in the Reason.\n' \
                                 '6. If you decide to input text, the Action should be Input.'

        self.__relation_prompt_gpt4v = 'What is the relation between this UI and the task "{task}" and why?\n' \
                                     '!!!Relation Options:\n'\
                                     '1. Almost Complete: The UI is at the final stage, with only one action left to complete the task. This status applies if the next action directly concludes the task (e.g., finalizing a setting adjustment).\n' \
                                     '2. Directly related: The UI contains elements (clickable, scrollable, swipeable) that are essential for advancing the task, but it isn\'t the task\'s final step.\n' \
                                     '3. Indirectly related: Although the UI doesn\'t have direct elements for the task, it includes elements that lead to the relevant UI or task (e.g., a settings button, search bar).\n' \
                                     '4. Unrelated: The UI is irrelevant to the task or any sub-tasks.\n' \
                                     '!!!Notes:\n' \
                                     '- For Almost Complete, include the Element Id shown in the UI for the final action and a brief reason.\n' \
                                     '- For Directly or Indirectly Related, check if the UI contains:\n' \
                                     '-- UI Modal: Overlay windows (e.g., alerts, confirmations).\n' \
                                     '-- User Permission: Permissions request dialogs.\n' \
                                     '-- Login Page: Login requirements.\n' \
                                     '-- Form: Personal data input forms.\n' \
                                     '-- If present, describe the component, provide a reason, and specify the user\'s required action.\n' \
                                     '- For Unrelated scenarios, try to find which element (by element Id shown in the UI) in the current UI can be clicked to navigate back or close the current unrelated UI to proceed the task, suggest "Back" as the action.\n\n' \
                                     'Response Format:\n' \
                                     '1. If Almost Complete, use:\n' \
                                     '{{"Relation": "<relation>", "Element Id": "<ID>", "Reason": "<reason>"}}\n' \
                                     '2. If Directly or Indirectly Related and components are present, use:\n' \
                                     '{{"Relation": "<relation>", "Element Id": "<ID>", "Reason": "<reason>", "Component": "<component>", "Explanation": "<explanation>", "Required action": "<action>"}}\n' \
                                     '3. If Directly or Indirectly Related without specific components, specify the action to proceed (Click, Input, Scroll, Swipe) and, if applicable, the input text:\n' \
                                     '{{"Relation": "<relation>", "Element Id": "<ID>", "Reason": "<reason>", "Action": "<type>", "Input Text": "<text>"}}\n' \
                                     '4. If Unrelated, use:\n' \
                                     '{{"Relation": "<relation>", "Element Id": "<ID or None>", "Reason": "<reason>", "Action": "Back"}}\n\n' \
                                     'Examples:\n' \
                                     '- Indirectly Related with User Permission Component:\n' \
                                     '{{"Relation": "Indirectly related", "Element Id": "2", "Reason": "The UI has a search bar to find \'Turn on voice\'", "Component": "User Permission", "Explanation": "Asks for photo access permission", "Required action": "Allow or deny"}}\n' \
                                     '- Directly Related with Action:\n' \
                                     '{{"Relation": "Directly related", "Element Id": "3", "Reason": "UI has \'Open Settings\' for task settings access", "Action": "Click"}}\n' \
                                     '- Unrelated with Back Action:\n' \
                                     '{{"Relation": "Unrelated", "Element Id": "3", "Reason": "This element enables returning to the last page.", "Action": "Back"}}\n\n' \
                                     '!!!Additional Notes:\n' \
                                     '1. If the UI indicates the task has nearly reached completion (requiring just one final user action), select "Almost Complete".\n' \
                                     '2. Try to use the most convenient way to finish the task, please make use of the search bar with flexibility.\n' \
                                     '3. If the relation is related/almost complete, you MUST give the Element Id (int, shown in the UI) of the related element\n' \
                                     '4. If Relation is almost complete, you MUST provide the Element Id (int, shown in the UI) required for the final step and describe its operation in the Reason.\n' \
                                     '5. Before the Input action, you need to select Click action to active the keyboard first.\n' \
                                     '6. After keyboard is activated, if you want to input text, the action should be input.\n' \
                                     '7. You MUST give Element Id in your result.'
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
        # if task.step_hint is not None:
        #     prompt += "(Additional step hints to proceed the task:" + str(task.step_hint) + ')\n'
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
        if len(task.relations) > 0:
            prompt += '!!!Action history for this task - MUST NOT REPEAT PREVIOUS ACTIONS:\n ' + str(
                task.relations) + '.\n'
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
                task.full_automation_conversation += [{'role': 'system', 'content': SYSTEM_PROMPT},
                                                      {'role': 'user', 'content': f'This is a view hierarchy of a UI:\n'
                                                      f'{str(ui_data.element_tree)}\n\n{prompt}'}]
            else:
                task.conversation_automation.append({'role': 'user', 'content': prompt})
                task.full_automation_conversation.append({'role': 'user', 'content': prompt})
            resp = self.__model_manager.send_fm_conversation(task.conversation_automation, printlog=printlog)
            task.conversation_automation.append(resp)
            task.full_automation_conversation.append(resp)
            return resp
        except Exception as e:
            print(resp)
            raise e

    def check_ui_task_gpt4v(self, ui_data, task, prompt, printlog=False):
        """
        Check UI and Task by prompt through foundation gpt4v model
        """
        try:
            task.conversation_automation.append({'role': 'user', 'content': prompt})
            task.full_automation_conversation.append({'role': 'user', 'content': prompt})
            resp = self.__model_manager.send_gpt4_vision_img_paths(prompt=prompt, img_paths=[ui_data.annotated_elements_screenshot_path], printlog=printlog)
            resp = {'role': 'assistant', 'content': resp[1]}
            task.conversation_automation.append(resp)
            task.full_automation_conversation.append(resp)
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
            prompt += self.wrap_task_history(task)
            prompt += self.__relation_prompt.format(task=task.selected_task)
            # Ask FM
            resp = self.check_ui_task(ui_data=ui_data, task=task, prompt=prompt, printlog=printlog)
            task.res_relation_check = self.transfer_to_dict(resp)
            print(task.res_relation_check)
            return task.res_relation_check
        except Exception as e:
            print(resp)
            raise e

    def check_ui_relation_gpt4v(self, ui_data, task, printlog=False):
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
            prompt += self.wrap_task_history(task)
            prompt += self.__relation_prompt_gpt4v.format(task=task.selected_task, keyboard_active=task.keyboard_active)
            # Ask FM
            resp = self.check_ui_task_gpt4v(ui_data=ui_data, task=task, prompt=prompt, printlog=printlog)
            task.res_relation_check = self.transfer_to_dict(resp)
            print(task.res_relation_check)
            return task.res_relation_check
        except Exception as e:
            print(resp)
            raise e