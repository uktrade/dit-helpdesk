from django.conf import settings
from django.http import HttpResponse
from django.test import override_settings, TestCase
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from ..helpers import require_feature


@method_decorator(require_feature("FEATURE_SWITCH_ENABLED"), name="dispatch")
class MyView(View):

    def get(self, request):
        return HttpResponse("OK")


@override_settings(
    ROOT_URLCONF="core.tests.urls",
)
class TestRequireFeature(TestCase):

    def setUp(self):
        self.url = reverse("test-require-feature")

    def test_feature_switch_does_not_exist(self):
        with self.assertRaises(AttributeError):
            _ = settings.FEATURE_SWITCH_ENABLED
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    @override_settings(FEATURE_SWITCH_ENABLED=True)
    def test_feature_switch_on(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @override_settings(FEATURE_SWITCH_ENABLED=False)
    def test_feature_switch_off(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
