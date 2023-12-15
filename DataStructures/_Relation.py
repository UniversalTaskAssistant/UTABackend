

class _Relation:
    def __init__(self, step_id: int, relation: str, reason: str):
        self.step_id: int = step_id
        self.relation: str = relation
        self.reason: str = reason