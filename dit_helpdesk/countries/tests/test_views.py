import logging

from collections import namedtuple

from django.test import override_settings, TestCase
from django.test.utils import modify_settings
from django.urls import reverse
from django.utils.functional import SimpleLazyObject

from countries.models import Country

logger = logging.getLogger(__name__)
# logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


Agreement = namedtuple("Agreement", ["country_code", "agreements"])


class CountriesViewsTestCase(TestCase):

    """
    Views tests
    """

    def test_get_choose_country_returns_http_200_and_renders_correct_template(self):
        resp = self.client.get(reverse("choose-country"))
        self.assertTrue(resp.status_code, 200)
        self.assertTemplateUsed(resp, "countries/choose_country.html")

    def test_session_has_no_origin_country_attribute(self):
        session = self.client.session
        self.assertRaises(KeyError, lambda: session["origin_country"])

    def test_request_has_origin_country_attribute(self):
        session = self.client.session
        session["origin_country"] = "AU"
        session.save()
        self.assertEqual(session["origin_country"], "AU")

    def test_get_context_has_selected_country_and_value_is_false(self):
        resp = self.client.get(reverse("choose-country"))
        self.assertFalse("selected_country" in resp.context)

    def test_get_context_does_not_have_selected_country_and_value_is_cleared(self):
        resp = self.client.get(reverse("choose-country"))
        self.assertTrue("selected_country" not in resp.context.keys())

    def test_post_is_ok_and_has_valid_csrftoken(self):
        resp = self.client.post(reverse("choose-country"))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue("csrf_token" in resp.context)
        self.assertTrue(isinstance(resp.context["csrf_token"], SimpleLazyObject))

    def test_post_without_values_and_without_session_attribute_gives_correct_error_and_renders_form(
        self,
    ):
        resp = self.client.post(reverse("choose-country"))
        self.assertTrue("origin_country" not in self.client.session)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue("isError" in resp.context)
        self.assertEqual(resp.context["isError"], True)
        self.assertEqual(
            resp.context["errorInputMessage"], "Enter a country or territory"
        )
        self.assertTemplateUsed(resp, "countries/choose_country.html")

    def test_post_without_values_and_with_session_attribute_gives_correct_error_and_renders_form(
        self,
    ):
        session = self.client.session
        session["origin_country"] = "AU"
        session.save()
        self.assertTrue("origin_country" in self.client.session)
        resp = self.client.post(reverse("choose-country"))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue("isError" in resp.context)
        self.assertEqual(resp.context["isError"], True)
        self.assertEqual(
            resp.context["errorInputMessage"], "Enter a country or territory"
        )
        self.assertTemplateUsed(resp, "countries/choose_country.html")

    def test_post_with_country_selected_and_country_exists_and_country_code_not_in_session(
        self,
    ):
        self.assertTrue("origin_country" not in self.client.session)
        resp = self.client.post(
            reverse("choose-country"), data={"origin_country": "au"}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp.url, reverse("search:search-commodity", kwargs={"country_code": "au"})
        )

    def test_post_with_country_selected_and_country_not_exist(self):
        with self.assertRaises(Country.DoesNotExist):
            Country.objects.get(country_code="XT")
        resp = self.client.post(
            reverse("choose-country"), data={"origin_country": "xt"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.context["errorInputMessage"], "Enter a country or territory"
        )
        self.assertTemplateUsed(resp, "countries/choose_country.html")
        self.assertTrue("origin_country" not in self.client.session)

    @override_settings(AGREEMENTS=[("XX", True)])
    def test_post_with_country_having_fta_and_enabled(self):
        Country.objects.create(country_code="XX", name="Atlantis")
        self.assertTrue("origin_country" not in self.client.session)
        resp = self.client.post(
            reverse("choose-country"), data={"origin_country": "xx"}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp.url, reverse("country-information", kwargs={"country_code": "xx"})
        )

    @override_settings(AGREEMENTS=[("XX", False)])
    def test_post_with_country_having_fta_and_disabled(self):
        Country.objects.create(country_code="XX", name="Atlantis")
        self.assertTrue("origin_country" not in self.client.session)
        resp = self.client.post(
            reverse("choose-country"), data={"origin_country": "xx"}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp.url, reverse("search:search-commodity", kwargs={"country_code": "xx"})
        )

    @override_settings(AGREEMENTS=[])
    def test_post_with_country_having_fta_and_without_setting(self):
        Country.objects.create(country_code="XX", name="Atlantis")
        self.assertTrue("origin_country" not in self.client.session)
        resp = self.client.post(
            reverse("choose-country"), data={"origin_country": "xx"}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp.url, reverse("search:search-commodity", kwargs={"country_code": "xx"})
        )


@modify_settings(INSTALLED_APPS={"append": ["countries.tests"]})
class CountryInformationViewTestCase(TestCase):
    def setUp(self):
        super().setUp()

        self.country = Country.objects.create(country_code="XX", name="Atlantis")
        self.url = reverse(
            "country-information",
            kwargs={"country_code": self.country.country_code.lower()},
        )

    def test_agreement_with_invalid_country_code(self):
        with self.assertRaises(Country.DoesNotExist):
            Country.objects.get(country_code="XT")

        url = reverse("country-information", kwargs={"country_code": "XT"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @override_settings(AGREEMENTS=[])
    def test_agreement_page_without_settings(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    @override_settings(AGREEMENTS=[("XX", False)])
    def test_agreement_page_with_setting_disabled(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    @override_settings(AGREEMENTS=[("XX", True)])
    def test_agreement_page_with_setting_enabled(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @override_settings(AGREEMENTS=[("XX", True)])
    def test_renders_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "countries/XX/information.html")

    @override_settings(AGREEMENTS=[("XX", True)])
    def test_context_data(self):
        response = self.client.get(self.url)
        ctx = response.context_data

        self.assertEqual(ctx["country"], self.country)
        self.assertEqual(ctx["country_code"], "xx")
        self.assertEqual(
            ctx["trade_agreements_template_name"], "countries/XX/_trade_agreements.html"
        )
        self.assertEqual(ctx["goods_template_name"], "countries/XX/_goods.html")
        self.assertEqual(
            ctx["grow_your_business_template_name"],
            "countries/XX/_grow_your_business.html",
        )
        self.assertEqual(
            ctx["other_information_template_name"],
            "countries/XX/_other_information.html",
        )

    @override_settings(AGREEMENTS=[("XX", True)])
    def test_renders_custom_html(self):
        response = self.client.get(self.url)

        self.assertContains(response, "Custom XX trade agreements")
        self.assertContains(response, "Custom XX goods")
        self.assertContains(response, "Custom XX grow your business")
        self.assertContains(response, "Custom XX other information")


@modify_settings(INSTALLED_APPS={"append": ["countries.tests"]})
class CountryInformationViewTestCaseEUVersion(TestCase):
    def setUp(self):
        super().setUp()

        self.country = Country.objects.create(
            country_code="XX", name="Atlantis", is_eu=True
        )
        self.url = reverse(
            "country-information",
            kwargs={"country_code": self.country.country_code.lower()},
        )

    def test_EU_country_code_updates(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "countries/EU/information.html")


class LocationAutocompleteViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse("location-autocomplete")

    def test_location_autocomplete(self):
        response = self.client.get(self.url)
        self.assertContains(response, '{"en-GB": "Italy"}')

    @override_settings(COUNTRIES_TO_REMOVE={"IT"})
    def test_location_autocomplete_remove_country(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, '{"en-GB": "Italy"}')

    @override_settings(COUNTRY_SYNONYMS={"IT": ["Italia"]})
    def test_location_autocomplete_synonym(self):
        response = self.client.get(self.url)
        self.assertContains(response, "nym:italia")
