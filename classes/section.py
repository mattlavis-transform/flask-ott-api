import roman

class Section(object):
    title = None
    position = None
    numeral = None

    def __init__(self, position, title):
        self.title = title
        self.position = position
        self.numeral = roman.toRoman(int(self.position))

    def as_dict(self):
        obj_d = {
            'title': self.title,
            'position': self.position,
            'numeral': self.numeral,
            'section_note': None
        }
        return obj_d
