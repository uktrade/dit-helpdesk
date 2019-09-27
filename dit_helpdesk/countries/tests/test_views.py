import logging

from django.test import TestCase
from django.urls import reverse
from django.utils.functional import SimpleLazyObject

from countries.models import Country

logger = logging.getLogger(__name__)
# logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class CountriesViewsTestCase(TestCase):

    """
    Views tests
    """

    def test_get_choose_country_returns_http_200_and_renders_correct_template(self):
        resp = self.client.get(reverse('choose-country'))
        self.assertTrue(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'countries/choose_country.html')

    def test_session_has_no_origin_country_attribute(self):
        session = self.client.session
        self.assertRaises(KeyError, lambda: session['origin_country'])

    def test_request_has_origin_country_attribute(self):
        session = self.client.session
        session['origin_country'] = 'AU'
        session.save()
        self.assertEqual(session['origin_country'], 'AU')

    def test_get_context_has_selected_country_and_value_is_false(self):
        resp = self.client.get(reverse('choose-country'))
        self.assertTrue('selected_country' in resp.context)
        self.assertEqual(resp.context['selected_country'], False)

    def test_get_context_has_selected_country_and_value_is_country_code(self):
        session = self.client.session
        session['origin_country'] = 'AU'
        session.save()
        resp = self.client.get(reverse('choose-country'))
        self.assertEqual(resp.context['selected_country'], 'AU')

    def test_post_is_ok_and_has_valid_csrftoken(self):
        resp = self.client.post(reverse('choose-country'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('csrf_token' in resp.context)
        self.assertTrue(isinstance(resp.context['csrf_token'], SimpleLazyObject))

    def test_post_without_values_and_without_session_attribute_gives_correct_error_and_renders_form(self):
        resp = self.client.post(reverse('choose-country'))
        self.assertTrue('origin_country' not in self.client.session)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('isError' in resp.context)
        self.assertEqual(resp.context['isError'], True)
        self.assertFalse(resp.context['country_options'])
        self.assertEqual(resp.context['errorInputMessage'], "Enter a country")
        self.assertTemplateUsed(resp, 'countries/choose_country.html')

    def test_post_without_values_and_with_session_attribute_gives_correct_error_and_renders_form(self):
        session = self.client.session
        session['origin_country'] = 'AU'
        session.save()
        self.assertTrue('origin_country' in self.client.session)
        resp = self.client.post(reverse('choose-country'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('isError' in resp.context)
        self.assertEqual(resp.context['isError'], True)
        self.assertFalse(resp.context['country_options'])
        self.assertEqual(resp.context['errorInputMessage'], "Enter a country")
        self.assertTemplateUsed(resp, 'countries/choose_country.html')

    def test_post_with_country_selected_and_country_exists_and_country_code_not_in_session(self):
        Country.objects.create(country_code="AU", name="Australia")
        self.assertTrue('origin_country' not in self.client.session)
        resp = self.client.post(reverse('choose-country'), data={"origin_country": "au"})
        self.assertEqual(self.client.session['origin_country'], "AU")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('search:search-commodity', kwargs={
            "country_code": self.client.session['origin_country'].lower()
        }))

    def test_post_with_country_selected_and_country_not_exist(self):
        resp = self.client.post(reverse('choose-country'), data={"origin_country": "au"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['errorInputMessage'], "Enter a country")
        self.assertTemplateUsed(resp, 'countries/choose_country.html')
        self.assertTrue('origin_country' not in self.client.session)
