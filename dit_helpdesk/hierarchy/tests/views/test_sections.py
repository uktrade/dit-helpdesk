from contextlib import contextmanager
from unittest import mock

from faker import Faker
from mixer.backend.django import mixer

from django.test import modify_settings, override_settings, TestCase
from django.urls import reverse

from countries.models import Country
from rules_of_origin.models import Rule, RulesDocument, RulesDocumentFootnote
from trade_tariff_service.tts_api import ImportMeasureJson

from ...helpers import create_nomenclature_tree
from ...models import Chapter, Heading, Section
from ...views.base import BaseSectionedCommodityObjectDetailView
from ...views.sections import (
    OtherMeasuresSection,
    QuotasSection,
    RulesOfOriginSection,
    TariffsAndTaxesSection,
)


faker = Faker()


class TestSectionsView(BaseSectionedCommodityObjectDetailView):
    model = Heading
    template_name = "hierarchy/test_sections.html"

    def update_commodity_object_tts_content(self, commodity_object):
        pass

@modify_settings(
    INSTALLED_APPS={
        "append": ["hierarchy.tests.views"],
    }
)
@override_settings(ROOT_URLCONF="hierarchy.tests.views.urls")
class BaseSectionTestCase(TestCase):

    def setUp(self):
        super().setUp()

        self.country = Country.objects.all().first()

        tree = create_nomenclature_tree()
        self.tree = tree

        self.section = mixer.blend(
            Section,
            nomenclature_tree=tree,
        )
        self.chapter = mixer.blend(
            Chapter,
            nomenclature_tree=tree,
            chapter_code="0100000000",
            goods_nomenclature_sid="1",
        )
        self.heading = mixer.blend(
            Heading,
            nomenclature_tree=tree,
            heading_code="0101000000",
            goods_nomenclature_sid="2",
        )
        mock_get_commodity_object_path = mock.patch.object(
            TestSectionsView,
            "get_commodity_object_path",
            return_value=[
                [self.heading],
                [self.chapter],
                [self.section],
            ],
        )
        mock_get_commodity_object_path.start()
        self.mock_get_commodity_object_path = mock_get_commodity_object_path

        mock_sections = mock.patch.object(
            TestSectionsView,
            "sections",
            new_callable=mock.PropertyMock(return_value=[self.section_class]),
        )
        mock_sections.start()
        self.mock_sections = mock_sections

    def tearDown(self):
        super().tearDown()

        self.mock_get_commodity_object_path.stop()
        self.mock_sections.stop()

    def get_url(self, country_code=None, commodity_code=None, nomenclature_sid=None):
        if not country_code:
            country_code = self.country.country_code

        if not commodity_code:
            commodity_code = self.heading.commodity_code

        if not nomenclature_sid:
            nomenclature_sid = self.heading.goods_nomenclature_sid

        return reverse(
            "test-sections-view",
            kwargs={
                "country_code": country_code,
                "commodity_code": commodity_code,
                "nomenclature_sid": nomenclature_sid,
            },
        )

    @contextmanager
    def patch_get_nomenclature_group_measures(self, measures):
        with mock.patch(
            "hierarchy.views.sections.get_nomenclature_group_measures",
            return_value=measures
        ) as mock_get_nomenclature_group_measures:
            yield mock_get_nomenclature_group_measures

    def assert_section_not_displayed(self, response, section_class):
        sections = response.context["sections"]

        for section in sections:
            if isinstance(section, section_class):
                raise AssertionError(f"{section_class} displayed")

    def assert_section_displayed(self, response, section_class):
        sections = response.context["sections"]

        for section in sections:
            if isinstance(section, section_class):
                return

        raise AssertionError(f"{section_class} not displayed")

    def assert_has_menu_item(self, response, menu_item_label, menu_item_id):
        section_menu_items = dict(response.context["section_menu_items"])

        try:
            found_menu_item_id = section_menu_items[menu_item_label]
        except KeyError:
            raise AssertionError(f"{menu_item_label} not found in menu items {section_menu_items.keys()}")

        if found_menu_item_id != menu_item_id:
            raise AssertionError(f"{menu_item_id} does not equal {found_menu_item_id}")

    def assert_uses_template(self, response, template_name):
        self.assertTemplateUsed(response, template_name)

    def assert_modal(self, response, modal_key, modal_value):
        modals = response.context["modals"]

        try:
            found_modal_value = modals[modal_key]
        except KeyError:
            raise AssertionError(f"{modal_key} not found in modals")

        if found_modal_value != modal_value:
            raise AssertionError(f"{modal_value} does not equal {found_modal_value}")

    def get_mock_measure(self, id=None, commodity_object=None, country_code="XT", vat=False, excise=False, measures_modals=None, **kwargs):
        if not id:
            id = faker.word()

        if not measures_modals:
            measures_modals = {}

        if not commodity_object:
            commodity_object = self.heading

        mock_measure = mock.MagicMock(
            id=id,
            spec=ImportMeasureJson,
            vat=vat,
            excise=excise,
            measures_modals=measures_modals,
            commodity_object=commodity_object,
            **kwargs,
        )

        mock_measure.get_table_row.return_value = [
            ["Country", country_code],
            ["ID", id],
        ]

        return mock_measure


