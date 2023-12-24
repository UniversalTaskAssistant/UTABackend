

class DecomposedTask:
    def __init__(self, task_id: int):
        """
        Initializes a DecomposedTask instance.
        Args:
            task_id (int): Identifier for the task.
        """
        self.task_id: int = task_id
        self.task: str = "None"
        self.steps: list = []
        self.task_type: str = "None"
        self.execution_result: str = "None"

    def __dict__(self):
        return {
            'task_id': self.task_id,
            'task': self.task,
            'steps': self.steps,
            'task_type': self.task_type,
            'execution_result': self.execution_result
        }

    def __str__(self):
        return f"Task(task_id={self.task_id}, task={self.task}, " \
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
    def __init__(self, task_id: int):
        """
        Initializes a OriginalTask instance.
        Args:
            task_id (int): Identifier for the task.
        """
        self.task_id: int = task_id
        self.task: str = "None"
        self.decomposed_tasks: list = []
        self.clarifying_conversations: list = []

    def __dict__(self):
        return {
            'task_id': self.task_id,
            'task': self.task,
            'decomposed_tasks': self.decomposed_tasks,
            'clarifying_conversations': self.clarifying_conversations,
        }

    def __str__(self):
        return f"Task(task_id={self.task_id}, task={self.task}, " \
            f"decomposed_tasks={self.decomposed_tasks}, clarifying_conversations={self.clarifying_conversations})"

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

    def append_decomposed_task(self, decomposed_task):
        """
        Appends a new decomposed task to the task.
        Args:
            decomposed_task: The decomposed task to be added.
        """
        self.decomposed_tasks.append(decomposed_task)

