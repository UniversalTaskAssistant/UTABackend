
class AutonomicTask:
    def __init__(self, task_id: str, **kwargs):
        """
        Initializes a AutonomicTask instance.
        Args:
            task_id (str): Identifier for the task.
        """
        self.task_id: str = task_id
        self.parent_id: str = kwargs["parent_id"] if kwargs.get("parent_id") else "None"
        self.task: str = kwargs["task"] if kwargs.get("task") else "None"
        self.steps: list = kwargs["steps"] if kwargs.get("steps") else []
        self.task_type: str = kwargs["task_type"] if kwargs.get("task_type") else "None"
        self.execution_result: str = kwargs["execution_result"] if kwargs.get("execution_result") else "None"

    def __dict__(self):
        return {
            'task_id': self.task_id,
            'parent_id': self.parent_id,
            'task': self.task,
            'steps': self.steps,
            'task_type': self.task_type,
            'execution_result': self.execution_result
        }

    def __str__(self):
        return f"Task(task_id={self.task_id}, parent_id={self.parent_id}, task={self.task}, " \
            f"steps={self.steps}, task_type={self.task_type}, execution_result={self.execution_result})"

    def set_attributes(self, **kwargs):
        """
        Dynamically sets attributes based on provided keyword arguments.
        Args:
            **kwargs: Key-value pairs to set as attributes.
        Raises:
            AttributeError: If a given attribute is not defined in the class.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"No attribute {key} defined in {self.__class__.__name__}.")

    def append_step(self, step):
        """
        Appends a new step to the task.
        Args:
            step: The step to be added.
        """
        self.steps.append(step)


class OriginalTask:
    def __init__(self, task_id: str, **kwargs):
        """
        Initializes a OriginalTask instance.
        Args:
            task_id (str): Identifier for the task.
        """
        self.task_id: str = task_id
        self.parent_id: str = kwargs["parent_id"] if kwargs.get("parent_id") else "None"
        self.original_task: str = kwargs["original_task"] if kwargs.get("original_task") else "None"
        self.clarifyed_task: str = kwargs["clarifyed_task"] if kwargs.get("clarifyed_task") else "None"
        self.autonomic_tasks: list = kwargs["autonomic_tasks"] if kwargs.get("autonomic_tasks") else []
        self.clarifying_conversations: list = kwargs["clarifying_conversations"] if \
            kwargs.get("clarifying_conversations") else []
        # [({'role': 'user', 'content': conversation}, {'role': 'assistant', 'content': conversation}), ...}

    def __dict__(self):
        return {
            'task_id': self.task_id,
            'parent_id': self.parent_id,
            'original_task': self.original_task,
            'clarifyed_task': self.clarifyed_task,
            'autonomic_tasks': self.autonomic_tasks,
            'clarifying_conversations': self.clarifying_conversations,
        }

    def __str__(self):
        return f"Task(task_id={self.task_id}, parent_id={self.parent_id}, original_task={self.original_task}, " \
            f"clarifyed_task={self.clarifyed_task}, " \
            f"autonomic_tasks={self.autonomic_tasks}, clarifying_conversations={self.clarifying_conversations})"

    def set_attributes(self, **kwargs):
        """
        Dynamically sets attributes based on provided keyword arguments.
        Args:
            **kwargs: Key-value pairs to set as attributes.
        Raises:
            AttributeError: If a given attribute is not defined in the class.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"No attribute {key} defined in {self.__class__.__name__}.")

    def append_autonomic_task(self, autonomic_task):
        """
        Appends a new autonomic task to the task.
        Args:
            autonomic_task: The autonomic task to be added.
        """
        self.autonomic_tasks.append(autonomic_task)

    def append_clarifying_conversation(self, conversation):
        """
        Appends a new clarifying conversation to the task.
        Args:
            conversation: The conversation to be added.
        """
        self.clarifying_conversations.append(conversation)
