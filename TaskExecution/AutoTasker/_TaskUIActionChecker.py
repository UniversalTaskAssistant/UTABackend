from ModelManagement import ModelManager
import json
from DataStructures import _Action


class _TaskUIActionChecker:
    def __init__(self, system_prompt=None, **kwargs):
        """
        Initializes the TaskUIActionChecker.
        Args:
            system_prompt (str, optional): Custom system prompt for the text model.
            **kwargs: Additional keyword arguments for text model initialization.
        """
        self.__model_manager = ModelManager()
        self.__model_manager.initialize_llm_model("task_ui_action_checker", system_prompt=system_prompt, **kwargs)

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
                               '"Reason": "Access task settings"}}. \n' \
                               'Previous actions: {action_history}, Excluded elements: {except_elements}.'

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

    def check_go_back_availability(self, ui, task, reset_history=False, printlog=False):
        """
        Checks if there is an element in the UI that can be clicked to navigate back in relation to a given task.
        Args:
           ui: The current ui object.
           task (str): The task for which back navigation is being checked.
           reset_history (bool): If True, resets the conversation history in the model manager.
           printlog (bool): If True, enables logging of outputs.
        Returns:
           _Action indicating back navigation availability.
        """
        try:
            print('--- Check Any Action to Go Back to Related UI ---')
            if reset_history:
                self.__model_manager.reset_llm_conversations("task_ui_action_checker")

            conversation = self.__back_prompt.format(task=task)

            if ui:
                messages = [
                    {'role': 'user', 'content': 'This is a view hierarchy of a UI containing various UI blocks and elements.'},
                    {'role': 'user', 'content': str(ui.element_tree)}
                ]
                self.__model_manager.set_llm_conversations("task_ui_action_checker", messages)

            go_back_availability = self.__model_manager.create_llm_conversation("task_ui_action_checker", conversation, printlog=printlog)['content']
            go_back_availability = json.loads(go_back_availability)
            print(go_back_availability)

            if go_back_availability['Can'].lower() == 'yes':
                return _Action("Click", go_back_availability["Element"], go_back_availability["Description"], "None", go_back_availability["Reason"])
            else:
                return _Action("Find Relevant Apps", go_back_availability["Element"], go_back_availability["Description"], "None", go_back_availability["Reason"])
        except Exception as e:
            raise e

    def check_action(self, ui, task, except_elements=None, printlog=False):
        """
        Determines the appropriate action and target element in the UI for a given task.
        Args:
            ui: The current ui object.
            task (str): The task to be completed using the UI.
            except_elements (list, optional): Elements to be excluded from consideration.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            _Action with the determined action and target element.
        """
        try:
            print('--- Check UI Action and Target Element ---')
            # Format the prompt
            except_elements_str = ','.join(except_elements) if except_elements else ''
            action_history_str = str(self.__model_manager.get_llm_conversations("task_ui_action_checker"))
            conversation = self.__action_prompt.format(task=task, except_elements=except_elements_str, action_history=action_history_str)

            if ui:
                messages = [
                    {'role': 'user', 'content': 'This is a view hierarchy of a UI containing various UI blocks and elements.'},
                    {'role': 'user', 'content': str(ui.element_tree)}
                ]
                self.__model_manager.set_llm_conversations("task_ui_action_checker", messages)

            ui_task_action = self.__model_manager.create_llm_conversation("task_ui_action_checker", conversation, printlog=printlog)['content']
            ui_task_action = json.loads(ui_task_action)
            ui_task_action['Element'] = int(ui_task_action['Element'])

            if ui_task_action.get("Input Text") is None:
                action = _Action(ui_task_action["Action"], ui_task_action["Element"],
                                 ui_task_action["Description"], "None", ui_task_action["Reason"])
            else:
                action = _Action(ui_task_action["Action"], ui_task_action["Element"],
                                 ui_task_action["Description"], ui_task_action["Input Text"],
                                 ui_task_action["Reason"])
            print(action)
            return action
        except Exception as e:
            raise e

    def reset_ui_action_checker(self):
        """
        Clear model conversation history records.
        """
        self.__model_manager.reset_llm_conversations("task_ui_action_checker")
