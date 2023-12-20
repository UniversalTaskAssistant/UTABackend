

class AutoModeStep:
    def __init__(self, step_id: int, **kwargs):
        """
        Initializes an AutoModeStep instance.
        Args:
            step_id (int): Identifier for the step.
            **kwargs: Additional keyword arguments. Supported keywords:
                       - is_go_back (bool): Indicates if the step involves a 'go back' action.
                       - recommended_action (str): Recommended action for this step.
                       - relation (str): Relation of this step to the task.
                       - ui_data: UI data associated with this step.
        """
        self.step_id: int = step_id
        self.is_go_back: bool = kwargs["is_go_back"] if kwargs.get("is_go_back") else False
        self.recommended_action = kwargs["recommended_action"] if kwargs.get("recommended_action") else "None"
        self.relation = kwargs["relation"] if kwargs.get("relation") else "None"
        self.ui_data = kwargs["ui_data"] if kwargs.get("ui_data") else "None"
        self.execution_result: str = "None"

    def __dict__(self):
        return {
            'step_id': self.step_id,
            'is_go_back': self.is_go_back,
            'recommended_action': self.recommended_action,
            'relation': self.relation,
            'ui_data': self.ui_data,
            'execution_result': self.execution_result,
        }

    def __str__(self):
        return f"AutoModeStep(step_id={self.step_id}, is_go_back={self.is_go_back}, " \
            f"recommended_action={self.recommended_action}, relation={self.relation}, ui_data={self.ui_data}" \
            f"execution_result={self.execution_result})"

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

    def annotate_ui_openation(self):
        assert self.ui_data != "None" and self.recommended_action != "None"
        self.ui_data.annotate_ui_openation(self.recommended_action)


class _ConversationStep:
    """
    Initializes an ConversationStep instance.
    Args:
        step_id (int): Identifier for the step.
        **kwargs: Additional keyword arguments. Supported keywords:
                   - conversation (str): conversation content for this step.
    """
    def __init__(self, step_id: int, **kwargs):
        self.step_id: int = step_id
        self.conversation: dict = kwargs["conversation"] if kwargs.get("conversation") else None

    def __dict__(self):
        return {
            'step_id': self.step_id,
            'conversation': self.conversation,
        }

    def __str__(self):
        return f"_ConversationStep(step_id={self.step_id}, conversation={self.conversation})"

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