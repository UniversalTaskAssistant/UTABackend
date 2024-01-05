from DataStructures.config import *


class Task:
    def __init__(self, task_id, task_description, parent_task_id=None):
        self.task_id = task_id
        self.task_description = task_description
        self.task_type = None

        self.parent_task_id = parent_task_id
        self.children_ids = []

        # task declaration
        self.res_clarification = None
        self.res_decomposition = None
        self.res_classification = None
        self.conversation_declaration = [{'role': 'system', 'content':SYSTEM_PROMPT}]
        self.conversation_automation = [{'role': 'system', 'content':SYSTEM_PROMPT}]

        # task automation
        self.steps = []
        self.task_execution_result = None

    def add_message_to_declaration_conversation(self, message):
        """
        Appends a new clarifying conversation to the task.
        Args:
            message (str): The message to be added.
        """
        self.conversation_declaration.append({'role':'user', 'content':message})

    def append_step(self, step):
        """
        Appends a new step to the task.
        Args:
            step: The step_id to be added.
        """
        self.steps.append(step)

