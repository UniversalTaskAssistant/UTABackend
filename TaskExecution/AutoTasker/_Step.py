

class _AutoModeStep:
    def __init__(self, step_id: int, **kwargs):
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
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"No attribute {key} defined in {self.__class__.__name__}.")