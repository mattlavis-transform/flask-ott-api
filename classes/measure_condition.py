class MeasureCondition(object):
    measure_sid = None
    condition_code = None
    condition_code_description = None
    document_code = None
    action_code = None
    action = None
    requirement = None
    certificate_description = None
    certificate_type_description = None


    def __init__(self):
        pass

    def get_requirement(self):
        self.requirement = None
        if self.certificate_type_description != "":
            self.requirement = self.certificate_type_description + ": "
            self.requirement += self.certificate_description

    def as_dict(self):
        obj_d = {
            'condition_code': self.condition_code,
            'condition': self.condition_code + ": " + self.condition_code_description,
            'document_code': self.document_code,
            'requirement': self.requirement,
            'action': self.action,
            'duty_expression': "",
            # 'action_code': self.action_code,
        }
        return obj_d
