from DataStructures.config import *


class Task:
    def __init__(self, task_id, task_description, parent_task_id=None):
        self.task_id = task_id
        self.task_description = task_description
        self.task_type = None

        self.parent_task_id = parent_task_id
        self.children_ids = []

        # task declaration
        self.conversation_clarification = [{'role': 'system', 'content':SYSTEM_PROMPT}]   # for multi conversations of clarification
        self.res_clarification = None
        self.res_decomposition = None
        self.res_classification = None

        # task automation
        self.conversation_automation = [{'role': 'system', 'content':SYSTEM_PROMPT}]      # fpr multi conversations of automation
        self.steps = []
        self.task_execution_result = None

