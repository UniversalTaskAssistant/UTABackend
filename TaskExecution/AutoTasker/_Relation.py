

class _Relation:
    def __init__(self, step_id: int, relation: str, reason: str):
        self.step_id: int = step_id
        self.relation: str = relation
        self.reason: str = reason

    def __dict__(self):
        return {
            'step_id': self.step_id,
            'relation': self.relation,
            'reason': self.reason
        }

    def __str__(self):
        return f"_Relation(step_id={self.step_id}, relation={self.relation}, reason={self.reason})"