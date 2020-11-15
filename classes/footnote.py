class Footnote(object):
    footnote_type_id = None
    footnote_id = None
    code = None
    description = None
    measure_sid = None

    def __init__(self, footnote_type_id, footnote_id, description, measure_sid = None):
        self.footnote_type_id = footnote_type_id
        self.footnote_id = footnote_id
        self.code = self.footnote_type_id + self.footnote_id
        self.description = description
        self.measure_sid = measure_sid

    def as_dict(self):
        obj_d = {
            'code': self.code,
            'description': self.description,
            'formatted_description': self.description
        }
        return obj_d
