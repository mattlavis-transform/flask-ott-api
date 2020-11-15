class Link(object):
    rel = None
    href = None

    def __init__(self, rel, href):
        self.rel = rel
        self.href = href

    def as_dict(self):
        obj_d = {
            'rel': self.rel,
            'href': self.href
        }
        return obj_d
