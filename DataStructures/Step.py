from ._Data import _Data


class AutoModeStep(_Data):
    def __init__(self, step_id: str, parent_id="None", is_go_back=False, recommended_action="None", relation="None",
                 ui_data="None", execution_result="None"):
        """
        Initializes an AutoModeStep instance.
        Args:
            step_id (str): Identifier for the step.
            parent_id (str): Identifier for the parental autonomic task.
            is_go_back (bool): Indicates if the step involves a 'go back' action.
            recommended_action (Action): Recommended action for this step.
            relation (Relation): Relation of this step to the task.
            ui_data (UI_Data): UI data associated with this step.
            execution_result (str): Execution result of the step.
        """
        super().__init__(step_id=step_id, parent_id=parent_id, is_go_back=is_go_back, relation=relation,
                         execution_result=execution_result)
        self.ui_data = ui_data
        self.recommended_action = recommended_action

    def annotate_ui_operation(self):
        assert self.ui_data != "None" and self.recommended_action != "None"
        self.ui_data.annotate_ui_operation(self.recommended_action)


class InquiryStep(_Data):
    def __init__(self, step_id: str, parent_id="None", user_conversation=None, llm_conversation=None):
        """
        Initializes an ConversationStep instance.
        Args:
            step_id (str): Identifier for the step.
            parent_id (str): Identifier for the parental autonomic task.
            user_conversation (dict): user conversation content for this step.
            llm_conversation (dict): gpt conversation response for this step.
        """
        super().__init__(step_id=step_id, parent_id=parent_id)

        self.llm_conversation = llm_conversation if llm_conversation else dict()
        self.user_conversation = user_conversation if user_conversation else dict()
