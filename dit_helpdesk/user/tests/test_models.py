from django.test import TestCase
from mixer.backend.django import mixer

from user.models import User


class UserModelsTestCase(TestCase):
    """
    Test User model
    """

    def setUp(self):
        self.user = mixer.blend(User, email="test@user.com")

    def test_username_returns_email(self):
        self.assertEqual(self.user.username, "test@user.com")
