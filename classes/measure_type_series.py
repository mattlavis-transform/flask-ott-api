class MeasureTypeSeries(object):
    measure_type_series_id = None
    description = None
    measure_type_combination = None

    def __init__(self, measure_type_id, description, measure_type_combination):
        self.measure_type_id = measure_type_id
        self.description = description
        self.measure_type_combination = measure_type_combination

    def as_dict(self):
        obj_d = {
            'id': self.measure_type_id,
            'description': self.description,
            'measure_type_combination': self.measure_type_combination
        }
        return obj_d