class TariffsAndTaxesSectionTestCase(BaseSectionTestCase):
    section_class = TariffsAndTaxesSection

    def test_template(self):
        mock_measure = self.get_mock_measure()
        with self.patch_get_nomenclature_group_measures([mock_measure]):
            response = self.client.get(self.get_url())
        self.assert_uses_template(response, "hierarchy/_tariffs_and_taxes.html")

    def test_calls_get_nomenclature_group_measures(self):
        with self.patch_get_nomenclature_group_measures([]) as mock_get_nomenclature_group_measures:
            self.client.get(self.get_url())

        mock_get_nomenclature_group_measures.assert_called_with(
            self.heading,
            "Tariffs and charges",
            self.country.country_code,
            is_eu=self.country.is_eu,
        )

    def test_menu_items(self):
        mock_measure = self.get_mock_measure()
        with self.patch_get_nomenclature_group_measures([mock_measure]):
            response = self.client.get(self.get_url())
        self.assert_has_menu_item(response, "Tariffs and taxes", "tariffs_and_taxes")

    def test_should_be_displayed(self):
        with self.patch_get_nomenclature_group_measures([]):
            response = self.client.get(self.get_url())
        self.assert_section_not_displayed(response, TariffsAndTaxesSection)

        mock_vat_measure = self.get_mock_measure(vat=True)
        with self.patch_get_nomenclature_group_measures([mock_vat_measure]):
            response = self.client.get(self.get_url())
        self.assert_section_displayed(response, TariffsAndTaxesSection)

        mock_excise_measure = self.get_mock_measure(excise=True)
        with self.patch_get_nomenclature_group_measures([mock_excise_measure]):
            response = self.client.get(self.get_url())
        self.assert_section_displayed(response, TariffsAndTaxesSection)

        mock_tariff_measure = self.get_mock_measure()
        with self.patch_get_nomenclature_group_measures([mock_tariff_measure]):
            response = self.client.get(self.get_url())
        self.assert_section_displayed(response, TariffsAndTaxesSection)

    def test_modals_context_data(self):
        mock_vat_measure = self.get_mock_measure(
            vat=True,
            measures_modals={
                "mock_vat_measure": "mock_vat_measure_modal",
            },
        )

        mock_excise_measure = self.get_mock_measure(
            excise=True,
            measures_modals={
                "mock_excise_measure": "mock_excise_measure_modal",
            },
        )

        mock_tariff_measure = self.get_mock_measure(measures_modals={
            "mock_tariff_measure": "mock_tariff_measure_modal",
        })
        with self.patch_get_nomenclature_group_measures([
            mock_vat_measure,
            mock_excise_measure,
            mock_tariff_measure,
        ]):
            response = self.client.get(self.get_url())

        self.assert_modal(response, "mock_vat_measure", "mock_vat_measure_modal")
        self.assert_modal(response, "mock_excise_measure", "mock_excise_measure_modal")
        self.assert_modal(response, "mock_tariff_measure", "mock_tariff_measure_modal")

    def test_tariffs_table_data(self):
        mock_vat_measure = self.get_mock_measure("vat", vat=True)
        mock_excise_measure = self.get_mock_measure("excise", excise=True)
        mock_tariff_measure = self.get_mock_measure("tariff")

        with self.patch_get_nomenclature_group_measures([
            mock_vat_measure,
            mock_excise_measure,
            mock_tariff_measure,
        ]):
            response = self.client.get(self.get_url())

        tariffs_table_data = response.context["tariffs_table_data"]
        self.assertEqual(
            tariffs_table_data,
            [
                [["Country", "XT"], ["ID", "tariff"]],
            ],
        )

    def test_tariffs_table_data_is_sorted(self):
        with self.patch_get_nomenclature_group_measures([
            self.get_mock_measure("c", country_code="CC"),
            self.get_mock_measure("b", country_code="BB"),
            self.get_mock_measure("a", country_code="AA"),
        ]):
            response = self.client.get(self.get_url())

        tariffs_table_data = response.context["tariffs_table_data"]
        self.assertEqual(
            tariffs_table_data,
            [
                [["Country", "AA"], ["ID", "a"]],
                [["Country", "BB"], ["ID", "b"]],
                [["Country", "CC"], ["ID", "c"]],
            ],
        )

    def test_tariffs_table_data_urls(self):
        mock_tariff = self.get_mock_measure()

        with self.patch_get_nomenclature_group_measures([mock_tariff]):
            self.client.get(self.get_url())

        call_args, _ = mock_tariff.get_table_row.call_args_list[0]
        get_quotas_url, get_conditions_url = call_args
        self.assertEqual(
            get_quotas_url("XT", "12", "1"),
            self.heading.get_quotas_url("XT", "12", "1"),
        )
        self.assertEqual(
            get_conditions_url("XT", "12"),
            self.heading.get_conditions_url("XT", "12"),
        )

    def test_taxes_table_data(self):
        mock_vat_measure = self.get_mock_measure("vat", vat=True)
        mock_excise_measure = self.get_mock_measure("excise", excise=True)
        mock_tariff_measure = self.get_mock_measure("tariff")

        with self.patch_get_nomenclature_group_measures([
            mock_vat_measure,
            mock_excise_measure,
            mock_tariff_measure,
        ]):
            response = self.client.get(self.get_url())

        taxes_table_data = response.context["taxes_table_data"]
        self.assertEqual(
            taxes_table_data,
            [
                [["Country", "XT"], ["ID", "vat"]],
                [["Country", "XT"], ["ID", "excise"]],
            ],
        )

    def test_taxes_table_data_urls(self):
        mock_vat_measure = self.get_mock_measure("vat", vat=True)
        mock_excise_measure = self.get_mock_measure("excise", excise=True)

        with self.patch_get_nomenclature_group_measures([
            mock_vat_measure,
            mock_excise_measure,
        ]):
            self.client.get(self.get_url())

        call_args, _ = mock_vat_measure.get_table_row.call_args_list[0]
        get_quotas_url, get_conditions_url = call_args
        self.assertEqual(
            get_quotas_url("XT", "12", "1"),
            self.heading.get_quotas_url("XT", "12", "1"),
        )
        self.assertEqual(
            get_conditions_url("XT", "12"),
            self.heading.get_conditions_url("XT", "12"),
        )

        call_args, _ = mock_excise_measure.get_table_row.call_args_list[0]
        get_quotas_url, get_conditions_url = call_args
        self.assertEqual(
            get_quotas_url("XT", "12", "1"),
            self.heading.get_quotas_url("XT", "12", "1"),
        )
        self.assertEqual(
            get_conditions_url("XT", "12"),
            self.heading.get_conditions_url("XT", "12"),
        )

    def test_has_multiple_vat_entries(self):
        mock_vat_measure = self.get_mock_measure("vat", vat=True)
        with self.patch_get_nomenclature_group_measures([mock_vat_measure]):
            response = self.client.get(self.get_url())
        self.assertFalse(response.context["has_multiple_vat_entries"])

        another_mock_vat_measure = self.get_mock_measure("vat", vat=True)
        with self.patch_get_nomenclature_group_measures([
            mock_vat_measure,
            another_mock_vat_measure,
        ]):
            response = self.client.get(self.get_url())
        self.assertTrue(response.context["has_multiple_vat_entries"])


