import datetime as dt
import requests_mock

from django.test import TestCase, Client, override_settings
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

    @override_settings(ES_URL="")
    def test_check_view_no_elasticsearch_connection(self):
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

        old_date = (
            timezone.now() - TreeRefreshCheckView.MAX_DELTA - dt.timedelta(days=1)
        )
        tree.start_date = old_date
        tree.save()

        resp = self.anonymous_client.get(reverse("healthcheck:tree_freshness"))

        self.assertEqual(resp.content, b"Failed")
        self.assertEqual(resp.status_code, 503)

    @requests_mock.Mocker()
    def test_cms_existence__exists(self, mock_requests):
        mock_requests.get("http://testserver/cms/", status_code=200)
        resp = self.anonymous_client.get(reverse("healthcheck:cms_existence"))

        self.assertEqual(resp.content, b"Failed")
        self.assertEqual(resp.status_code, 503)

        mock_requests.get("http://testserver/cms/", status_code=302)
        resp = self.anonymous_client.get(reverse("healthcheck:cms_existence"))

        self.assertEqual(resp.content, b"Failed")
        self.assertEqual(resp.status_code, 503)

    @requests_mock.Mocker()
    def test_cms_existence__does_not_exists(self, mock_requests):
        mock_requests.get("http://testserver/cms/", status_code=404)
        resp = self.anonymous_client.get(reverse("healthcheck:cms_existence"))

        self.assertEqual(resp.content, b"OK")
        self.assertEqual(resp.status_code, 200)
