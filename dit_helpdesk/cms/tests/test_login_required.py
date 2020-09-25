from django.test import TestCase

from ..views import BaseCMSMixin
from ..urls import urlpatterns


class TestLoginRequired(TestCase):

    def test_login_required_applied_to_all_views(self):
        # This is a slightly clunky check to know whether login required is
        # applied but we're essentially specifying that all of our views need
        # to inherit from a mixin that does have the login_required decorator
        # applied
        for pattern in urlpatterns:
            view_class = pattern.callback.view_class
            self.assertTrue(issubclass(view_class, BaseCMSMixin))
