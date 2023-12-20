

class Task:
    def __init__(self, task_id: int, task: str):
        """
        Initializes a Task instance.
        Args:
            task_id (int): Identifier for the task.
            task (str): Description of the task.
        """
        self.task_id: int = task_id
        self.task: str = task
        self.steps: list = []
        self.execution_result: str = "None"

    def __dict__(self):
        return {
            'task_id': self.task_id,
            'task': self.task,
            'steps': self.steps,
            'execution_result': self.execution_result
        }

    def __str__(self):
        return f"Task(task_id={self.task_id}, task={self.task}, " \
            f"steps={self.steps}, execution_result={self.execution_result})"

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

    def append(self, step):
        """
        Appends a new step to the task.
        Args:
            step: The step to be added.
        """
        self.steps.append(step)

    def set_step(self, step_id, step):
        """
        Sets or replaces a step at a specific position.
        Args:
            step_id (int): The position to insert or replace the step.
            step: The step to be set.
        Raises:
            IndexError: If step_id is out of the range of current steps.
        """
        if len(self.steps) == step_id - 1:
            self.steps.append(step)
        elif len(self.steps) > step_id - 1:
            self.steps[step_id - 1] = step
        else:
            raise IndexError(f"step_id - 1 {step_id - 1} exceeds the current length {len(self.steps)} of stored steps.")

    def get_step(self, step_id):
        """
        Retrieves a step based on its position.
        Args:
            step_id (int): The position of the step to retrieve.
        Returns:
            The requested step.
        Raises:
            IndexError: If step_id is out of the range of current steps.
        """
        if len(self.steps) > step_id - 1:
            return self.steps[step_id - 1]
        else:
            raise IndexError(f"step_id - 1 {step_id - 1} exceeds max index {len(self.steps) - 1} of stored steps.")