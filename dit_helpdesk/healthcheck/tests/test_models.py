from django.test import TestCase

from healthcheck.models import HealthCheck


class TestModels(TestCase):

    def test_health_model(self):
        check = HealthCheck.objects.get(health_check_field=True)
        self.assertEquals(check.health_check_field, True)
        self.assertEquals(str(check), "True")
