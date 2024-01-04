from ._Data import _Data

class Task:
    def __init__(self, task_id, task_description, parent_task_id=None):
        self.task_id = task_id
        self.task_description = task_description
        self.task_type = None

        self.parent_task_id = parent_task_id
        self.children_ids = []

        self.steps = []
        self.conversation_declaration = None
        self.conversation_automation = None
        self.task_execution_result = None


class Task(_Data):
    def __init__(self, task_id: str, parent_id="None", original_task="None", atomic_tasks=None,
                 clarifying_conversations=None, atomic_task="None", steps=None, task_type="None",
                 execution_result="None"):
        """
        Initializes a Task instance, which is a more specific type of _Data.

        Args:
            **Rest attributes are used for original task
            task_id (str): Unique identifier for the task.
            parent_id (str, optional): Identifier of the parent task. Defaults to "None".
            original_task (str, optional): Description or details of the original task. Defaults to "None".
            atomic_tasks (list, optional): List of identifiers for atomic tasks related to this task. Defaults to empty
            list.
            clarifying_conversations (list, optional): List of conversations that occurred during task clarification.
            Defaults to empty list.

            **Rest attributes are used for atomic task
            atomic_task (str, optional): Identifier for an atomic task. Defaults to "None".
            steps (list, optional): List of step identifiers associated with this task. Defaults to empty list.
            task_type (str, optional): Type of the task, can be either General Inquiry or System Function or
            App-Related Task. Defaults to "None".
            execution_result (str, optional): The result of executing the task. Defaults to "None".

        Notes:
            - Initializes 'steps', 'atomic_tasks', and 'clarifying_conversations' as empty lists if not provided.
            - Inherits properties from the _Data class using super().
        """
        if atomic_tasks is None:
            atomic_tasks = []  # [task_id, ...]
        if clarifying_conversations is None:
            clarifying_conversations = []
        if steps is None:
            steps = []  # [step_id, ...]

        super().__init__(task_id=task_id, parent_id=parent_id, original_task=original_task, atomic_task=atomic_task,
                         task_type=task_type, execution_result=execution_result)
        self.steps = steps
        self.atomic_tasks = atomic_tasks
        self.clarifying_conversations = clarifying_conversations

    def append_step(self, step):
        """
        Appends a new step to the task.
        Args:
            step: The step_id to be added.
        """
        self.steps.append(step)

    def append_autonomic_task(self, atomic_task):
        """
        Appends a new atomic task to the task.
        Args:
            atomic_task: The atomic task id to be added.
        """
        self.atomic_tasks.append(atomic_task)

    def append_clarifying_conversation(self, conversation):
        """
        Appends a new clarifying conversation to the task.
        Args:
            conversation: The conversation to be added.
        """
        self.clarifying_conversations.append(conversation)
