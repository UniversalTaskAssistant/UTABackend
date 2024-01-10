from ._Data import _Data
from uta.config import SYSTEM_PROMPT


class Task(_Data):
    def __init__(self, task_id, user_id, parent_task_id=None, task_description=None):
        """
        Initializes a Task instance.
        Args:
            task_id (str): Unique identifier for the task.
            user_id (str): User id associated with the task.
            parent_task_id (str): Identifier of the parent task.
            task_description (str): Description or details of the task.
        """
        super().__init__()
        self.task_id = task_id
        self.user_id = user_id
        self.parent_task_id = parent_task_id
        self.task_description = task_description
        self.task_type = None   # Type of the task, can be either Original Task, General Inquiry, system Function, or App-Related Task.
        self.children_ids = []  # List of identifiers of the sub-tasks or steps.

        # Only used when task declaration
        self.conversation_clarification = [{"role": "system", "content": SYSTEM_PROMPT}]    # List of conversations
        # that occurred during multiple turns of task clarification.
        self.res_clarification = dict()     # Final json result of task clarification.
        self.res_decomposition = dict()     # Final json result of task decomposition.
        self.res_classification = dict()    # Final json result of task classification.

        # Only used when task automation
        self.conversation_automation = [{"role": "system", "content": SYSTEM_PROMPT}]       # List of conversations
        # that occurred during multiple turns of task automation.
        self.steps = []                     # List of step objects associated with this task.
        self.task_execution_result = None   # The result of executing the task.
