

class Relation:
    def __init__(self, relation: str, reason: str):
        self.relation: str = relation
        self.reason: str = reason

    def __dict__(self):
        return {
            'relation': self.relation,
            'reason': self.reason
        }

    def __str__(self):
        return f"Relation(relation={self.relation}, reason={self.reason})"
