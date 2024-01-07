import json
from DataStructures import Action, InquiryStep, AutoModeStep, Relation, SYSTEM_PROMPT


class TaskExecutor:
    def __init__(self, model_manager):
        """
        Initialize TaskExecutor object.
        """
        self.__model_manager = model_manager

        # Initialize the base prompt template
        self.__action_prompt = 'Determine the appropriate action for completing the task "{task}" ' \
                               'using the current UI. \n' \
                               'Consider the following action types: Click, Scroll Up, Scroll Down, ' \
                               'Swipe Right, Swipe Left, Long Press, Input. \n' \
                               'Note: Use "Input" only if the keyboard is active; activate the keyboard by clicking' \
                               ' a relevant element if necessary. Ensure the chosen element supports the ' \
                               'intended action. \n' \
                               'Provide a single, most effective action. Avoid repeating actions listed in ' \
                               '{action_history}. \n' \
                               'Exclude elements with IDs {except_elements} as they are unrelated to the task. \n' \
                               'Respond in JSON format: {{"Action": "<type>", "Element": <id>, "Description": ' \
                               '"<desc>", "Input Text": "<text>", "Reason": "<why>"}}. \n' \
                               'Example: {{"Action": "Click", "Element": 3, "Description": "Open Settings", ' \
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

    @staticmethod
    def load_auto_mode_step(ui_data, task):
        """
        Initialize new AutoModeStep.
        Args:
            ui_data (UI_Data): Current ui object.
            task (Task): Parental task object.
        Returns:
            AutoModeStep.
        """
        return AutoModeStep(step_id=str(len(task.steps)), parent_id=task.task_id, ui_data=ui_data)

    def check_go_back_availability(self, step, task, printlog=False):
        """
        Checks if there is an element in the UI that can be clicked to navigate back in relation to a given task.
        Args:
           step (AutoModeStep): AutoModeStep object containing current ui object.
           task (Task): Task object containing task description for which back navigation is being checked.
           printlog (bool): If True, enables logging of outputs.
        Returns:
           Action indicating back navigation availability.
        """
        try:
            print('--- Check Any Action to Go Back to Related UI ---')
            conversations = [{'role': 'system', 'content': SYSTEM_PROMPT}]

            ui = step.ui_data
            if ui:
                messages = [
                    {'role': 'user', 'content': 'This is a view hierarchy of a UI containing various '
                                                'UI blocks and elements.'},
                    {'role': 'user', 'content': str(ui.element_tree)}
                ]
                conversations += messages

            new_conversation = self.__back_prompt.format(task=task.task_description)
            conversations.append({'role': 'user', 'content': new_conversation})

            go_back_availability = self.__model_manager.send_fm_conversation(conversations,
                                                                             printlog=printlog)['content']
            conversations.append(go_back_availability)
            task.conversation_automation.append(conversations)

            go_back_availability = json.loads(go_back_availability)
            print(go_back_availability)

            if go_back_availability['Can'].lower() == 'yes':
                recommended_action = Action("Click", go_back_availability["Element"],
                                            go_back_availability["Description"], "None", go_back_availability["Reason"])
            else:
                recommended_action = Action("Find Relevant Apps", go_back_availability["Element"],
                                            go_back_availability["Description"], "None", go_back_availability["Reason"])
            step.recommended_action = recommended_action
            step.is_go_back = True
            return recommended_action
        except Exception as e:
            raise e

    def check_action(self, step, task, except_elements=None, printlog=False):
        """
        Determines the appropriate action and target element in the UI for a given task.
        Args:
            step (AutoModeStep): AutoModeStep object containing current ui object.
            task (Task): Task object containing task description for which back navigation is being checked.
            except_elements (list, optional): Elements to be excluded from consideration.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Action with the determined action and target element.
        """
        try:
            print('--- Check UI Action and Target Element ---')
            conversations = [{'role': 'system', 'content': SYSTEM_PROMPT}]

            ui = step.ui_data
            if ui:
                messages = [
                    {'role': 'user', 'content': 'This is a view hierarchy of a UI containing various UI '
                                                'blocks and elements.'},
                    {'role': 'user', 'content': str(ui.element_tree)}
                ]
                conversations += messages

            # Format the prompt
            except_elements_str = ','.join(except_elements) if except_elements else ''
            action_history_list = [one_conv for step_index, one_step in enumerate(task.steps) if
                                   isinstance(one_step, AutoModeStep) for one_conv in
                                   task.conversation_automation[step_index][1:]]  # remove the system prompt
            action_history_str = str(action_history_list)
            new_conversation = self.__action_prompt.format(task=task.task_description,
                                                           except_elements=except_elements_str,
                                                           action_history=action_history_str)
            conversations.append({'role': 'user', 'content': new_conversation})

            ui_task_action = self.__model_manager.send_fm_conversation(conversations, printlog=printlog)['content']
            conversations.append(ui_task_action)
            task.conversation_automation.append(conversations)

            ui_task_action = json.loads(ui_task_action)

            try:
                ui_task_action['Element'] = int(ui_task_action['Element'])
            except ValueError:
                print('No valid action on the UI for the task')
                ui_task_action['Element'] = -1

            action = Action(ui_task_action["Action"], ui_task_action["Element"],
                            ui_task_action["Description"], ui_task_action["Input Text"],
                            ui_task_action["Reason"])
            print(action)

            step.recommended_action = action
            return action
        except Exception as e:
            raise e

    def check_relation(self, step, task, except_elements=None, printlog=False):
        """
        Checks the relation between a given ui and a task.
        Args:
            step (AutoModeStep): AutoModeStep object containing current ui object.
            task (Task): Task object containing task description for which back navigation is being checked.
            except_elements (list, optional): List of elements to exclude from consideration.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Relation between the ui and the task.
        """
        try:
            print('--- Check UI and Task Relation ---')
            conversations = [{'role': 'system', 'content': SYSTEM_PROMPT}]

            ui = step.ui_data
            if ui:
                messages = [
                    {'role': 'user', 'content': 'This is a view hierarchy of a UI containing various UI blocks and '
                                                'elements.'},
                    {'role': 'user', 'content': str(ui.element_tree)}
                ]
                conversations += messages

            # Format the prompt
            except_elements_str = ','.join(except_elements) if except_elements else ''
            action_history_list = [one_conv for step_index, one_step in enumerate(task.steps) if
                                   isinstance(one_step, AutoModeStep) for one_conv in
                                   task.conversation_automation[step_index][1:]]  # remove the system prompt
            action_history_str = str(action_history_list)
            new_conversation = self.__relation_prompt.format(task=task.task_description,
                                                             except_elements=except_elements_str,
                                                             action_history=action_history_str)
            conversations.append({'role': 'user', 'content': new_conversation})

            ui_task_relation = self.__model_manager.send_fm_conversation(conversations, printlog=printlog)['content']
            conversations.append(ui_task_relation)
            task.conversation_automation.append(conversations)

            ui_task_relation = json.loads(ui_task_relation)
            relation = Relation(ui_task_relation['Relation'], ui_task_relation['Reason'])
            print(relation)

            step.relation = relation
            return relation
        except Exception as e:
            raise e

    def execute_inquiry_task(self, step, task, user_message, printlog=False):
        """
        Execute inquiry type task.
        Args:
            step (InquiryStep): InquiryStep object.
            task (Task): Task object containing historical inquiry steps.
            user_message (str): User's question.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            LLM's response.
        """
        try:
            step.user_conversation = {'role': 'user', 'content': user_message}
            inquiry_history_list = [one_conv for step_index, one_step in enumerate(task.steps) if
                                    isinstance(one_step, InquiryStep) for one_conv in
                                    task.conversation_automation[step_index]]
            inquiry_history_list.append(step.user_conversation)

            resp = self.__model_manager.send_fm_conversation(inquiry_history_list, printlog=printlog)
            step.llm_conversation = resp
            task.conversation_automation.append([step.user_conversation, step.llm_conversation])
            return json.loads(resp)
        except Exception as e:
            print('error:', e)
            raise e
