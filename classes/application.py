# Import custom libraries
from classes.goods_nomenclature import GoodsNomenclature
from classes.measure_type import MeasureType
from classes.measure_type_series import MeasureTypeSeries
from classes.certificate_type import CertificateType
from classes.additional_code_type import AdditionalCodeType
from classes.additional_code import AdditionalCode
from classes.footnote_type import FootnoteType
from classes.database import Database


class Application(object):
    def __init__(self):
        print("Init application class")

    @staticmethod
    def get_measure_types():
        d = Database()
        measure_types = []
        sql = """select mt.measure_type_id, mtd.description,
        mts.measure_type_series_id, mtsd.description 
        from measure_type_series mts, measure_type_series_descriptions mtsd, measure_types mt, measure_type_descriptions mtd 
        where mts.measure_type_series_id = mtsd.measure_type_series_id 
        and mt.measure_type_id = mtd.measure_type_id 
        and mt.measure_type_series_id = mts.measure_type_series_id 
        and mts.validity_end_date is null
        and mt.validity_end_date is null
        order by 1;"""
        rows = d.run_query(sql)
        for row in rows:
            obj = MeasureType(row[0], row[1])
            obj.measure_type_series_id = row[2]
            obj.measure_type_series_description = row[3]
            measure_types.append(obj.as_dict())

        return measure_types

    @staticmethod
    def get_measure_type_series():
        d = Database()
        measure_type_series = []
        sql = """select mts.measure_type_series_id, mts.measure_type_combination, mtsd.description 
        from measure_type_series mts, measure_type_series_descriptions mtsd 
        where mts.measure_type_series_id = mtsd.measure_type_series_id 
        and mts.validity_end_date is null order by 1;"""
        rows = d.run_query(sql)
        for row in rows:
            obj = MeasureTypeSeries(row[0], row[1], row[2])
            measure_type_series.append(obj.as_dict())

        return measure_type_series

    @staticmethod
    def get_certificate_types():
        d = Database()
        certificate_types = []
        sql = """select ct.certificate_type_code, ctd.description
        from certificate_types ct, certificate_type_descriptions ctd
        where ct.certificate_type_code = ctd.certificate_type_code
        and ct.validity_end_date is null
        order by 1"""
        rows = d.run_query(sql)
        for row in rows:
            obj = CertificateType(row[0], row[1])
            certificate_types.append(obj.as_dict())

        return certificate_types

    @staticmethod
    def get_additional_code_types():
        d = Database()
        additional_code_types = []
        sql = """select act.additional_code_type_id, act.application_code,
        actd.description 
        from additional_code_types act, additional_code_type_descriptions actd 
        where act.additional_code_type_id = actd.additional_code_type_id 
        and act.validity_end_date is null
        order by 1;"""
        rows = d.run_query(sql)
        for row in rows:
            obj = AdditionalCodeType(row[0], row[1], row[2])
            additional_code_types.append(obj.as_dict())

        return additional_code_types

    @staticmethod
    def get_footnote_types():
        d = Database()
        footnote_types = []
        sql = """select ft.footnote_type_id, application_code, description
        from footnote_types ft, footnote_type_descriptions ftd
        where ft.footnote_type_id = ftd.footnote_type_id 
        and ft.validity_end_date is null
        order by 1"""
        rows = d.run_query(sql)
        for row in rows:
            obj = FootnoteType(row[0], row[1], row[2])
            footnote_types.append(obj.as_dict())
        return footnote_types

    @staticmethod
    def get_meursing_measures(additional_code_id, geographical_area_id):
        d = Database()
        gn = GoodsNomenclature("", additional_code_id, geographical_area_id)
        gn.get_measures()
        gn.get_measure_components()
        gn.assign_measure_components()
        gn.get_duty_expressions()
        gn.assign_meursing_measures()
        return gn.meursing_measures

    @staticmethod
    def get_meursing_codes():
        d = Database()
        additional_codes = []
        sql = """select additional_code from meursing_additional_codes mac
        where validity_end_date is null
        order by 1"""
        rows = d.run_query(sql)
        for row in rows:
            obj = AdditionalCode("7", row[0], "")
            additional_codes.append(obj.as_dict())
        return additional_codes

    @staticmethod
    def get_meursing_code_list():
        d = Database()
        additional_codes = []
        sql = """select additional_code from meursing_additional_codes mac
        where validity_end_date is null order by 1"""
        rows = d.run_query(sql)
        for row in rows:
            additional_codes.append(row[0])
        return additional_codes

