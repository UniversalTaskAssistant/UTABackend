

class _AutoModeStep:
    def __init__(self, step_id: int, **kwargs):
        """
        Initializes an AutoModeStep instance.
        Args:
            step_id (int): Identifier for the step.
            **kwargs: Additional keyword arguments. Supported keywords:
                       - is_go_back (bool): Indicates if the step involves a 'go back' action.
                       - recommend_action (str): Recommended action for this step.
                       - relation (str): Relation of this step to the task.
                       - ui_data: UI data associated with this step.
        """
        self.step_id: int = step_id
        self.is_go_back: bool = kwargs["is_go_back"] if kwargs.get("is_go_back") else False
        self.recommend_action = kwargs["recommend_action"] if kwargs.get("recommend_action") else "None"
        self.relation = kwargs["relation"] if kwargs.get("relation") else "None"
        self.ui_data = kwargs["ui_data"] if kwargs.get("ui_data") else "None"

    def __dict__(self):
        return {
            'step_id': self.step_id,
            'is_go_back': self.is_go_back,
            'recommend_action': self.recommend_action,
            'relation': self.relation,
            'ui_data': self.ui_data,
        }

    def __str__(self):
        return f"_Action(step_id={self.step_id}, is_go_back={self.is_go_back}, " \
            f"recommend_action={self.recommend_action}, relation={self.relation}, ui_data={self.ui_data})"

    def set_attributes(self, **kwargs):
        """
        Dynamically sets attributes based on provided keyword arguments.
        Args:
            **kwargs: Key-value pairs to set as attributes of the instance.
        Raises:
            AttributeError: If a given attribute is not defined in the class.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"No attribute {key} defined in {self.__class__.__name__}.")