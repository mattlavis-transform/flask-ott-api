class GeoMembership(object):
    geographical_area_id = None
    description = None
    measure_sid = None

    def __init__(self, geographical_area_group_sid, geographical_area_id, description):
        self.geographical_area_group_sid = geographical_area_group_sid
        self.geographical_area_id = geographical_area_id
        self.description = description

    def as_dict(self):
        obj_d = {
            'id': self.geographical_area_id,
            'description': self.description
        }
        return obj_d
