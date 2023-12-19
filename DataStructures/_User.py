

class _User:
    def __init__(self, user_id: int):
        """
        Initializes a _User instance.
        Args:
            user_id (int): Identifier for the user.
        """
        self.user_id = user_id
        self.user_tasks = dict()

    def __dict__(self):
        return {
            'user_id': self.user_id,
            'user_tasks': self.user_tasks,
        }

    def __str__(self):
        return f"_User(task_id={self.user_id}, user_tasks={self.user_tasks})"