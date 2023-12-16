

class _Action:
    def __init__(self, step_id: int, action: str, element_id: int, description: str,
                 input_text: str, reason: str):
        self.step_id: int = step_id
        self.action: str = action
        self.element_id: int = element_id
        self.description: str = description
        self.input_text: str = input_text
        self.reason: str = reason

    def __dict__(self):
        return {
            'step_id': self.step_id,
            'action': self.action,
            'element_id': self.element_id,
            'description': self.description,
            'input_text': self.input_text,
            'reason': self.reason,
        }

    def __str__(self):
        return f"_Action(step_id={self.step_id}, action={self.action}, element_id={self.element_id}, " \
            f"description={self.description}, input_text={self.input_text}, reason={self.reason})"