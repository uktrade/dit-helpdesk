from unittest import mock

from django.template import Template, Context
from django.test import TestCase, override_settings

expected_value_with_setting = "expected value"
expected_content_for_missing_setting = "<!-- missing GTM container id -->"


class CoookieTemplateTagTestCase(TestCase):
    """
    Test the templatetags return the expected content
    when the required setting is and isn't present
    """

    @override_settings(HELPDESK_GA_GTM=expected_value_with_setting)
    def test_google_tag_manager_templatetag_with_setting(self):
        template = Template(
            template_string="""
            {% load gtm %}
            {% google_tag_manager %}
        """
        )
        content = template.render(Context({}))
        self.assertIn(expected_value_with_setting, content)

    @override_settings(HELPDESK_GA_GTM=expected_value_with_setting)
    @mock.patch("cookies.templatetags.gtm.render_gtm_template")
    def test_google_tag_manager_templatetag_renders_main_template(self, mock_render):
        template = Template(
            template_string="""
            {% load gtm %}
            {% google_tag_manager %}
        """
        )
        template.render(Context({}))
        mock_render.assert_called_with("gtm.html")

    @override_settings(HELPDESK_GA_GTM=None)
    def test_google_tag_manager_templatetag_without_setting(self):
        template = Template(
            template_string="""
            {% load gtm %}
            {% google_tag_manager %}
        """
        )
        content = template.render(Context({}))
        self.assertIn(expected_content_for_missing_setting, content)

    @override_settings(HELPDESK_GA_GTM=expected_value_with_setting)
    def test_google_tag_manager_noscript_templatetag_with_setting(self):
        template = Template(
            template_string="""
            {% load gtm %}
            {% google_tag_manager_noscript %}
        """
        )
        content = template.render(Context({}))
        self.assertIn(expected_value_with_setting, content)

    @override_settings(HELPDESK_GA_GTM=expected_value_with_setting)
    @mock.patch("cookies.templatetags.gtm.render_gtm_template")
    def test_google_tag_manager_noscript_templatetag_renders_main_template(
        self, mock_render
    ):
        template = Template(
            template_string="""
            {% load gtm %}
            {% google_tag_manager_noscript %}
        """
        )
        template.render(Context({}))
        mock_render.assert_called_with("gtm_noscript.html")

    @override_settings(HELPDESK_GA_GTM=None)
    def test_google_tag_manager_noscript_templatetag_without_setting(self):
        template = Template(
            template_string="""
            {% load gtm %}
            {% google_tag_manager_noscript %}
        """
        )
        content = template.render(Context({}))
        self.assertIn(expected_content_for_missing_setting, content)
