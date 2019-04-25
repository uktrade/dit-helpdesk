from django.test import TestCase
from mixer.backend.django import mixer

from healthcheck.models import HealthCheck


class TestModels(TestCase):

    def test_health_model(self):
        check = mixer.blend(HealthCheck, health_check_field=True)
        self.assertEquals(check.health_check_field, True)
        self.assertEquals(str(check), "True")
        self.assertEquals(check.__unicode__(), "True")
