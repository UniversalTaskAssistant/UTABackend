from ._Data import _Data


class Task(_Data):
    def __init__(self, task_id: str, parent_id="None", original_task="None", clarified_task="None",
                 atomic_tasks=None, clarifying_conversations=None, atomic_task="None", steps=None, task_type="None",
                 execution_result="None"):
        if atomic_tasks is None:
            atomic_tasks = []  # [task_id, ...]
        if clarifying_conversations is None:
            clarifying_conversations = []
        if steps is None:
            steps = []  # [step_id, ...]

        super().__init__(task_id=task_id, parent_id=parent_id, original_task=original_task,
                         clarified_task=clarified_task, atomic_task=atomic_task, task_type=task_type,
                         execution_result=execution_result)
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