class QuotasSectionTestCase(BaseSectionTestCase):
    section_class = QuotasSection

    def test_template(self):
        mock_measure = self.get_mock_measure()
        with self.patch_get_nomenclature_group_measures([mock_measure]):
            response = self.client.get(self.get_url())
            self.assert_uses_template(response, "hierarchy/_quotas.html")

    def test_calls_get_nomenclature_group_measures(self):
        with self.patch_get_nomenclature_group_measures([]) as mock_get_nomenclature_group_measures:
            self.client.get(self.get_url())

        mock_get_nomenclature_group_measures.assert_called_with(
            self.heading,
            "Quotas",
            self.country.country_code,
            is_eu=self.country.is_eu,
        )

    def test_menu_items(self):
        mock_measure = self.get_mock_measure()
        with self.patch_get_nomenclature_group_measures([mock_measure]):
            response = self.client.get(self.get_url())
            self.assert_has_menu_item(response, "Quotas", "quotas")

    def test_should_be_displayed(self):
        with self.patch_get_nomenclature_group_measures([]):
            response = self.client.get(self.get_url())
            self.assert_section_not_displayed(response, QuotasSection)

        mock_measure = self.get_mock_measure()
        with self.patch_get_nomenclature_group_measures([mock_measure]):
            response = self.client.get(self.get_url())
            self.assert_section_displayed(response, QuotasSection)

    def test_modals_context_data(self):
        mock_measure = self.get_mock_measure(measures_modals={
            "mock_quota_measure": "mock_quota_measure_modal",
        })
        with self.patch_get_nomenclature_group_measures([mock_measure]):
            response = self.client.get(self.get_url())

        self.assert_modal(response, "mock_quota_measure", "mock_quota_measure_modal")

    def test_quotas_table_data(self):
        mock_measure = self.get_mock_measure("quota")

        with self.patch_get_nomenclature_group_measures([mock_measure]):
            response = self.client.get(self.get_url())

        quotas_table_data = response.context["quotas_table_data"]
        self.assertEqual(
            quotas_table_data,
            [
                [["Country", "XT"], ["ID", "quota"]],
            ],
        )

    def test_quotas_table_data_urls(self):
        mock_measure = self.get_mock_measure()

        with self.patch_get_nomenclature_group_measures([mock_measure]):
            self.client.get(self.get_url())

        call_args, _ = mock_measure.get_table_row.call_args_list[0]
        get_quotas_url, get_conditions_url = call_args
        self.assertEqual(
            get_quotas_url("XT", "12", "1"),
            self.heading.get_quotas_url("XT", "12", "1"),
        )
        self.assertEqual(
            get_conditions_url("XT", "12"),
            self.heading.get_conditions_url("XT", "12"),
        )


