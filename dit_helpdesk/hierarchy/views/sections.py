import itertools
import logging

from django.conf import settings

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

    def _get_table_data(self, measures):
        table_data = [
            measure_json.get_table_row()
            for measure_json in measures
        ]

        return table_data

    def get_context_data(self):
        ctx = super().get_context_data()

        ctx["tariffs_table_data"] = self._get_table_data(self.tariffs)
        ctx["taxes_table_data"] = self._get_table_data(self.taxes)
        ctx["has_multiple_vat_entries"] = len([t for t in self.taxes if t.vat]) > 1

        if settings.UKGT_ENABLED:
            ctx["global_tariff_data"] = get_global_tariff_context(self.commodity_object)

        return ctx


class UKGTTariffsAndTaxesSection(TariffsAndTaxesSection):
    template = "hierarchy/_tariffs_and_taxes_ukgt.html"


class BaseTariffsAndTaxesNorthernIrelandSection(TariffsAndTaxesSection):
    template = "hierarchy/_tariffs_and_taxes_northern_ireland.html"

    def __init__(self, country, commodity_object):
        super().__init__(country, commodity_object)

        eu_commodity_object = self.get_eu_commodity_object(commodity_object)
        self.eu_tariffs, self.eu_taxes = self._get_tariffs_and_taxes(eu_commodity_object, country)

    def get_eu_commodity_object(self, commodity_object):
        raise NotImplementedError("Implement `get_eu_commodity_object`")

    def get_context_data(self):
        ctx = super().get_context_data()

        ctx["eu_tariffs_and_taxes_table_data"] = self._get_table_data(itertools.chain(self.eu_tariffs, self.eu_taxes))

        return ctx


class QuotasSection(CommodityDetailSection):
    template = "hierarchy/_quotas.html"

    def __init__(self, country, commodity_object):
        super().__init__(country, commodity_object)

        self.has_quotas_measures = True

        self.quotas_measures = get_nomenclature_group_measures(
            self.commodity_object,
            "Quotas",
            self.country.country_code,
        )

        try:
            self.quotas_table_data = self._get_table_data(self.quotas_measures)
        except Exception as exc:
            self.has_quotas_measures = False
            logger.error("Quotas error", exc_info=exc)

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

    def _get_table_data(self, quotas_measures):
        return [
            measure_json.get_table_row() for measure_json in quotas_measures
        ]

    def get_context_data(self):
        ctx = super().get_context_data()

        ctx["quotas_table_data"] = self.quotas_table_data

        return ctx


class QuotasNorthernIrelandSection(QuotasSection):
    template = "hierarchy/_quotas_northern_ireland.html"

    def get_context_data(self):
        ctx = super().get_context_data()

        ctx["eu_quotas_link"] = get_eu_commodity_link(self.commodity_object, self.country)

        return ctx


class OtherMeasuresSection(CommodityDetailSection):
    template = "hierarchy/_other_measures.html"

    def __init__(self, country, commodity_object):
        super().__init__(country, commodity_object)

        self.has_other_measures = True

        self.other_measures = get_nomenclature_group_measures(
            commodity_object,
            "Other measures",
            country.country_code,
        )

        try:
            self.other_measures_table_data = [measure_json.get_table_row() for measure_json in self.other_measures]
        except Exception as exc:
            self.has_other_measures = False
            logger.error("Other measures error", exc_info=exc)

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


class OtherMeasuresNorthernIrelandSection(OtherMeasuresSection):
    template = "hierarchy/_other_measures_northern_ireland.html"

    def get_context_data(self):
        ctx = super().get_context_data()

        ctx["eu_other_measures_link"] = get_eu_commodity_link(self.commodity_object, self.country)

        return ctx


class RulesOfOriginSection(CommodityDetailSection):
    template = "hierarchy/_rules_of_origin.html"

    def __init__(self, country, commodity_object):
        super().__init__(country, commodity_object)

        self.old_rules_of_origin = commodity_object.get_old_rules_of_origin(
            country_code=country.country_code,
        )
        self.rules_of_origin = commodity_object.get_rules_of_origin(
            country_code=country.country_code,
        )

    @property
    def should_be_displayed(self):
        return bool(self.old_rules_of_origin) or bool(self.rules_of_origin)

    def get_menu_items(self):
        return [("Rules of origin", "rules_of_origin")]

    def get_context_data(self):
        ctx = super().get_context_data()

        ctx["old_rules_of_origin"] = self.old_rules_of_origin
        ctx["rules_of_origin"] = self.rules_of_origin

        return ctx


class RulesOfOriginNorthernIrelandSection(RulesOfOriginSection):
    template = "hierarchy/_rules_of_origin_northern_ireland.html"

    def get_context_data(self):
        ctx = super().get_context_data()

        ctx["eu_rules_of_origin_link"] = get_eu_commodity_link(self.commodity_object, self.country)

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


class SubHeadingTariffsAndTaxesNorthernIrelandSection(BaseTariffsAndTaxesNorthernIrelandSection):

    def get_eu_commodity_object(self, commodity_object):
        return SubHeading.objects.for_region(
            settings.SECONDARY_REGION,
        ).get(
            commodity_code=commodity_object.commodity_code,
            goods_nomenclature_sid=commodity_object.goods_nomenclature_sid,
        )


class HeadingTariffsAndTaxesNorthernIrelandSection(BaseTariffsAndTaxesNorthernIrelandSection):

    def get_eu_commodity_object(self, commodity_object):
        return Heading.objects.for_region(
            settings.SECONDARY_REGION,
        ).get(
            heading_code=commodity_object.heading_code,
            goods_nomenclature_sid=commodity_object.goods_nomenclature_sid,
        )


class TradeStatusSection(CommodityDetailSection):
    template = "hierarchy/_trade_status.html"

    @property
    def should_be_displayed(self):
        return has_trade_scenario(self.country)

    def get_menu_items(self):
        return [("Trade status", "trade_status")]

    def get_context_data(self):
        return get_tariff_content_context(self.country, self.commodity_object)
