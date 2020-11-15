class AdditionalCode(object):
    additional_code_type_id = None
    application_code = None
    description = None

    def __init__(self, additional_code_type_id, additional_code_id, description):
        self.additional_code_type_id = additional_code_type_id
        self.additional_code_id = additional_code_id
        self.code = self.additional_code_type_id + self.additional_code_id
        self.description = description

    def as_dict(self):
        obj_d = {
            'additional_code_type_id': self.additional_code_type_id,
            'additional_code_id': self.additional_code_id,
            'code': self.code,
            'description': self.description
        }
        return obj_d
