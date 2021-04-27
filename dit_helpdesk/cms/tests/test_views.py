from mixer.backend.django import mixer

from django.urls import reverse

from core.helpers import reset_urls_for_settings
from regulations.models import RegulationGroup

from .base import CMSTestCase


class TestRegulationGroupsList(CMSTestCase):
    def setUp(self):
        self.login()

    @reset_urls_for_settings(CMS_ENABLED=True)
    def test_list(self):
        mixer.cycle(20).blend(RegulationGroup)

        response = self.client.get(reverse("cms:regulation-groups-list"))

        self.assertTemplateUsed(response, "cms/regulations/regulationgroup_list.html")

        object_list = response.context["object_list"]
        self.assertEqual(object_list.count(), 10)

    @reset_urls_for_settings(CMS_ENABLED=True)
    def test_search(self):
        foo_regulation = mixer.blend(RegulationGroup, title="This is foo regulation")
        bar_regulation = mixer.blend(RegulationGroup, title="This is bar regulation")

        response = self.client.get(reverse("cms:regulation-groups-list"))
        object_list = response.context["object_list"]
        self.assertIn(foo_regulation, object_list)
        self.assertIn(bar_regulation, object_list)
        searching = response.context["searching"]
        self.assertFalse(searching)
        search_query = response.context["search_query"]
        self.assertEqual(search_query, None)

        response = self.client.get(reverse("cms:regulation-groups-list"), {"q": "foo"})
        object_list = response.context["object_list"]
        self.assertIn(foo_regulation, object_list)
        self.assertNotIn(bar_regulation, object_list)
        searching = response.context["searching"]
        self.assertTrue(searching)
        search_query = response.context["search_query"]
        self.assertEqual(search_query, "foo")

        response = self.client.get(reverse("cms:regulation-groups-list"), {"q": "bar"})
        object_list = response.context["object_list"]
        self.assertNotIn(foo_regulation, object_list)
        self.assertIn(bar_regulation, object_list)
        searching = response.context["searching"]
        self.assertTrue(searching)
        search_query = response.context["search_query"]
        self.assertEqual(search_query, "bar")

        response = self.client.get(
            reverse("cms:regulation-groups-list"), {"q": "regulation"}
        )
        object_list = response.context["object_list"]
        self.assertIn(foo_regulation, object_list)
        self.assertIn(bar_regulation, object_list)
        searching = response.context["searching"]
        self.assertTrue(searching)
        search_query = response.context["search_query"]
        self.assertEqual(search_query, "regulation")

        response = self.client.get(
            reverse("cms:regulation-groups-list"), {"q": "madeup"}
        )
        object_list = response.context["object_list"]
        self.assertNotIn(foo_regulation, object_list)
        self.assertNotIn(bar_regulation, object_list)
        searching = response.context["searching"]
        self.assertTrue(searching)
        search_query = response.context["search_query"]
        self.assertEqual(search_query, "madeup")
