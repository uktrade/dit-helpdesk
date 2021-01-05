import itertools
import logging

from django.conf import settings

from flags.state import flag_enabled

from commodities.helpers import (
    get_global_tariff_context,
    get_tariff_content_context,
    has_trade_scenario,
)
from regulations.models import RegulationGroup

from ..helpers import get_eu_commodity_link, get_nomenclature_group_measures
from ..models import Heading, SubHeading


logger = logging.getLogger(__name__)


class CommodityDetailSection:
    should_be_displayed = True

    def __init__(self, country, commodity_object):
        self.country = country
        self.commodity_object = commodity_object

    def get_menu_items(self):
        raise NotImplementedError("Implement `get_menu_items`")

    def get_modals_context_data(self):
        return []

    def get_context_data(self):
        return {}


class TariffsAndTaxesSection(CommodityDetailSection):
    template = "hierarchy/_tariffs_and_taxes.html"

    def __init__(self, country, commodity_object):
        super().__init__(country, commodity_object)

        self.tariffs, self.taxes = self._get_tariffs_and_taxes(commodity_object, country)

    def _get_tariffs_and_taxes(self, commodity_object, country):
        measures = get_nomenclature_group_measures(
            commodity_object,
            "Tariffs and charges",
            country.country_code,
            is_eu=country.is_eu,
        )

        tariffs = []
        taxes = []
        for measure in measures:
            if measure.vat or measure.excise:
                taxes.append(measure)
            else:
                tariffs.append(measure)

        return tariffs, taxes

    @property
    def should_be_displayed(self):
        return bool(self.taxes) or bool(self.tariffs)

    def get_menu_items(self):
        return [
            ("Tariffs and taxes", "tariffs_and_taxes"),
        ]

    def get_modals_context_data(self):
        return [
            measure_json.measures_modals
            for measure_json in itertools.chain(self.tariffs, self.taxes)
        ]

    def _get_table_data(self, measures, get_quotas_url, get_conditions_url):
        table_data = [
            measure_json.get_table_row(get_quotas_url, get_conditions_url)
            for measure_json in measures
        ]

        return table_data

    def get_context_data(self):
        ctx = super().get_context_data()

        def sort_tariffs_by_country_column(row):
            country_column = row[0]
            _, val = country_column

            return val

        def get_quotas_url(country_code, measure_id, order_number):
            return self.commodity_object.get_quotas_url(country_code, measure_id, order_number)

        def get_conditions_url(country_code, measure_id):
            return self.commodity_object.get_conditions_url(country_code, measure_id)

        tariffs_table_data = sorted(
            self._get_table_data(self.tariffs, get_quotas_url, get_conditions_url),
            key=sort_tariffs_by_country_column,
        )
        ctx["tariffs_table_data"] = tariffs_table_data
        ctx["taxes_table_data"] = self._get_table_data(self.taxes, get_quotas_url, get_conditions_url)
        ctx["has_multiple_vat_entries"] = len([t for t in self.taxes if t.vat]) > 1

        if flag_enabled("PRE21"):
            ctx["global_tariff_data"] = get_global_tariff_context(self.commodity_object)

        return ctx


class UKGTTariffsAndTaxesSection(TariffsAndTaxesSection):
    template = "hierarchy/_tariffs_and_taxes_ukgt.html"


class BaseTariffsAndTaxesNorthernIrelandSection(TariffsAndTaxesSection):
    template = "hierarchy/_tariffs_and_taxes_northern_ireland.html"

    def __init__(self, country, commodity_object):
        super().__init__(country, commodity_object)

        eu_commodity_object = self.get_eu_commodity_object(commodity_object)
        self.eu_tariffs, _ = self._get_tariffs_and_taxes(eu_commodity_object, country)

    def get_eu_commodity_object(self, commodity_object):
        raise NotImplementedError("Implement `get_eu_commodity_object`")

    def _get_meursing_calculator_link(self, commodity_object):
        commodity_code = commodity_object.commodity_code

        return f"https://ec.europa.eu/taxation_customs/dds2/taric/measures.jsp?Lang=en&SimDate=20201208&Taric={commodity_code}&LangDescr=en"

    def _get_is_meursing_code(self, commodity_object):
        return commodity_object.tts_obj.is_meursing_code

    def get_modals_context_data(self):
        modals_context_data = super().get_modals_context_data()

        return modals_context_data + [
            measure_json.measures_modals
            for measure_json in self.eu_tariffs
        ]

    def get_context_data(self):
        ctx = super().get_context_data()

        def get_quotas_url(country_code, measure_id, order_number):
            return self.commodity_object.get_northern_ireland_quotas_url(country_code, measure_id, order_number)

        def get_conditions_url(country_code, measure_id):
            return self.commodity_object.get_northern_ireland_conditions_url(country_code, measure_id)            

        ctx["eu_tariffs_and_taxes_table_data"] = self._get_table_data(
            self.eu_tariffs,
            get_quotas_url,
            get_conditions_url,
        )
        ctx["is_meursing_code"] = self._get_is_meursing_code(self.commodity_object)
        ctx["meursing_calculator_link"] = self._get_meursing_calculator_link(self.commodity_object)

        return ctx


