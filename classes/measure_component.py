from classes.config import Config


class MeasureComponent(object):
    measure_sid = None
    duty_expression_id = None
    duty_amount = None
    monetary_unit_code = None
    measurement_unit_code = None
    measurement_unit_qualifier_code = None
    duty_expression_description = None
    monetary_unit_description = None
    measurement_unit_description = None
    measurement_unit_qualifier_description = None
    duty_string = ""

    def __init__(self):
        pass

    def as_dict(self):
        obj_d = {
            'duty_expression_id': self.duty_expression_id,
            'duty_amount': self.duty_amount,
            'monetary_unit_code': self.monetary_unit_code,
            'measurement_unit_code': self.measurement_unit_code,
            'measurement_unit_qualifier_code': self.measurement_unit_qualifier_code,
            'duty_expression_description': self.duty_expression_description,
            'monetary_unit_description': self.monetary_unit_description,
            'measurement_unit_description': self.measurement_unit_description,
            'measurement_unit_qualifier_description': self.measurement_unit_qualifier_description,
            'duty_string': self.duty_string
        }
        return obj_d

    def get_duty_string(self):
        c = Config()
        self.duty_string = ""

        self.monetary_unit_code = c.mstr(self.monetary_unit_code)
        self.measurement_unit_code = c.mstr(self.measurement_unit_code)
        self.measurement_unit_qualifier_code = c.mstr(
            self.measurement_unit_qualifier_code)

        if self.duty_expression_id == "01":  # Ad valorem or specific
            if self.monetary_unit_code == "":
                self.duty_string += "{0:1.2f}".format(self.duty_amount) + "%"
            else:
                self.duty_string += "{0:1.3f}".format(
                    self.duty_amount) + " " + self.monetary_unit_code
                if self.measurement_unit_code != "":
                    self.duty_string += " / " + \
                        self.get_measurement_unit(self.measurement_unit_code)
                    if self.measurement_unit_qualifier_code != "":
                        self.duty_string += " / " + self.get_measurement_unit_qualifier_code()

        elif self.duty_expression_id in ("04", "19", "20"):  # Plus % or amount
            if self.monetary_unit_code == "":
                self.duty_string += "+ {0:1.2f}".format(self.duty_amount) + "%"
            else:
                self.duty_string += "+ {0:1.3f}".format(
                    self.duty_amount) + " " + self.monetary_unit_code
                if self.measurement_unit_code != "":
                    self.duty_string += " / " + \
                        self.get_measurement_unit(self.measurement_unit_code)
                    if self.measurement_unit_qualifier_code != "":
                        self.duty_string += " / " + self.get_measurement_unit_qualifier_code()

        elif self.duty_expression_id == "12":  # Agri component
            self.duty_string += " + AC"

        elif self.duty_expression_id == "15":  # Minimum
            if self.monetary_unit_code == "":
                self.duty_string += "MIN {0:1.2f}".format(
                    self.duty_amount) + "%"
            else:
                self.duty_string += "MIN {0:1.3f}".format(
                    self.duty_amount) + " " + self.monetary_unit_code
                if self.measurement_unit_code != "":
                    self.duty_string += " / " + \
                        self.get_measurement_unit(self.measurement_unit_code)
                    if self.measurement_unit_qualifier_code != "":
                        self.duty_string += " / " + self.get_measurement_unit_qualifier_code()

        elif self.duty_expression_id == "17":  # Maximum
            if self.monetary_unit_code == "":
                self.duty_string += "MAX {0:1.2f}".format(
                    self.duty_amount) + "%"
            else:
                self.duty_string += "MAX {0:1.3f}".format(
                    self.duty_amount) + " " + self.monetary_unit_code
                if self.measurement_unit_code != "":
                    self.duty_string += " / " + \
                        self.get_measurement_unit(self.measurement_unit_code)
                    if self.measurement_unit_qualifier_code != "":
                        self.duty_string += " / " + self.get_measurement_unit_qualifier_code()

        elif self.duty_expression_id == "21":  # Sugar duty
            self.duty_string += " + SD"

        elif self.duty_expression_id == "27":  # Flour duty
            self.duty_string += " + FD"

    def get_measurement_unit(self, s):
        if s == "ASV":
            return "% vol"  # 3302101000
        if s == "NAR":
            return "item"
        elif s == "CCT":
            return "ct/l"
        elif s == "CEN":
            return "100 p/st"
        elif s == "CTM":
            return "c/k"
        elif s == "DTN":
            return "100 kg"
        elif s == "GFI":
            return "gi F/S"
        elif s == "GRM":
            return "g"
        elif s == "HLT":
            return "hl"  # 2209009100
        elif s == "HMT":
            return "100 m"  # 3706909900
        elif s == "KGM":
            return "kg"
        elif s == "KLT":
            return "1,000 l"
        elif s == "KMA":
            return "kg met.am."
        elif s == "KNI":
            return "kg N"
        elif s == "KNS":
            return "kg H2O2"
        elif s == "KPH":
            return "kg KOH"
        elif s == "KPO":
            return "kg K2O"
        elif s == "KPP":
            return "kg P<sup>2</sup>O<sup>5</sup>"
        elif s == "KSD":
            return "kg 90 % sdt"
        elif s == "KSH":
            return "kg NaOH"
        elif s == "KUR":
            return "kg U"
        elif s == "LPA":
            return "l alc. 100%"
        elif s == "LTR":
            return "l"
        elif s == "MIL":
            return "1,000 items"
        elif s == "MTK":
            return "m2"
        elif s == "MTQ":
            return "m3"
        elif s == "MTR":
            return "m"
        elif s == "MWH":
            return "1,000 kWh"
        elif s == "NCL":
            return "ce/el"
        elif s == "NPR":
            return "pa"
        elif s == "TJO":
            return "TJ"
        elif s == "TNE":
            return "tonne"  # 1005900020
            # return "1000 kg" # 1005900020
        else:
            return s

    def get_measurement_unit_qualifier_code(self):
        qualifier_description = ""
        s = self.measurement_unit_qualifier_code
        if s == "A":
            qualifier_description = "tot alc"  # Total alcohol
        elif s == "C":
            qualifier_description = "1 000"  # Total alcohol
        elif s == "E":
            qualifier_description = "net drained wt"  # net of drained weight
        elif s == "G":
            qualifier_description = "gross"  # Gross
        elif s == "M":
            qualifier_description = "net dry"  # net of dry matter
        elif s == "P":
            qualifier_description = "lactic matter"  # of lactic matter
        elif s == "R":
            qualifier_description = "std qual"  # of the standard quality
        elif s == "S":
            qualifier_description = " raw sugar"
        elif s == "T":
            qualifier_description = "dry lactic matter"  # of dry lactic matter
        elif s == "X":
            qualifier_description = " hl"  # Hectolitre
        elif s == "Z":
            qualifier_description = "% sacchar."  # per 1% by weight of sucrose
        return qualifier_description
