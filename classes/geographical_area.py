class GeographicalArea(object):
    geographical_area_id = None
    description = None
    measure_sid = None
    children_geographical_areas = []

    def __init__(self, geographical_area_id, description):
        self.geographical_area_id = geographical_area_id
        self.description = description

    def as_dict(self):
        obj_d = {
            'id': self.geographical_area_id,
            'description': self.description,
            'children_geographical_areas': self.children_geographical_areas
        }
        return obj_d

    def as_exclusion_dict(self):
        obj_d = {
            'geographical_area_id': self.geographical_area_id,
            'description': self.description
        }
        return obj_d
