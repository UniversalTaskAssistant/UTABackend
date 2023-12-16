from ModelManagement import ModelManager
import json
from ._Relation import _Relation


class _TaskUIRelationChecker:
    def __init__(self, system_prompt=None, **kwargs):
        """
        Initializes the TaskUIRelationChecker.
        Args:
            system_prompt (str, optional): Custom system prompt for the text model.
            **kwargs: Additional keyword arguments for text model initialization.
        """
        self.__model_manager = ModelManager()
        self.__model_manager.initialize_llm_model("task_ui_relation_checker", system_prompt=system_prompt, **kwargs)

        # Initialize the base prompt template
        self.__base_prompt = 'Given the task "{task}", analyze this UI hierarchy. Exclude elements with ' \
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

    def check_relation(self, step_id, gui, task, except_elements=None, printlog=False):
        """
        Checks the relation between a given GUI and a task.
        Args:
            step_id: id of step.
            gui: GUI object to be analyzed.
            task (str): The task for which the relation is to be checked.
            except_elements (list, optional): List of elements to exclude from consideration.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            _Relation between the GUI and the task.
        """
        try:
            print('--- Check UI and Task Relation ---')
            # Format the prompt
            except_elements_str = ','.join(except_elements) if except_elements else ''
            action_history_str = str(self.__model_manager.get_llm_conversations("task_ui_relation_checker"))
            conversation = self.__base_prompt.format(task=task, except_elements=except_elements_str,
                                                     action_history=action_history_str)

            if gui:
                messages = [
                    {'role': 'user', 'content': 'This is a view hierarchy of a UI containing various UI blocks and '
                                                'elements.'},
                    {'role': 'user', 'content': str(gui.element_tree)}
                ]
                self.__model_manager.set_llm_conversations("task_ui_relation_checker", messages)

            gui_task_relation = self.__model_manager.create_llm_conversation("task_ui_relation_checker", conversation,
                                                                             printlog=printlog)['content']
            gui_task_relation = json.loads(gui_task_relation)

            relation = _Relation(step_id, gui_task_relation['Relation'], gui_task_relation['Reason'])
            print(relation)
            return relation
        except Exception as e:
            raise e

    def reset_ui_relation_checker(self):
        """
        Clear model conversation history records.
        """
        self.__model_manager.reset_llm_conversations("task_ui_relation_checker")