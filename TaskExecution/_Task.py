

class _Task:
    def __init__(self, task_id: int, task: str):
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
        return f"_Action(task_id={self.task_id}, task={self.task}, " \
            f"steps={self.steps}, execution_result={self.execution_result})"

    def set_attributes(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"No attribute {key} defined in {self.__class__.__name__}.")

    def append(self, step):
        self.steps.append(step)

    def set_step(self, step_id, step):
        if len(self.steps) == step_id - 1:
            self.steps.append(step)
        elif len(self.steps) > step_id - 1:
            self.steps[step_id - 1] = step
        else:
            raise IndexError(f"step_id - 1 {step_id - 1} exceeds the current length {len(self.steps)} of stored steps.")

    def get_step(self, step_id):
        if len(self.steps) > step_id - 1:
            return self.steps[step_id - 1]
        else:
            raise IndexError(f"step_id - 1 {step_id - 1} exceeds max index {len(self.steps) - 1} of stored steps.")