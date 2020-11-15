class CertificateType(object):
    certificate_type_code = None
    description = None

    def __init__(self, certificate_type_code, description):
        self.certificate_type_code = certificate_type_code
        self.description = description

    def as_dict(self):
        obj_d = {
            'certificate_type_code': self.certificate_type_code,
            'description': self.description
        }
        return obj_d
