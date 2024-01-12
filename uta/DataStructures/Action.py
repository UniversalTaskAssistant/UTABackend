from ._Data import _Data


class Action(_Data):
    def __init__(self, action, element_id, description, input_text, reason):
        super().__init__()
        self.action = action
        self.element_id = element_id
        self.description = description
        self.input_text = input_text
        self.reason = reason
