class FootnoteType(object):
    footnote_type_id = None
    application_code = None
    description = None

    def __init__(self, footnote_type_id, application_code, description):
        self.footnote_type_id = footnote_type_id
        self.application_code = application_code
        self.description = description

    def as_dict(self):
        obj_d = {
            'footnote_type_id': self.footnote_type_id,
            'application_code': self.application_code,
            'description': self.description
        }
        return obj_d
