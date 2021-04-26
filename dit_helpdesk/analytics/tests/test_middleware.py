from unittest import mock

from django.http import HttpResponse
from django.test import override_settings, TestCase
from django.urls import reverse
from django.views import View


class TestMiddlewareView(View):
    def get(self, request):
        return HttpResponse("OK")


@override_settings(
    MIDDLEWARE=["analytics.middleware.page_view_tracking_middleware"],
    ROOT_URLCONF="analytics.tests.urls",
)
class PageViewTrackingMiddlewareTestCase(TestCase):
    @mock.patch("analytics.middleware.track_page_view")
    def test_page_view_called_on_view(self, mock_track_page_view):
        response = self.client.get(reverse("test-middleware"))
        mock_track_page_view.assert_called_once_with(response.wsgi_request)
