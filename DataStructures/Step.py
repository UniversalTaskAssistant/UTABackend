from ._Data import _Data


class AutoModeStep(_Data):
    def __init__(self, step_id: str, parent_id=None, ui_data=None):
        """
        Initializes an AutoModeStep instance.
        Args:
            step_id (str): Identifier for the step.
            parent_id (str): Identifier for the parental autonomic task.
            ui_data (UI_Data): UI data associated with this step.
        """
        super().__init__()
        self.step_id = step_id
        self.parent_id = parent_id
        self.ui_data = ui_data
        self.is_go_back = False  # Indicates if the step involves a 'go back' action.
        self.relation = None  # Recommended action for this step.
        self.recommended_action = None  # Recommended action for this step.
        self.related_app_check_result = None  # If UI is unrelated, then need to check related apps, record result here
        self.app_recommendation_result = None  # Recommended app result.

    def annotate_ui_operation(self):
        """
        Store annotated UI for debugging
        """
        assert self.ui_data is not None and self.recommended_action is not None
        self.ui_data.annotate_ui_operation(self.recommended_action)


class InquiryStep(_Data):
    def __init__(self, step_id: str, parent_id=None, user_conversation=None):
        """
        Initializes an ConversationStep instance.
        Args:
            step_id (str): Identifier for the step.
            parent_id (str): Identifier for the parental autonomic task.
            user_conversation (dict): user conversation content for this step.
        """
        super().__init__()
        self.step_id = step_id
        self.parent_id = parent_id
        self.llm_conversation = dict()  # gpt conversation response for this step.
        self.user_conversation = user_conversation if user_conversation else dict()