class OtherMeasuresSectionTestCase(BaseSectionTestCase):
    section_class = OtherMeasuresSection

    def test_template(self):
        mock_measure = self.get_mock_measure()
        with self.patch_get_nomenclature_group_measures([mock_measure]):
            response = self.client.get(self.get_url())
        self.assert_uses_template(response, "hierarchy/_other_measures.html")

    def test_calls_get_nomenclature_group_measures(self):
        with self.patch_get_nomenclature_group_measures([]) as mock_get_nomenclature_group_measures:
            self.client.get(self.get_url())

        mock_get_nomenclature_group_measures.assert_called_with(
            self.heading,
            "Other measures",
            self.country.country_code,
            is_eu=self.country.is_eu,
        )

    def test_menu_items(self):
        mock_measure = self.get_mock_measure()
        with self.patch_get_nomenclature_group_measures([mock_measure]):
            response = self.client.get(self.get_url())
        self.assert_has_menu_item(response, "Other measures", "other_measures")

    def test_should_be_displayed(self):
        with self.patch_get_nomenclature_group_measures([]):
            response = self.client.get(self.get_url())
            self.assert_section_not_displayed(response, OtherMeasuresSection)

        mock_measure = self.get_mock_measure()
        with self.patch_get_nomenclature_group_measures([mock_measure]):
            response = self.client.get(self.get_url())
            self.assert_section_displayed(response, OtherMeasuresSection)

    def test_modals_context_data(self):
        mock_measure = self.get_mock_measure(measures_modals={
            "mock_other_measure": "mock_other_measure_modal",
        })
        with self.patch_get_nomenclature_group_measures([mock_measure]):
            response = self.client.get(self.get_url())

        self.assert_modal(response, "mock_other_measure", "mock_other_measure_modal")

    def test_other_measures_table_data(self):
        mock_measure = self.get_mock_measure("other")

        with self.patch_get_nomenclature_group_measures([mock_measure]):
            response = self.client.get(self.get_url())

        other_measures_table_data = response.context["other_measures_table"]
        self.assertEqual(
            other_measures_table_data,
            [
                [["Country", "XT"], ["ID", "other"]],
            ],
        )

    def test_other_measures_table_data_urls(self):
        mock_measure = self.get_mock_measure()

        with self.patch_get_nomenclature_group_measures([mock_measure]):
            self.client.get(self.get_url())

        call_args, _ = mock_measure.get_table_row.call_args_list[0]
        get_quotas_url, get_conditions_url = call_args
        self.assertEqual(
            get_quotas_url("XT", "12", "1"),
            self.heading.get_quotas_url("XT", "12", "1"),
        )
        self.assertEqual(
            get_conditions_url("XT", "12"),
            self.heading.get_conditions_url("XT", "12"),
        )


