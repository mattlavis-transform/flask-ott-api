class MeasureType(object):
    measure_type_id = None
    description = None
    measure_type_series_id = None
    measure_type_series_description = None

    def __init__(self, measure_type_id, description):
        self.measure_type_id = measure_type_id
        self.description = description

    def as_dict(self):
        obj_d = {
            'id': self.measure_type_id,
            'description': self.description,
            'measure_type_series_id': self.measure_type_series_id,
            'measure_type_series_description': self.measure_type_series_description
        }
        return obj_d
