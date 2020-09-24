import datetime as dt

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from healthcheck.models import HealthCheck
from healthcheck.views import TreeRefreshCheckView
from hierarchy.helpers import create_nomenclature_tree

import xml.etree.ElementTree as ET


class TestViews(TestCase):
    """
    Test Healthcheck views
    """

    def setUp(self):
        self.anonymous_client = Client()

    def test_check_view(self):
        response = self.anonymous_client.get(reverse("healthcheck:basic"))
        tree = ET.fromstring(response.content)
        pingdom_status = tree[0].text
        pingdom_response_time = float(tree[1].text)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(pingdom_status, "OK")
        self.assertGreater(pingdom_response_time, 0)
        self.assertLess(pingdom_response_time, 1)

    def test_check_view_no_data_fail(self):
        HealthCheck.objects.all().delete()
        response = self.anonymous_client.get(reverse("healthcheck:basic"))
        tree = ET.fromstring(response.content)
        pingdom_status = tree[0].text
        pingdom_response_time = float(tree[1].text)
        self.assertGreater(pingdom_response_time, 0)
        self.assertLess(pingdom_response_time, 1)
        self.assertEqual(pingdom_status, "FAIL")
        self.assertEqual(response.status_code, 200)

    def test_tree_freshness__fresh(self):
        create_nomenclature_tree()

        resp = self.anonymous_client.get(reverse("healthcheck:tree_freshness"))

        self.assertEqual(resp.content, b"OK")
        self.assertEqual(resp.status_code, 200)

    def test_tree_freshness__stale(self):
        tree = create_nomenclature_tree()

        old_date = timezone.now() - TreeRefreshCheckView.MAX_DELTA - dt.timedelta(days=1)
        tree.start_date = old_date
        tree.save()

        resp = self.anonymous_client.get(reverse("healthcheck:tree_freshness"))

        self.assertEqual(resp.content, b"Failed")
        self.assertEqual(resp.status_code, 503)