class HeadingEUCommodityObjectMixin:
    def get_eu_commodity_object(self, commodity_object):
        return Heading.objects.for_region(
            settings.SECONDARY_REGION,
        ).get(
            heading_code=commodity_object.heading_code,
            goods_nomenclature_sid=commodity_object.goods_nomenclature_sid,
        )


class SubHeadingEUCommodityObjectMixin:
    def get_eu_commodity_object(self, commodity_object):
        return SubHeading.objects.for_region(
            settings.SECONDARY_REGION,
        ).get(
            commodity_code=commodity_object.commodity_code,
            goods_nomenclature_sid=commodity_object.goods_nomenclature_sid,
        )


class HeadingTariffsAndTaxesNorthernIrelandSection(HeadingEUCommodityObjectMixin, BaseTariffsAndTaxesNorthernIrelandSection):
    pass


class SubHeadingTariffsAndTaxesNorthernIrelandSection(SubHeadingEUCommodityObjectMixin, BaseTariffsAndTaxesNorthernIrelandSection):
    pass


class QuotasSection(CommodityDetailSection):
    template = "hierarchy/_quotas.html"

    def __init__(self, country, commodity_object):
        super().__init__(country, commodity_object)

        self.has_quotas_measures = True

        self.quotas_measures = get_nomenclature_group_measures(
            self.commodity_object,
            "Quotas",
            self.country.country_code,
            is_eu=country.is_eu,
        )

        def get_quotas_url(country_code, measure_id, order_number):
            return self.commodity_object.get_quotas_url(country_code, measure_id, order_number)

        def get_conditions_url(country_code, measure_id):
            return self.commodity_object.get_conditions_url(country_code, measure_id)

        self.quotas_table_data = self._get_table_data(
            self.quotas_measures,
            get_quotas_url,
            get_conditions_url,
        )

    @property
    def should_be_displayed(self):
        return self.has_quotas_measures and bool(self.quotas_measures)

    def get_menu_items(self):
        return [
            ("Quotas", "quotas"),
        ]

    def get_modals_context_data(self):
        return [
            measure_json.measures_modals
            for measure_json in self.quotas_measures
        ]

    def _get_table_data(self, quotas_measures, get_quotas_url, get_conditions_url):
        return [
            measure_json.get_table_row(get_quotas_url, get_conditions_url)
            for measure_json in quotas_measures
        ]

    def get_context_data(self):
        ctx = super().get_context_data()

        ctx["quotas_table_data"] = self.quotas_table_data

        return ctx


class QuotasNorthernIrelandSection(QuotasSection):
    template = "hierarchy/_quotas_northern_ireland.html"


class OtherMeasuresSection(CommodityDetailSection):
    template = "hierarchy/_other_measures.html"

    def __init__(self, country, commodity_object):
        super().__init__(country, commodity_object)

        self.has_other_measures = True

        self.other_measures = get_nomenclature_group_measures(
            commodity_object,
            "Other measures",
            country.country_code,
            is_eu=country.is_eu,
        )

        def get_quotas_url(country_code, measure_id, order_number):
            return commodity_object.get_quotas_url(country_code, measure_id, order_number)

        def get_conditions_url(country_code, measure_id):
            return commodity_object.get_conditions_url(country_code, measure_id)

        self.other_measures_table_data = [
            measure_json.get_table_row(get_quotas_url, get_conditions_url)
            for measure_json in self.other_measures
        ]

    @property
    def should_be_displayed(self):
        return self.has_other_measures and bool(self.other_measures)

    def get_menu_items(self):
        return [("Other measures", "other_measures")]

    def get_modals_context_data(self):
        return [
            measure_json.measures_modals
            for measure_json in self.other_measures
        ]

    def get_context_data(self):
        ctx = super().get_context_data()

        ctx["other_measures_table"] = self.other_measures_table_data

        return ctx


