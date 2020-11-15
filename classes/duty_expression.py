class DutyExpression(object):
    base = None
    formatted_base = None

    def __init__(self, base):
        self.base = base
        self.formatted_base = base

    def as_dict(self):
        obj_d = {
            'base': self.base,
            'formatted_base': self.formatted_base
        }
        return obj_d
