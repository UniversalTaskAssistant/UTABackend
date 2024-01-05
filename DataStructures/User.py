from ._Data import _Data


class User(_Data):
    def __init__(self, user_id: str):
        """
        Initializes a _User instance.
        Args:
            user_id (str): Identifier for the user.
        """
        super().__init__()
        self.user_id = user_id
