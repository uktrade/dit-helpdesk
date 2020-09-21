from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import override_settings, TestCase
from django.urls import reverse
from django.views import View

from ..views import BaseCMSMixin


User = get_user_model()


class MyView(BaseCMSMixin, View):

    def get(self, request):
        return HttpResponse("OK")


@override_settings(
    ROOT_URLCONF="cms.tests.urls",
    AUTHENTICATION_BACKENDS=[
        "django.contrib.auth.backends.ModelBackend",
    ],
)
class TestBaseCMSMixin(TestCase):

    def setUp(self):
        self.url = reverse("test-base-cms-mixin")

    def test_login_required_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}", fetch_redirect_response=False)

    def test_login_required_logged_in(self):
        email = "test@example.com"
        password = "test"
        user = User.objects.create(email=email)
        user.set_password(password)
        user.save()
        self.client.login(username=user.email, password=password)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
