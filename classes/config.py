class Config(object):
    geo_memberships = []

    def __init__(self):
        self.excluded_measure_types = ["440", "441", "442"]
        self.sql = {}
        self.get_sql()

    @classmethod
    def set_geo_memberships(cls, geo_memberships):
        cls.geo_memberships = geo_memberships

    def get_sql(self):
        # Gets the ancestors of a commodity code - the last item in the list is the actual commodity
        self.sql["ancestors"] = """
        SELECT gn.goods_nomenclature_sid, gn.goods_nomenclature_item_id, gn.producline_suffix, 
        description,
        gni.number_indents, (gn.goods_nomenclature_item_id || gn.producline_suffix) as commcode_plus_suffix 
        FROM goods_nomenclatures gn
        JOIN goods_nomenclature_descriptions gnd ON gnd.goods_nomenclature_sid = gn.goods_nomenclature_sid
        JOIN goods_nomenclature_description_periods gndp ON gndp.goods_nomenclature_description_period_sid = gnd.goods_nomenclature_description_period_sid
        JOIN goods_nomenclature_indents gni ON gni.goods_nomenclature_sid = gn.goods_nomenclature_sid
        WHERE (gn.validity_end_date IS NULL OR gn.validity_end_date >= %s)
        AND gndp.goods_nomenclature_description_period_sid IN
        (
            SELECT MAX (gndp2.goods_nomenclature_description_period_sid)
            FROM goods_nomenclature_description_periods gndp2
            WHERE gndp2.goods_nomenclature_sid = gnd.goods_nomenclature_sid
            AND gndp2.validity_start_date <= %s
        )
        AND gni.goods_nomenclature_indent_sid IN
        (
            SELECT MAX (gni2.goods_nomenclature_indent_sid)
            FROM goods_nomenclature_indents gni2
            WHERE gni2.goods_nomenclature_sid = gn.goods_nomenclature_sid
            AND gni2.validity_start_date <= %s
        )
        and left(gn.goods_nomenclature_item_id, 2) = %s
        and gn.goods_nomenclature_item_id <= %s
        order by gn.goods_nomenclature_item_id desc, gn.producline_suffix desc
        """

        # Gets the descendants of a heading - the heading is the first in the list
        self.sql["descendants"] = """
        SELECT gn.goods_nomenclature_sid, gn.goods_nomenclature_item_id, gn.producline_suffix, 
        description,
        gni.number_indents, (gn.goods_nomenclature_item_id || gn.producline_suffix) as commcode_plus_suffix 
        FROM goods_nomenclatures gn
        JOIN goods_nomenclature_descriptions gnd ON gnd.goods_nomenclature_sid = gn.goods_nomenclature_sid
        JOIN goods_nomenclature_description_periods gndp ON gndp.goods_nomenclature_description_period_sid = gnd.goods_nomenclature_description_period_sid
        JOIN goods_nomenclature_indents gni ON gni.goods_nomenclature_sid = gn.goods_nomenclature_sid
        WHERE (gn.validity_end_date IS NULL OR gn.validity_end_date >= %s)
        AND gndp.goods_nomenclature_description_period_sid IN
        (
            SELECT MAX (gndp2.goods_nomenclature_description_period_sid)
            FROM goods_nomenclature_description_periods gndp2
            WHERE gndp2.goods_nomenclature_sid = gnd.goods_nomenclature_sid
            AND gndp2.validity_start_date <= %s
        )
        AND gni.goods_nomenclature_indent_sid IN
        (
            SELECT MAX (gni2.goods_nomenclature_indent_sid)
            FROM goods_nomenclature_indents gni2
            WHERE gni2.goods_nomenclature_sid = gn.goods_nomenclature_sid
            AND gni2.validity_start_date <= %s
        )
        and left(gn.goods_nomenclature_item_id, 4) = %s
        and gn.goods_nomenclature_item_id || gn.producline_suffix >= %s
        order by gn.goods_nomenclature_item_id asc, gn.producline_suffix asc
        """

        # Gets all the measures for the given commodity code
        self.sql["measures"] = """
        with cte_m as (
            SELECT m.measure_sid,
            m.goods_nomenclature_item_id,
            m.geographical_area_id,
            m.measure_type_id,
            mtd.description as measure_type_description,
            mt.trade_movement_code,
            mt.measure_type_series_id,
            m.measure_generating_regulation_id,
            m.ordernumber,
            m.additional_code_type_id,
            m.additional_code_id,
            m.additional_code_type_id || m.additional_code_id::text AS additional_code,
            m.geographical_area_sid,
            m.goods_nomenclature_sid,
            m.additional_code_sid,
            to_char(m.validity_start_date, 'YYYY-MM-DD'::text) AS effective_start_date,
            LEAST(to_char(m.validity_end_date, 'YYYY-MM-DD'::text), to_char(r.validity_end_date, 'YYYY-MM-DD'::text), to_char(r.effective_end_date, 'YYYY-MM-DD'::text)) AS effective_end_date,
            r.officialjournal_number, r.officialjournal_page, r.published_date, r.validity_start_date, r.validity_end_date,
            m.reduction_indicator
            FROM measures m, base_regulations r, measure_type_descriptions mtd, measure_types mt
            WHERE m.measure_generating_regulation_id::text = r.base_regulation_id::text
            and m.measure_type_id = mt.measure_type_id 
            and m.measure_type_id = mtd.measure_type_id 
            and m.goods_nomenclature_item_id in (<params>)

            UNION

            SELECT m.measure_sid,
            m.goods_nomenclature_item_id,
            m.geographical_area_id,
            m.measure_type_id,
            mtd.description as measure_type_description,
            mt.trade_movement_code,
            mt.measure_type_series_id,
            m.measure_generating_regulation_id,
            m.ordernumber,
            m.additional_code_type_id,
            m.additional_code_id,
            m.additional_code_type_id || m.additional_code_id::text AS additional_code,
            m.geographical_area_sid,
            m.goods_nomenclature_sid,
            m.additional_code_sid,
            to_char(m.validity_start_date, 'YYYY-MM-DD'::text) AS effective_start_date,
            LEAST(to_char(m.validity_end_date, 'YYYY-MM-DD'::text), to_char(r.validity_end_date, 'YYYY-MM-DD'::text), to_char(r.effective_end_date, 'YYYY-MM-DD'::text)) AS effective_end_date,
            r.officialjournal_number, r.officialjournal_page, r.published_date, r.validity_start_date, r.validity_end_date,
            m.reduction_indicator
            FROM measures m, modification_regulations r, measure_type_descriptions mtd, measure_types mt
            WHERE m.measure_generating_regulation_id::text = r.modification_regulation_id::text
            and m.measure_type_id = mt.measure_type_id 
            and m.measure_type_id = mtd.measure_type_id 
            and m.goods_nomenclature_item_id in (<params>)
        ),
        cte_g as (
            SELECT g.geographical_area_sid,
            g.parent_geographical_area_group_sid,
            geo1.geographical_area_id,
            geo1.description as geographical_area_description,
            g.geographical_code
            FROM geographical_area_descriptions geo1,
            geographical_areas g
            WHERE g.geographical_area_id::text = geo1.geographical_area_id::text AND (geo1.geographical_area_description_period_sid IN ( SELECT max(geo2.geographical_area_description_period_sid) AS max
            FROM geographical_area_descriptions geo2
            WHERE geo1.geographical_area_id::text = geo2.geographical_area_id::text))
            ORDER BY geo1.geographical_area_id
        )
        select cte_m.*, geographical_area_description
        from cte_m, cte_g
        where cte_m.geographical_area_id = cte_g.geographical_area_id
        and (cte_m.effective_end_date is null or cte_m.effective_end_date > '<date>')
        and cte_m.effective_start_date <= '<date>'
        """

        # Gets all the measures for the given commodity code
        self.sql["meursing_measures"] = """
        with cte_m as (
            SELECT m.measure_sid,
            m.goods_nomenclature_item_id,
            m.geographical_area_id,
            m.measure_type_id,
            mtd.description as measure_type_description,
            mt.trade_movement_code,
            mt.measure_type_series_id,
            m.measure_generating_regulation_id,
            m.ordernumber,
            m.additional_code_type_id,
            m.additional_code_id,
            m.additional_code_type_id || m.additional_code_id::text AS additional_code,
            m.geographical_area_sid,
            m.goods_nomenclature_sid,
            m.additional_code_sid,
            to_char(m.validity_start_date, 'YYYY-MM-DD'::text) AS effective_start_date,
            LEAST(to_char(m.validity_end_date, 'YYYY-MM-DD'::text), to_char(r.validity_end_date, 'YYYY-MM-DD'::text), to_char(r.effective_end_date, 'YYYY-MM-DD'::text)) AS effective_end_date,
            r.officialjournal_number, r.officialjournal_page, r.published_date, r.validity_start_date, r.validity_end_date,
            m.reduction_indicator
            FROM measures m, base_regulations r, measure_type_descriptions mtd, measure_types mt
            WHERE m.measure_generating_regulation_id::text = r.base_regulation_id::text
            and m.measure_type_id = mt.measure_type_id 
            and m.measure_type_id = mtd.measure_type_id 
            and m.goods_nomenclature_item_id is null
            and m.measure_type_id in ('672', '673', '674')
	        and m.additional_code_id = %s

            UNION

            SELECT m.measure_sid,
            m.goods_nomenclature_item_id,
            m.geographical_area_id,
            m.measure_type_id,
            mtd.description as measure_type_description,
            mt.trade_movement_code,
            mt.measure_type_series_id,
            m.measure_generating_regulation_id,
            m.ordernumber,
            m.additional_code_type_id,
            m.additional_code_id,
            m.additional_code_type_id || m.additional_code_id::text AS additional_code,
            m.geographical_area_sid,
            m.goods_nomenclature_sid,
            m.additional_code_sid,
            to_char(m.validity_start_date, 'YYYY-MM-DD'::text) AS effective_start_date,
            LEAST(to_char(m.validity_end_date, 'YYYY-MM-DD'::text), to_char(r.validity_end_date, 'YYYY-MM-DD'::text), to_char(r.effective_end_date, 'YYYY-MM-DD'::text)) AS effective_end_date,
            r.officialjournal_number, r.officialjournal_page, r.published_date, r.validity_start_date, r.validity_end_date,
            m.reduction_indicator
            FROM measures m, modification_regulations r, measure_type_descriptions mtd, measure_types mt
            WHERE m.measure_generating_regulation_id::text = r.modification_regulation_id::text
            and m.measure_type_id = mt.measure_type_id 
            and m.measure_type_id = mtd.measure_type_id 
            and m.goods_nomenclature_item_id is null
            and m.measure_type_id in ('672', '673', '674')
	        and m.additional_code_id = %s
        ),
        cte_g as (
            SELECT g.geographical_area_sid,
            g.parent_geographical_area_group_sid,
            geo1.geographical_area_id,
            geo1.description as geographical_area_description,
            g.geographical_code
            FROM geographical_area_descriptions geo1,
            geographical_areas g
            WHERE g.geographical_area_id::text = geo1.geographical_area_id::text AND (geo1.geographical_area_description_period_sid IN ( SELECT max(geo2.geographical_area_description_period_sid) AS max
            FROM geographical_area_descriptions geo2
            WHERE geo1.geographical_area_id::text = geo2.geographical_area_id::text))
            ORDER BY geo1.geographical_area_id
        ),
        cte_mem as (
        	select geographical_area_group_sid
			       from geographical_area_memberships gam, geographical_areas ga2 
        	where gam.geographical_area_sid = ga2.geographical_area_sid 
        	and gam.validity_end_date is null
        	and ga2.geographical_area_id = %s
        )
        select cte_m.*, geographical_area_description
        from cte_m, cte_g
        where cte_m.geographical_area_id = cte_g.geographical_area_id
        and (cte_m.effective_end_date is null or cte_m.effective_end_date > %s)
        and cte_m.effective_start_date <= %s
        and
        (
            cte_m.geographical_area_id = %s
            or cte_m.geographical_area_sid in (
                select geographical_area_group_sid
                from cte_mem
            )
        )
        """

        self.sql["measure_conditions"] = """
        with cte_mc as (
            select mc.measure_sid, mc.condition_code, mccd.description as condition_code_description,
            coalesce(mc.certificate_type_code, '') as certificate_type_code,
            coalesce(mc.certificate_code, '') as certificate_code,
            coalesce(mc.certificate_type_code, '') || coalesce(mc.certificate_code, '') as document_code,
            mad.action_code as action_code,
            mad.description as action,
            coalesce(ctd.description, '') as certificate_type_description,
            component_sequence_number 
            from measure_condition_code_descriptions mccd, measure_action_descriptions mad,
            measure_conditions mc left outer join certificate_type_descriptions ctd on mc.certificate_type_code = ctd.certificate_type_code 
            where mc.condition_code = mccd.condition_code
            and mad.action_code = mc.action_code 
            and mc.measure_sid in (<params>)
        ), cte_c as (
            SELECT cd1.certificate_type_code,
            cd1.certificate_code,
            coalesce(cd1.certificate_type_code, '') || coalesce(cd1.certificate_code, '') AS document_code,
            cd1.description
            FROM certificate_descriptions cd1,
            certificates c
            WHERE c.certificate_code::text = cd1.certificate_code::text AND c.certificate_type_code::text = cd1.certificate_type_code::text AND (cd1.oid IN ( SELECT max(cd2.oid) AS max
            FROM certificate_descriptions cd2
            WHERE cd1.certificate_type_code::text = cd2.certificate_type_code::text AND cd1.certificate_code::text = cd2.certificate_code::text))
            ORDER BY cd1.certificate_type_code
        )
        select cte_mc.*, coalesce(cte_c.description, '') as certificate_description
        from cte_mc left outer join cte_c on cte_mc.document_code = cte_c.document_code
        order by cte_mc.measure_sid, cte_mc.component_sequence_number
        """

        self.sql["measure_components"] = """
        select mc.measure_sid, mc.duty_expression_id, mc.duty_amount,
        mc.monetary_unit_code,mc.measurement_unit_code, mc.measurement_unit_qualifier_code,
        ded.description as duty_expression_description,
        mud.description as monetary_unit_description,
        mud2.description as measurement_unit_description,
        muqd.description as measurement_unit_qualifier_description
        from duty_expression_descriptions ded, measure_components mc
        left outer join monetary_unit_descriptions mud on mc.monetary_unit_code = mud.monetary_unit_code 
        left outer join measurement_unit_descriptions mud2 on mc.measurement_unit_code = mud2.measurement_unit_code 
        left outer join measurement_unit_qualifier_descriptions muqd on mc.measurement_unit_qualifier_code = muqd.measurement_unit_qualifier_code 
        where mc.duty_expression_id = ded.duty_expression_id 
        and mc.measure_sid in (<params>)
        """

        self.sql["exclusions"] = """
        with cte_g as (
            SELECT g.geographical_area_sid,
                g.parent_geographical_area_group_sid,
                geo1.geographical_area_id,
                geo1.description,
                g.geographical_code,
                g.validity_start_date,
                g.validity_end_date
            FROM geographical_area_descriptions geo1,
                geographical_areas g
            WHERE g.geographical_area_id::text = geo1.geographical_area_id::text AND (geo1.geographical_area_description_period_sid IN ( SELECT max(geo2.geographical_area_description_period_sid) AS max
                    FROM geographical_area_descriptions geo2
                    WHERE geo1.geographical_area_id::text = geo2.geographical_area_id::text))
            ORDER BY geo1.geographical_area_id
        )
        select mega.excluded_geographical_area, cte_g.description, mega.measure_sid 
        from measure_excluded_geographical_areas mega, cte_g
        where cte_g.geographical_area_sid = mega.geographical_area_sid 
        and mega.measure_sid in (<params>)
        order by 1
        """

        self.sql["measure_footnotes"] = """
        with cte_f as (
        SELECT ft1.footnote_type_id,
            ft1.footnote_id,
            ft1.description,
            f1.validity_start_date,
            f1.validity_end_date
        FROM footnote_descriptions ft1,
            footnotes f1
        WHERE ft1.footnote_id::text = f1.footnote_id::text AND ft1.footnote_type_id::text = f1.footnote_type_id::text AND (ft1.footnote_description_period_sid IN ( SELECT max(ft2.footnote_description_period_sid) AS max
                FROM footnote_descriptions ft2
                WHERE ft1.footnote_type_id::text = ft2.footnote_type_id::text AND ft1.footnote_id::text = ft2.footnote_id::text))
        ORDER BY ft1.footnote_type_id, ft1.footnote_id
        )
        select fam.footnote_type_id, fam.footnote_id, f.description, fam.measure_sid
        from footnote_association_measures fam, cte_f f
        where f.footnote_type_id = fam.footnote_type_id
        and f.footnote_id = fam.footnote_id
        and fam.measure_sid in (<params>)
        order by 4, 1, 2
        """

        self.sql["section"] = """
        select s.position, s.title 
        from sections s, chapters_sections cs 
        where cs.section_id = s.id
        and cs.goods_nomenclature_sid = %s
        """

        self.sql["geo_memberships"] = """
        with cte_g as (
            SELECT g.geographical_area_sid,
                g.parent_geographical_area_group_sid,
                geo1.geographical_area_id,
                geo1.description,
                g.geographical_code
            FROM geographical_area_descriptions geo1,
                geographical_areas g
            WHERE g.geographical_area_id::text = geo1.geographical_area_id::text AND (geo1.geographical_area_description_period_sid IN ( SELECT max(geo2.geographical_area_description_period_sid) AS max
                    FROM geographical_area_descriptions geo2
                    WHERE geo1.geographical_area_id::text = geo2.geographical_area_id::text))
            ORDER BY geo1.geographical_area_id
        )
        select gam.geographical_area_group_sid, cte_g.geographical_area_id, cte_g.description
        from geographical_area_memberships gam, cte_g
        where gam.geographical_area_sid = cte_g.geographical_area_sid
        and (gam.validity_end_date is null or gam.validity_end_date > %s)
        and gam.validity_start_date <= %s
        order by 1, 2
        """

        self.sql["commodity_footnotes"] = """
        with cte_f as (
        SELECT ft1.footnote_type_id,
            ft1.footnote_id,
            ft1.description,
            f1.validity_start_date,
            f1.validity_end_date
        FROM footnote_descriptions ft1,
            footnotes f1
        WHERE ft1.footnote_id::text = f1.footnote_id::text AND ft1.footnote_type_id::text = f1.footnote_type_id::text AND (ft1.footnote_description_period_sid IN ( SELECT max(ft2.footnote_description_period_sid) AS max
                FROM footnote_descriptions ft2
                WHERE ft1.footnote_type_id::text = ft2.footnote_type_id::text AND ft1.footnote_id::text = ft2.footnote_id::text))
        ORDER BY ft1.footnote_type_id, ft1.footnote_id
        )
        select f.footnote_type_id, f.footnote_id, f.description
        from cte_f f, footnote_association_goods_nomenclatures fagn
        where fagn.footnote_id = f.footnote_id 
        and fagn.footnote_type = f.footnote_type_id 
        and fagn.goods_nomenclature_item_id in (<params>)
        """


    @staticmethod
    def mstr(v):
        if v is None:
            return ""
        else:
            return v