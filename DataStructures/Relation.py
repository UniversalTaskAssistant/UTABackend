from ._Data import _Data


class Relation(_Data):
    def __init__(self, relation: str, reason: str):
        super().__init__()
        self.relation = relation
        self.reason = reason
