

class User:
    def __init__(self, user_id: int):
        """
        Initializes a _User instance.
        Args:
            user_id (int): Identifier for the user.
        """
        self.user_id = user_id
        self.user_tasks = []  # [{'original_task': OriginalTask, 'decomposed_task': DecomposedTask}, ...]

    def __dict__(self):
        return {
            'user_id': self.user_id,
            'user_tasks': self.user_tasks,
        }

    def __str__(self):
        return f"_User(task_id={self.user_id}, user_tasks={self.user_tasks})"

    def append_user_task(self, user_task):
        """
        Appends a new user task to the user_tasks.
        Args:
            user_task: The user task to be added.
                       Format:{'original_task': OriginalTask, 'decomposed_task': DecomposedTask}
        """
        self.user_tasks.append(user_task)