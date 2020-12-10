import logging

from django.conf import settings

from commodities.helpers import get_global_tariff_context

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
        raise NotImplementedError("Implement `get_context_data`")


class BaseTariffAndChargesNorthernIrelandSection(CommodityDetailSection):
    template = "hierarchy/_tariffs_and_charges_northern_ireland.html"

    def __init__(self, country, commodity_object):
        super().__init__(country, commodity_object)

        self.uk_tariffs_and_charges_measures = self._get_tariffs_and_charges_measures(commodity_object, country)
        eu_commodity_object = self.get_eu_commodity_object(commodity_object)
        self.eu_tariffs_and_charges_measures = self._get_tariffs_and_charges_measures(eu_commodity_object, country)

    def _get_tariffs_and_charges_measures(self, commodity_object, country):
        tariffs_and_charges_measures = get_nomenclature_group_measures(
            commodity_object,
            "Tariffs and charges",
            country.country_code,
        )

        is_eu = self.country.country_code.upper() == "EU"
        if is_eu:
            tariffs_and_charges_measures = [m for m in tariffs_and_charges_measures if m.vat or m.excise]

        return tariffs_and_charges_measures

    def get_eu_commodity_object(self, commodity_object):
        raise NotImplementedError("Implement `get_eu_commodity_object`")

    @property
    def should_be_displayed(self):
        return bool(self.uk_tariffs_and_charges_measures)

    def get_menu_items(self):
        return [
            ("Tariffs and charges", "tariffs_and_charges"),
        ]

    def get_modals_context_data(self):
        return [
            measure_json.measures_modals
            for measure_json in self.uk_tariffs_and_charges_measures
        ]

    def _get_table_data(self, charges_and_measures):
        tariffs_and_charges_table_data = [
            measure_json.get_table_row()
            for measure_json in charges_and_measures
        ]

        return tariffs_and_charges_table_data

    def get_context_data(self):
        ctx = {
            "uk_tariffs_and_charges_table_data": self._get_table_data(self.uk_tariffs_and_charges_measures),
            "eu_tariffs_and_charges_table_data": self._get_table_data(self.eu_tariffs_and_charges_measures),
        }

        if settings.UKGT_ENABLED:
            ctx["global_tariff_data"] = get_global_tariff_context(self.commodity_object)

        return ctx


class QuotasNorthernIrelandSection(CommodityDetailSection):
    template = "hierarchy/_quotas_northern_ireland.html"

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
        return {
            "eu_quotas_link": get_eu_commodity_link(self.commodity_object, self.country),
            "quotas_table_data": self.quotas_table_data,
        }


class OtherMeasuresNorthernIrelandSection(CommodityDetailSection):
    template = "hierarchy/_other_measures_northern_ireland.html"

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
        return {
            "eu_other_measures_link": get_eu_commodity_link(self.commodity_object, self.country),
            "other_measures_table": self.other_measures_table_data,
        }


class RulesOfOriginNorthernIrelandSection(CommodityDetailSection):
    template = "hierarchy/_rules_of_origin_northern_ireland.html"

    def get_menu_items(self):
        return [("Rules of origin", "rules_of_origin")]

    def get_context_data(self):
        commodity_object = self.commodity_object
        country = self.country

        rules_of_origin = commodity_object.get_rules_of_origin(
            country_code=country.country_code,
        )

        return {
            "eu_rules_of_origin_link": get_eu_commodity_link(commodity_object, country),
            "rules_of_origin": rules_of_origin,
        }


class ProductRegulationsNorthernIrelandSection(CommodityDetailSection):
    template = "hierarchy/_product_regulations_northern_ireland.html"

    def get_menu_items(self):
        return [("Product-specific regulations", "regulations")]

    def get_context_data(self):
        return {
            "eu_regulations_link": get_eu_commodity_link(self.commodity_object, self.country),
        }


class SubHeadingTariffAndChargesNorthernIrelandSection(BaseTariffAndChargesNorthernIrelandSection):

    def get_eu_commodity_object(self, commodity_object):
        return SubHeading.objects.for_region(
            settings.SECONDARY_REGION,
        ).get(
            commodity_code=commodity_object.commodity_code,
            goods_nomenclature_sid=commodity_object.goods_nomenclature_sid,
        )


class HeadingTariffAndChargesNorthernIrelandSection(BaseTariffAndChargesNorthernIrelandSection):

    def get_eu_commodity_object(self, commodity_object):
        return Heading.objects.for_region(
            settings.SECONDARY_REGION,
        ).get(
            heading_code=commodity_object.heading_code,
            goods_nomenclature_sid=commodity_object.goods_nomenclature_sid,
        )