class RulesOfOriginSectionTestCase(BaseSectionTestCase):
    section_class = RulesOfOriginSection

    def setUp(self):
        super().setUp()

        rules_document = mixer.blend(
            RulesDocument,
            countries=[self.country],
            nomenclature_tree=self.tree,
        )
        self.rules_document = rules_document

        self.rule = mixer.blend(
            Rule,
            description=mixer.RANDOM,
            headings=[self.heading],
            rules_document=rules_document,
        )

    def test_template(self):
        with self.patch_get_nomenclature_group_measures([]):
            response = self.client.get(self.get_url())
        self.assert_uses_template(response, "hierarchy/_rules_of_origin.html")

    def test_menu_items(self):
        mock_measure = self.get_mock_measure()
        with self.patch_get_nomenclature_group_measures([mock_measure]):
            response = self.client.get(self.get_url())
            self.assert_has_menu_item(response, "Rules of origin", "rules_of_origin")

    def test_should_be_displayed(self):
        with self.patch_get_nomenclature_group_measures([]):
            response = self.client.get(self.get_url())
        self.assert_section_displayed(response, RulesOfOriginSection)

    def test_rules_of_origin(self):
        expected_rules_of_origin = self.heading.get_rules_of_origin(self.country.country_code)

        with self.patch_get_nomenclature_group_measures([]), \
            mock.patch.object(Heading, "get_rules_of_origin") as mock_rules_of_origin:
            mock_rules_of_origin.return_value = expected_rules_of_origin
            response = self.client.get(self.get_url())

        mock_rules_of_origin.assert_called_once_with(country_code=self.country.country_code)
        rules_of_origin = response.context["rules_of_origin"]

        self.assertEqual(
            rules_of_origin,
            expected_rules_of_origin,
        )

    def test_has_uk_trade_agreement(self):
        with self.patch_get_nomenclature_group_measures([]):
            response = self.client.get(self.get_url())

        self.assertEqual(
            response.context["has_uk_trade_agreement"],
            self.country.has_uk_trade_agreement,
        )

    def test_has_gsp_tariff_preference(self):
        with self.patch_get_nomenclature_group_measures([]) as mock_nomenclature_group_measures:
            response = self.client.get(self.get_url())
        mock_nomenclature_group_measures.assert_called_with(
            self.heading,
            "Tariffs and charges",
            self.country.country_code,
        )
        self.assertFalse(response.context["has_gsp_tariff_preference"])

        mock_measure_no_gsp = self.get_mock_measure(is_gsp=False)
        with self.patch_get_nomenclature_group_measures([mock_measure_no_gsp]) as mock_nomenclature_group_measures:
            response = self.client.get(self.get_url())
        mock_nomenclature_group_measures.assert_called_with(
            self.heading,
            "Tariffs and charges",
            self.country.country_code,
        )
        self.assertFalse(response.context["has_gsp_tariff_preference"])

        mock_measure_has_gsp = self.get_mock_measure(is_gsp=True)
        with self.patch_get_nomenclature_group_measures([mock_measure_has_gsp]) as mock_nomenclature_group_measures:
            response = self.client.get(self.get_url())
        mock_nomenclature_group_measures.assert_called_with(
            self.heading,
            "Tariffs and charges",
            self.country.country_code,
        )
        self.assertTrue(response.context["has_gsp_tariff_preference"])
