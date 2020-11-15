# Import custom libraries
import sys
import re
import collections

from classes.measure import Measure
from classes.measure_condition import MeasureCondition
from classes.measure_component import MeasureComponent
from classes.geographical_area import GeographicalArea
from classes.geo_membership import GeoMembership
from classes.footnote import Footnote
from classes.section import Section
from classes.link import Link
from classes.database import Database
from classes.config import Config

class GoodsNomenclature(object):
    chapter_id = None
    heading_id = None
    goods_nomenclature_item_id = None
    commcode_plus_suffix = None
    goods_nomenclature_sid = None
    number_indents = None
    description = ""
    formatted_description = ""
    description_plain = ""
    bti_url = ""
    ancestors = []
    descendants = []
    measures = []
    measure_conditions = []
    measure_components = []
    measure_exclusions = []
    import_measures = []
    export_measures = []
    commodity_footnotes = []
    measure_footnotes = []
    guides = []
    section = None
    chapter = None
    heading = None
    object_type = None
    leaf = None
    declarable = None
    context = None
    parent_sid = None
    search_references_count = 0
    meursing_code = False
    basic_duty_rate = None
    links = []
    is_meursing = False
    meursing_additional_code_id = None
    meursing_geographical_area_id = None

    def __init__(self, commodity, meursing_additional_code_id = None, meursing_geographical_area_id = None):
        self.measures = []
        self.meursing_additional_code_id = meursing_additional_code_id
        self.meursing_geographical_area_id = meursing_geographical_area_id
        if len(commodity) == 4:
            self.goods_nomenclature_item_id = commodity.ljust(10, "0")
            self.object_type = "heading"
        else:
            self.goods_nomenclature_item_id = commodity
            self.object_type = "commodity"

        # If this is amn empty comm code, then it's a Meursing placeholder
        if commodity == "":
            self.is_meursing = True

        self.productline_suffix = "80"
        self.chapter_id = self.goods_nomenclature_item_id[0:2]
        self.heading_id = self.goods_nomenclature_item_id[0:4]
        self.date = '2020-01-01'
        if self.is_meursing == False:
            self.get_guides()

    def get_guides(self):
        # Dummy only
        self.guides = []
        guide = {}
        guide["title"] = "Classification of goods"
        guide["url"] = "https://www.gov.uk/government/collections/classification-of-goods"
        self.guides.append(guide)

    def get_ancestors_and_descendants(self):
        self.get_ancestors()
        self.get_descendants()

    def get_ancestors(self):
        # Get core data like the description
        d = Database()
        c = Config()
        self.ancestors = []
        self.codes = []

        params = [
            self.date,
            self.date,
            self.date,
            self.chapter_id,
            self.goods_nomenclature_item_id
        ]
        rows = d.run_query(c.sql["ancestors"], params)
        row_count = len(rows)
        if row_count < 1:
            return

        # Data in the first row is the current commodity
        self.description = rows[0][3]
        self.number_indents = rows[0][4]
        self.commcode_plus_suffix = rows[0][5]
        current_indent = 99
        for row in rows:
            goods_nomenclature_sid = row[0]
            goods_nomenclature_item_id = row[1]
            productline_suffix = row[2]
            description = row[3]
            number_indents = row[4]
            commcode_plus_suffix = row[5]

            if (number_indents < current_indent) or (goods_nomenclature_item_id[-8:] == "00000000"):
                gn = GoodsNomenclature(goods_nomenclature_item_id)
                gn.goods_nomenclature_sid = goods_nomenclature_sid
                gn.productline_suffix = productline_suffix
                gn.description = description
                gn.number_indents = number_indents
                gn.commcode_plus_suffix = commcode_plus_suffix
                gn.get_formatted_descriptions()
                gn.context = "ancestor"

                if commcode_plus_suffix != self.commcode_plus_suffix:
                    self.ancestors.append(gn)

                if productline_suffix == '80':
                    self.codes.append(goods_nomenclature_item_id)

            if number_indents < current_indent:
                current_indent = number_indents

        return row_count

    def get_descendants(self):
        # Get descendants of the selected commodity code or heading
        d = Database()
        c = Config()
        self.descendants = []
        params = [
            self.date,
            self.date,
            self.date,
            self.heading_id,
            self.goods_nomenclature_item_id + self.productline_suffix
        ]
        rows = d.run_query(c.sql["descendants"], params)
        row_count = len(rows)
        if row_count < 1:
            return False

        # Data in the first row is the current commodity
        self.goods_nomenclature_sid = rows[0][0]
        self.description = rows[0][3]
        self.get_formatted_descriptions()
        self.number_indents = rows[0][4]
        self.commcode_plus_suffix = rows[0][5]

        start_indent = self.number_indents
        for row in rows:
            goods_nomenclature_sid = row[0]
            goods_nomenclature_item_id = row[1]
            productline_suffix = row[2]
            description = row[3]
            number_indents = row[4]
            commcode_plus_suffix = row[5]

            if (number_indents > start_indent):
                gn = GoodsNomenclature(goods_nomenclature_item_id)
                gn.goods_nomenclature_sid = goods_nomenclature_sid
                gn.productline_suffix = productline_suffix
                gn.description = description
                gn.number_indents = number_indents
                gn.commcode_plus_suffix = commcode_plus_suffix
                gn.context = "descendant"
                gn.get_formatted_descriptions()

                if commcode_plus_suffix != self.commcode_plus_suffix:
                    self.descendants.append(gn.as_dict())

            if commcode_plus_suffix > self.commcode_plus_suffix:
                if number_indents <= start_indent:
                    break

        self.leaf = True if len(self.descendants) == 0 else False
        self.declarable = True if (
            len(self.descendants) == 0 and self.productline_suffix == '80') else False

        self.get_descendant_parentage(self.goods_nomenclature_sid)
        return True

    def as_dict(self):
        if self.object_type == "chapter":
            obj_d = {
                'goods_nomenclature_item_id': self.goods_nomenclature_item_id,
                'description': self.description,
                'formatted_description': self.formatted_description.capitalize(),
                'guides': self.guides,
                'chapter_note': None
            }
        elif self.object_type == "heading":
            obj_d = {
                'goods_nomenclature_item_id': self.goods_nomenclature_item_id,
                'description': self.description,
                'formatted_description': self.formatted_description,
                'description_plain': self.description_plain
            }
        else:
            if self.context == "ancestor":
                obj_d = {
                    'producline_suffix': self.productline_suffix,
                    'description': self.description,
                    'number_indents': self.number_indents,
                    'goods_nomenclature_item_id': self.goods_nomenclature_item_id,
                    # 'goods_nomenclature_sid': self.goods_nomenclature_sid,
                    'formatted_description': self.formatted_description,
                    'description_plain': self.description_plain,
                    # 'object_type': self.object_type
                }
            else:
                obj_d = {
                    'goods_nomenclature_sid': self.goods_nomenclature_sid,
                    'producline_suffix': self.productline_suffix,
                    'goods_nomenclature_item_id': self.goods_nomenclature_item_id,
                    'number_indents': self.number_indents,
                    'description': self.description,
                    'formatted_description': self.formatted_description,
                    'description_plain': self.description_plain,
                    'leaf': self.leaf,
                    'parent_sid': self.parent_sid,
                    'search_references_count': self.search_references_count
                }
        return obj_d

    def return_error(self, msg=""):
        results = collections.OrderedDict()
        results["error"] = "404 - Not Found"
        if msg != "":
            print(msg)
        return results

    def get_commodity_json(self):
        results = collections.OrderedDict()

        if len(self.goods_nomenclature_item_id) != 10:
            return self.return_error("Length of commodity is not 10 digits")

        if not self.declarable:
            return self.return_error("Commodity is not declarable")

        if len(self.ancestors) == 0:
            return self.return_error("No ancestors")

        self.get_geo_memberships()
        self.ancestors.reverse()
        self.split_ancestors()
        self.get_section()
        self.get_measures()
        self.get_measure_conditions()
        self.assign_measure_conditions()
        self.get_measure_components()
        self.assign_measure_components()
        self.get_measure_exclusions()
        self.assign_measure_exclusions()
        self.get_measure_footnotes()
        self.assign_measure_footnotes()
        self.get_duty_expressions()
        self.sort_measures()
        self.assign_measures_to_import_export()
        self.get_commodity_footnotes()
        self.populate_links()

        # Get the stuff that does not need to be got from the database
        results["producline_suffix"] = self.productline_suffix
        results["description"] = self.description
        results["number_indents"] = self.number_indents
        results["goods_nomenclature_item_id"] = self.goods_nomenclature_item_id
        results["bti_url"] = "http://ec.europa.eu/taxation_customs/dds2/ebti/ebti_consultation.jsp?Lang=en&nomenc=" + \
            self.goods_nomenclature_item_id + "&Expand=true"
        results["formatted_description"] = self.formatted_description
        results["description_plain"] = self.description_plain
        results["consigned_from"] = None
        results["basic_duty_rate"] = self.basic_duty_rate
        results["meursing_code"] = self.meursing_code
        results["section"] = self.section
        results["chapter"] = self.chapter.as_dict()
        results["declarable"] = self.declarable
        results["import_measures"] = self.import_measures
        results["export_measures"] = self.export_measures
        results["footnotes"] = self.commodity_footnotes
        results["heading"] = self.heading.as_dict()
        if len(self.ancestors) > 0:
            results["ancestors"] = []
            for item in self.ancestors:
                results["ancestors"].append(item.as_dict())
        results["_response_info"] = {}
        results["_response_info"]["links"] = self.links

        return results

    def populate_links(self):
        self.links = []
        l = Link("self", "/trade-tariff/commodities/" +
                 self.goods_nomenclature_item_id + ".json?currency=EUR")
        self.links.append(l.as_dict())
        l = Link("heading", "/trade-tariff/admin/headings/" + self.heading_id)
        self.links.append(l.as_dict())
        l = Link("chapter", "/trade-tariff/admin/chapters/" + self.chapter_id)
        self.links.append(l.as_dict())
        l = Link("section", "/trade-tariff/admin/sections/" +
                 str(self.section["position"]))
        self.links.append(l.as_dict())

    def split_ancestors(self):
        # self.ancestors[0]["object_type"] = "chapter"
        self.ancestors[0].object_type = "chapter"
        self.chapter = self.ancestors[0]
        self.ancestors.pop(0)
        if len(self.ancestors) > 0:
            # self.ancestors[0]["object_type"] = "heading"
            self.ancestors[0].object_type = "heading"
            self.heading = self.ancestors[0]
            self.ancestors.pop(0)

    def get_formatted_descriptions(self):
        break_tag = "<br />"
        s = self.description
        s = s.replace("|", " ")
        s = s.replace("  ", " ")
        s = s.strip()
        self.description_plain = s

        s = self.description_plain.replace("\n", break_tag)
        s = s.replace(break_tag + " " + break_tag, break_tag)
        s = s.replace(break_tag + break_tag, break_tag)
        self.formatted_description = s
        self.formatted_description = re.sub(
            "@(.)", '<sup>\\1</sup>', self.formatted_description, flags=re.MULTILINE)
        self.formatted_description = re.sub(
            "\$(.)", '<sub>\\1</sub>', self.formatted_description, flags=re.MULTILINE)

        self.description_plain = self.description_plain.replace("\n", " ")
        self.description_plain = self.description_plain.replace("  ", " ")
        self.description_plain = re.sub(
            "@(.)", '\\1', self.description_plain, flags=re.MULTILINE)
        self.description_plain = re.sub(
            "\$(.)", '\\1', self.description_plain, flags=re.MULTILINE)

    def get_measures(self):
        c = Config()
        d = Database()
        self.measures = []

        if self.is_meursing:
            params = [
                self.meursing_additional_code_id,
                self.meursing_additional_code_id,
                self.meursing_geographical_area_id,
                '2021-01-01',
                '2021-01-01',
                self.meursing_geographical_area_id
            ]
            rows = d.run_query(c.sql["meursing_measures"], params)
        else:
            comm_code_string = self.get_comm_code_string()
            c.sql["measures"] = c.sql["measures"].replace("<params>", comm_code_string)
            c.sql["measures"] = c.sql["measures"].replace("<date>", self.date)
            rows = d.run_query(c.sql["measures"])
        
        self.measure_sids = []
        for row in rows:
            m = Measure()
            m.measure_sid = row[0]
            m.goods_nomenclature_item_id = row[1]
            m.geographical_area_id = row[2]
            m.measure_type_id = row[3]
            m.measure_type_description = row[4]
            m.trade_movement_code = row[5]
            m.measure_type_series_id = row[6]
            m.measure_generating_regulation_id = row[7]
            m.ordernumber = row[8]
            m.additional_code_type_id = row[9]
            m.additional_code_id = row[10]
            m.additional_code = row[11]
            m.geographical_area_sid = row[12]
            m.goods_nomenclature_sid = row[13]
            m.additional_code_sid = row[14]
            m.effective_start_date = row[15]
            m.effective_end_date = row[16]
            m.regulation_officialjournal_number = row[17]
            m.regulation_officialjournal_page = row[18]
            m.regulation_published_date = row[19]
            m.regulation_validity_start_date = row[20]
            m.regulation_validity_end_date = row[21]
            m.geographical_area_description = row[22]
            m.reduction_indicator = row[23]
            self.measure_sids.append(m.measure_sid)
            if m.effective_start_date is not None:
                m.effective_start_date += "T00:00:00.000Z"

            m.interpret()

            self.measures.append(m)

    def assign_measures_to_import_export(self):
        c = Config()
        self.import_measures = []
        self.export_measures = []
        for m in self.measures:
            if m.measure_type_id not in c.excluded_measure_types:
                if m.is_import:
                    self.import_measures.append(m.as_dict())
                if m.is_export:
                    self.export_measures.append(m.as_dict())

    def assign_meursing_measures(self):
        self.meursing_measures = []
        for m in self.measures:
            self.meursing_measures.append(m.as_dict())

    def sort_measures(self):
        self.measures.sort(key=lambda x: x.measure_type_id, reverse=False)
        self.measures.sort(key=lambda x: x.geographical_area_id, reverse=False)
        self.measures.sort(key=lambda x: x.is_mfn, reverse=True)
        self.measures.sort(key=lambda x: x.is_excise, reverse=True)
        self.measures.sort(key=lambda x: x.is_vat, reverse=True)

    def get_comm_code_string(self):
        s = ""
        for code in self.codes:
            s += "'" + code + "', "
        s = s.strip()
        s = s.strip(",")
        return s

    def get_measure_sid_string(self):
        s = ""
        for sid in self.measure_sids:
            s += str(sid) + ", "
        s = s.strip()
        s = s.strip(",")
        return s

    def get_measure_conditions(self):
        d = Database()
        c = Config()
        self.measure_conditions = []
        self.meursing_code = False

        measure_sid_string = self.get_measure_sid_string()
        c.sql["measure_conditions"] = c.sql["measure_conditions"].replace(
            "<params>", measure_sid_string)

        rows = d.run_query(c.sql["measure_conditions"])
        for row in rows:
            mc = MeasureCondition()
            mc.measure_sid = row[0]
            mc.condition_code = row[1]
            mc.condition_code_description = row[2]
            mc.certificate_type_code = row[3]
            mc.certificate_code = row[4]
            mc.document_code = row[5]
            mc.action_code = row[6]
            mc.action = row[7]
            mc.certificate_type_description = row[8]
            mc.component_sequence_number = row[9]
            mc.certificate_description = row[10]

            mc.get_requirement()
            self.measure_conditions.append(mc)
            if mc.condition_code == "V":
                self.meursing_code = True

    def get_measure_components(self):
        d = Database()
        c = Config()
        self.measure_components = []

        measure_sid_string = self.get_measure_sid_string()
        c.sql["measure_components"] = c.sql["measure_components"].replace(
            "<params>", measure_sid_string)
        rows = d.run_query(c.sql["measure_components"])
        for row in rows:
            mc = MeasureComponent()
            mc.measure_sid = row[0]
            mc.duty_expression_id = row[1]
            mc.duty_amount = c.mstr(row[2])
            mc.monetary_unit_code = c.mstr(row[3])
            mc.measurement_unit_code = row[4]
            mc.measurement_unit_qualifier_code = row[5]
            mc.duty_expression_description = row[6]
            mc.monetary_unit_description = row[7]
            mc.measurement_unit_description = row[8]
            mc.measurement_unit_qualifier_description = row[9]
            mc.get_duty_string()

            self.measure_components.append(mc)

    def get_commodity_footnotes(self):
        d = Database()
        c = Config()
        self.commodity_footnotes = []

        comm_code_string = self.get_comm_code_string()
        c.sql["commodity_footnotes"] = c.sql["commodity_footnotes"].replace(
            "<params>", comm_code_string)
        rows = d.run_query(c.sql["commodity_footnotes"])
        for row in rows:
            f = Footnote(row[0], row[1], row[2])
            self.commodity_footnotes.append(f.as_dict())

    def get_measure_exclusions(self):
        d = Database()
        c = Config()
        self.measure_exclusions = []

        measure_sid_string = self.get_measure_sid_string()
        c.sql["exclusions"] = c.sql["exclusions"].replace(
            "<params>", measure_sid_string)
        rows = d.run_query(c.sql["exclusions"])
        for row in rows:
            ga = GeographicalArea(row[0], row[1])
            ga.measure_sid = row[2]
            self.measure_exclusions.append(ga)

    def assign_measure_conditions(self):
        for mc in self.measure_conditions:
            for m in self.measures:
                if m.measure_sid == mc.measure_sid:
                    m.measure_conditions.append(mc.as_dict())
                    break

    def assign_measure_components(self):
        for mc in self.measure_components:
            for m in self.measures:
                if m.measure_sid == mc.measure_sid:
                    m.measure_components.append(mc.as_dict())
                    break

    def assign_measure_exclusions(self):
        for me in self.measure_exclusions:
            for m in self.measures:
                if m.measure_sid == me.measure_sid:
                    m.measure_exclusions.append(me.as_exclusion_dict())
                    break

    def get_section(self):
        d = Database()
        c = Config()
        # Get core data like the description
        params = [
            self.chapter.goods_nomenclature_sid
        ]
        rows = d.run_query(c.sql["section"], params)
        row = rows[0]
        section_position = row[0]
        section_title = row[1]
        s = Section(section_position, section_title)
        self.section = s.as_dict()

    def get_duty_expressions(self):
        print("Combining")
        for m in self.measures:
            m.combine_duties()
            if m.measure_type_id in ('103', '105'):
                self.basic_duty_rate = m.duty_expression.base

    def get_heading_json(self):
        if self.declarable:
            return self.get_commodity_json()

        results = collections.OrderedDict()

        if len(self.goods_nomenclature_item_id) != 10:
            return self.return_error()

        self.split_ancestors()
        self.get_section()

        # Get the stuff that does not need to be got from the database
        results["goods_nomenclature_item_id"] = self.goods_nomenclature_item_id
        results["description"] = self.description
        results["description_plain"] = self.description_plain
        results["formatted_description"] = self.formatted_description
        results["declarable"] = self.declarable
        results["bti_url"] = "http://ec.europa.eu/taxation_customs/dds2/ebti/ebti_consultation.jsp?Lang=en&nomenc=" + \
            self.goods_nomenclature_item_id + "&Expand=true"
        results["section"] = self.section
        results["commodities"] = self.descendants
        return results

    def get_descendant_parentage(self, default):
        descendant_count = len(self.descendants)
        if descendant_count > 0:
            for i in range(descendant_count - 1, -1, -1):
                descendant1 = self.descendants[i]
                for j in range(i - 1, -1, -1):
                    descendant2 = self.descendants[j]
                    if descendant2["number_indents"] < descendant1["number_indents"]:
                        descendant1["parent_sid"] = descendant2["goods_nomenclature_sid"]
                        break
                    # if descendant2.number_indents < descendant1.number_indents:
                    #     descendant1.parent_sid = descendant2.goods_nomenclature_sid
                    #     break

            for i in range(1, descendant_count):
                descendant1 = self.descendants[i - 1]
                descendant2 = self.descendants[i]
                descendant1["leaf"] = False if descendant2["number_indents"] > descendant1["number_indents"] else True
                # descendant1.leaf = False if descendant2.number_indents > descendant1.number_indents else True

    def get_geo_memberships(self):
        d = Database()
        c = Config()
        geo_memberships = []
        params = [
            self.date,
            self.date
        ]
        rows = d.run_query(c.sql["geo_memberships"], params)
        row_count = len(rows)
        if row_count < 1:
            return

        for row in rows:
            gam = GeoMembership(row[0], row[1], row[2])
            geo_memberships.append(gam)
        c.set_geo_memberships(geo_memberships)

    def get_measure_footnotes(self):
        d = Database()
        c = Config()
        self.measure_footnotes = []

        measure_sid_string = self.get_measure_sid_string()
        c.sql["measure_footnotes"] = c.sql["measure_footnotes"].replace(
            "<params>", measure_sid_string)

        rows = d.run_query(c.sql["measure_footnotes"])
        for row in rows:
            f = Footnote(row[0], row[1], row[2], row[3])
            self.measure_footnotes.append(f)

    def assign_measure_footnotes(self):
        for mf in self.measure_footnotes:
            for m in self.measures:
                if m.measure_sid == mf.measure_sid:
                    m.measure_footnotes.append(mf)
                    break
