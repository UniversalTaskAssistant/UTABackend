from ._Data import _Data


class User(_Data):
    def __init__(self, user_id: str):
        """
        Initializes a _User instance.
        Args:
            user_id (str): Identifier for the user.
        """
        super().__init__(user_id=user_id)
        self.user_tasks = []  # [task_id, ...]

    def append_user_task(self, user_task):
        """
        Appends a new user task to the user_tasks.
        Args:
            user_task: The user task id to be added.
                       Format:{'original_task': OriginalTask, 'decomposed_task': DecomposedTask}
        """
        self.user_tasks.append(user_task)
