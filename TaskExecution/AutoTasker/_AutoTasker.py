from . import _TaskUIActionChecker, _TaskUIRelationChecker


class _AutoTasker:
    def __init__(self):
        self.relation_checker = _TaskUIRelationChecker()
        self.action_checker = _TaskUIActionChecker()