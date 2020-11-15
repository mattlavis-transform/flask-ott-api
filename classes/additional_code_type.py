class AdditionalCodeType(object):
    additional_code_type_id = None
    application_code = None
    description = None

    def __init__(self, additional_code_type_id, application_code, description):
        self.additional_code_type_id = additional_code_type_id
        self.application_code = application_code
        self.description = description

    def as_dict(self):
        obj_d = {
            'additional_code_type_id': self.additional_code_type_id,
            'application_code': self.application_code,
            'description': self.description
        }
        return obj_d