class BaseOtherMeasuresNorthernIrelandSection(OtherMeasuresSection):
    template = "hierarchy/_other_measures_northern_ireland.html"

    def __init__(self, country, commodity_object):
        super().__init__(country, commodity_object)

        eu_commodity_object = self.get_eu_commodity_object(commodity_object)
        self.eu_other_measures = get_nomenclature_group_measures(
            eu_commodity_object,
            "Other measures",
            country.country_code,
            is_eu=country.is_eu
        )

        def get_quotas_url(country_code, measure_id, order_number):
            return eu_commodity_object.get_northern_ireland_quotas_url(country_code, measure_id, order_number)

        def get_conditions_url(country_code, measure_id):
            return eu_commodity_object.get_northern_ireland_conditions_url(country_code, measure_id)

        self.eu_other_measures_table_data = [
            measure_json.get_table_row(get_quotas_url, get_conditions_url)
            for measure_json in self.eu_other_measures]

    def get_eu_commodity_object(self, commodity_object):
        raise NotImplementedError("Implement `get_eu_commodity_object`")

    def get_modals_context_data(self):
        modals_context_data = super().get_modals_context_data()

        return modals_context_data + [
            measure_json.measures_modals
            for measure_json in self.eu_other_measures
        ]

    def get_context_data(self):
        ctx = super().get_context_data()

        ctx["eu_other_measures_link"] = get_eu_commodity_link(self.commodity_object, self.country)
        ctx["eu_other_measures_table"] = self.eu_other_measures_table_data

        return ctx


class HeadingOtherMeasuresNorthernIrelandSection(HeadingEUCommodityObjectMixin, BaseOtherMeasuresNorthernIrelandSection):
    pass


class SubHeadingOtherMeasuresNorthernIrelandSection(SubHeadingEUCommodityObjectMixin, BaseOtherMeasuresNorthernIrelandSection):
    pass


class RulesOfOriginSection(CommodityDetailSection):
    template = "hierarchy/_rules_of_origin.html"

    def __init__(self, country, commodity_object):
        super().__init__(country, commodity_object)

        self.rules_of_origin = commodity_object.get_rules_of_origin(
            country_code=country.country_code,
        )

    @property
    def should_be_displayed(self):
        return True

    def get_menu_items(self):
        return [("Rules of origin", "rules_of_origin")]

    def get_has_gsp_tariff_preference(self, country, commodity_object):
        measures = get_nomenclature_group_measures(
            commodity_object,
            "Tariffs and charges",
            country.country_code,
        )

        return any(m.is_gsp for m in measures)

    def get_context_data(self):
        ctx = super().get_context_data()

        ctx["rules_of_origin"] = self.rules_of_origin
        ctx["has_uk_trade_agreement"] = self.country.has_uk_trade_agreement
        ctx["has_gsp_tariff_preference"] = self.get_has_gsp_tariff_preference(
            self.country, self.commodity_object,
        )

        return ctx


class RulesOfOriginNorthernIrelandSection(RulesOfOriginSection):
    template = "hierarchy/_rules_of_origin_northern_ireland.html"

    def get_context_data(self):
        ctx = super().get_context_data()

        commodity_object = self.commodity_object
        country = self.country

        ctx["eu_rules_of_origin_link"] = get_eu_commodity_link(commodity_object, country)
        ctx["has_eu_trade_agreement"] = country.has_eu_trade_agreement
        ctx["has_both_trade_agreements"] = country.has_uk_trade_agreement and country.has_eu_trade_agreement

        return ctx


class ProductRegulationsSection(CommodityDetailSection):
    template = "hierarchy/_product_regulations.html"

    def __init__(self, country, commodity_object):
        super().__init__(country, commodity_object)

        self.regulation_groups = RegulationGroup.objects.inherited(commodity_object)

    @property
    def should_be_displayed(self):
        return self.regulation_groups.exists()

    def get_menu_items(self):
        return [("Product-specific regulations", "regulations")]

    def get_context_data(self):
        ctx = super().get_context_data()

        ctx["regulation_groups"] = self.regulation_groups.order_by('title')

        return ctx


class ProductRegulationsNorthernIrelandSection(CommodityDetailSection):
    should_be_displayed = True
    template = "hierarchy/_product_regulations_northern_ireland.html"

    def get_menu_items(self):
        return [("Product-specific regulations", "regulations")]

    def get_context_data(self):
        return {
            "eu_regulations_link": get_eu_commodity_link(self.commodity_object, self.country),
        }


class TradeStatusSection(CommodityDetailSection):
    template = "hierarchy/_trade_status.html"

    @property
    def should_be_displayed(self):
        return has_trade_scenario(self.country)

    def get_menu_items(self):
        return [("Trade status", "trade_status")]

    def get_context_data(self):
        return get_tariff_content_context(self.country, self.commodity_object)
