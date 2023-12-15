

class Action:
    def __init__(self, step_id: int, is_go_back: bool, action: str, element_id: int, description: str,
                 input_text: str, reason: str):
        self.step_id: int = step_id
        self.is_go_back: bool = is_go_back
        self.action: str = action
        self.element_id: int = element_id
        self.description: str = description
        self.input_text: str = input_text
        self.reason: str = reason