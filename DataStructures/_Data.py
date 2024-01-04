class _Data:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        """
        String format of str()
        """
        return f"{self.__class__.__name__}(" + ", ".join([f"{key}={value}" for key, value in self.__dict__.items()]) \
               + ")"

    def to_dict(self):
        """
        Returns a dictionary representation of the AutonomicTask instance.
        """
        return {k: v for k, v in self.__dict__.items()}

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