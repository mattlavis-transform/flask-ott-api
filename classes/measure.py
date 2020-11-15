from classes.config import Config
from classes.geographical_area import GeographicalArea
from classes.measure_type import MeasureType
from classes.duty_expression import DutyExpression
from classes.legal_act import LegalAct


class Measure(object):
    measure_sid = None
    goods_nomenclature_item_id = None
    geographical_area_id = None
    measure_type_id = None
    measure_type_description = None
    trade_movement_code = None
    measure_type_series_id = None
    measure_generating_regulation_id = None
    ordernumber = None
    additional_code_type_id = None
    additional_code_id = None
    additional_code = None
    geographical_area_sid = None
    goods_nomenclature_sid = None
    additional_code_sid = None
    effective_start_date = None
    effective_end_date = None
    is_import = False
    is_export = False
    is_vat = False
    is_excise = False
    is_mfn = False
    origin = "eu"
    geographical_area_description = None
    geographical_area = None
    measure_type = None
    duty_expression = None
    reduction_indicator = None
    measure_conditions = []
    measure_components = []
    measure_exclusions = []
    measure_footnotes = []
    legal_acts = []
    combined_duty = ""
    regulation_officialjournal_number = None
    regulation_officialjournal_page = None
    regulation_published_date = None
    regulation_validity_start_date = None
    regulation_validity_end_date = None

    def __init__(self):
        self.measure_conditions = []
        self.measure_components = []
        self.measure_exclusions = []
        self.measure_footnotes = []

    def as_dict(self):
        footnotes = []
        for f in self.measure_footnotes:
            footnotes.append(f.as_dict())

        obj_d = {
            'id': self.measure_sid,
            'origin': self.origin,
            'effective_start_date': self.effective_start_date,
            'effective_end_date': self.effective_end_date,
            'import': self.is_import,
            'measure_conditions': self.measure_conditions,
            'geographical_area': self.geographical_area.as_dict(),
            'excluded_countries': self.measure_exclusions,
            'footnotes': footnotes,
            'order_number': self.ordernumber,
            'excise': self.is_excise,
            'vat': self.is_vat,
            'measure_type': self.measure_type.as_dict(),
            'duty_expression': self.duty_expression.as_dict(),
            'legal_acts': self.legal_acts
        }

        return obj_d

    def interpret(self):
        self.interpret_trade_movement_code()
        self.interpret_vat_excise_mfn()
        self.interpret_origin()
        self.create_geography_node()
        self.create_measure_type_node()
        self.get_legal_acts()

    def get_legal_acts(self):
        self.legal_acts = []
        l = LegalAct(self.measure_generating_regulation_id, self.regulation_validity_start_date, self.regulation_validity_end_date,
                      self.regulation_officialjournal_number, self.regulation_officialjournal_page, self.regulation_published_date)
        self.legal_acts.append(l.as_dict())
        pass

    def interpret_trade_movement_code(self):
        # 0 Import – majority of measure types concern import, as the tariff primarily deals with import
        # 1 Export – most of these are export controls (e.g. sanctions)
        # 2 Import/export – there are very few measure types which are applicable to both import and export

        self.trade_movement_code = str(self.trade_movement_code)
        if self.trade_movement_code == "0":
            self.is_import = True
            self.is_export = False

        elif self.trade_movement_code == "1":
            self.is_import = False
            self.is_export = True

        elif self.trade_movement_code == "2":
            self.is_import = True
            self.is_export = True

    def interpret_vat_excise_mfn(self):
        if self.measure_type_series_id == 'P':
            self.is_vat = True

        elif self.measure_type_series_id == 'Q':
            self.is_excise = True

        if self.measure_type_id in ("103", "105"):
            self.is_mfn = True
        else:
            self.is_mfn = False

    def interpret_origin(self):
        if self.measure_sid < 0:
            self.origin = "uk"
        else:
            self.origin = "eu"

    def create_geography_node(self):
        self.geographical_area = GeographicalArea(
            self.geographical_area_id, self.geographical_area_description)
        if len(self.geographical_area_id) == 4:
            self.get_children_geographical_areas()

    def get_children_geographical_areas(self):
        c = Config()
        self.geographical_area.children_geographical_areas = []
        for item in c.geo_memberships:
            if item.geographical_area_group_sid == self.geographical_area_sid:
                self.geographical_area.children_geographical_areas.append(
                    item.as_dict())
                pass

    def create_measure_type_node(self):
        self.measure_type = MeasureType(
            self.measure_type_id, self.measure_type_description)

    def combine_duties(self):
        self.combined_duty = ""
        if (len(self.measure_components)) > 0:
            for mc in self.measure_components:
                self.combined_duty += mc["duty_string"] + " "

            self.combined_duty = self.combined_duty.replace("  ", " ")
            self.combined_duty = self.combined_duty.strip()
            self.duty_expression = DutyExpression(self.combined_duty)
        else:
            self.duty_expression = DutyExpression("")
