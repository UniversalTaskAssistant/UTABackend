from ._Data import _Data


class Action(_Data):
    def __init__(self, action: str, element_id: int, description: str,
                 input_text: str, reason: str):
        super().__init__(action=action, element_id=element_id, description=description, input_text=input_text,
                         reason=reason)
