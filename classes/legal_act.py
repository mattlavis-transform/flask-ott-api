from classes.config import Config
import datetime
from datetime import datetime


class LegalAct(object):
    measure_generating_regulation_id = None
    validity_start_date = None
    validity_end_date = None
    officialjournal_number = None
    officialjournal_page = None
    published_date = None
    regulation_code = None
    regulation_url = None

    def __init__(self, measure_generating_regulation_id, validity_start_date, validity_end_date, officialjournal_number, officialjournal_page, published_date):
        self.measure_generating_regulation_id = measure_generating_regulation_id
        self.validity_start_date = validity_start_date
        self.validity_end_date = validity_end_date
        self.officialjournal_number = officialjournal_number
        self.officialjournal_page = officialjournal_page
        self.published_date = published_date
        self.get_eu_url()
        self.get_regulation_code()

    def get_eu_url(self):
        c = Config()
        if self.officialjournal_number is not None:
            year = self.published_date.year
            self.officialjournal_page = c.mstr(self.officialjournal_page)
            page = f'{self.officialjournal_page:0>4}'
            template = "http://eur-lex.europa.eu/search.html?whOJ=NO_OJ%3D<journal>,YEAR_OJ%3D<year>,PAGE_FIRST%3D<page>&DB_COLL_OJ=oj-l&type=advanced&lang=en"
            s = template.replace("<page>", page)
            s = s.replace("<year>", str(year))
            s = s.replace("<journal>", ''.join(
                filter(str.isdigit, self.officialjournal_number)))

            self.regulation_url = s
        else:
            self.regulation_url = None

    def get_regulation_code(self):
        # D1700370 -> D0037/17
        s = self.measure_generating_regulation_id
        self.regulation_code = s[0] + s[3:7] + "/" + s[1:3]

    def as_dict(self):
        self.published_date_string = self.published_date.strftime("%Y-%m-%d")
        self.validity_start_date = self.validity_start_date.strftime("%Y-%m-%dT00:00:00.000Z")
        if self.validity_end_date is not None:
            self.validity_end_date = self.validity_end_date.strftime("%Y-%m-%dT00:00:00.000Z")
        obj_d = {
            'validity_start_date': self.validity_start_date,
            'validity_end_date': self.validity_end_date,
            'officialjournal_number': self.officialjournal_number,
            'officialjournal_page': self.officialjournal_page,
            'published_date': self.published_date_string,
            'regulation_code': self.regulation_code,
            'regulation_url': self.regulation_url
        }
        return obj_d
