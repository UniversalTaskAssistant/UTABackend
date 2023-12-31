import json
from DataStructures import Relation


class _TaskUIRelationChecker:
    def __init__(self, model_identifier, model_manager):
        """
        Initializes the TaskUIRelationChecker.
        Args:
            model_identifier Name of the text model.
            model_manager: Initialised ModelManager used by this class.
        """
        self.__model_identifier = model_identifier
        self.__model_manager = model_manager

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

    def initialize_agent(self):
        """
            Initialize llm model in model manager.
        """
        if self.is_agent_initialized():
            self.delete_agent()
        self.__model_manager.initialize_llm_model(identifier=self.__model_identifier)

    def is_agent_initialized(self):
        """
        Check whether agent is initialized.
        """
        return self.__model_manager.is_llm_model_initialized(identifier=self.__model_identifier)

    def delete_agent(self):
        """
        Remove llm model in model manager.
        """
        self.__model_manager.delete_llm_model(identifier=self.__model_identifier)

    def check_relation(self, ui, task, except_elements=None, printlog=False):
        """
        Checks the relation between a given ui and a task.
        Args:
            ui: ui object to be analyzed.
            task (str): The task for which the relation is to be checked.
            except_elements (list, optional): List of elements to exclude from consideration.
            printlog (bool): If True, enables logging of outputs.
        Returns:
            Relation between the ui and the task.
        """
        try:
            print('--- Check UI and Task Relation ---')
            # Format the prompt
            except_elements_str = ','.join(except_elements) if except_elements else ''
            action_history_str = str(self.__model_manager.get_llm_conversations(self.__model_identifier))
            conversation = self.__base_prompt.format(task=task, except_elements=except_elements_str,
                                                     action_history=action_history_str)

            if ui:
                messages = [
                    {'role': 'user', 'content': 'This is a view hierarchy of a UI containing various UI blocks and '
                                                'elements.'},
                    {'role': 'user', 'content': str(ui.element_tree)}
                ]
                self.__model_manager.set_llm_conversations(self.__model_identifier, messages)

            ui_task_relation = self.__model_manager.create_llm_conversation(self.__model_identifier, conversation, printlog=printlog)['content']
            ui_task_relation = json.loads(ui_task_relation)

            relation = Relation(ui_task_relation['Relation'], ui_task_relation['Reason'])
            print(relation)
            return relation
        except Exception as e:
            raise e

    def reset_ui_relation_checker(self):
        """
        Clear model conversation history records.
        """
        self.__model_manager.reset_llm_conversations(self.__model_identifier)