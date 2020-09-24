from mixer.backend.django import mixer

from django.db.utils import IntegrityError
from django.test import TestCase

from user.models import User


class UserModelsTestCase(TestCase):
    """
    Test User model
    """

    def test_unique_email(self):
        mixer.blend(User, email="test@user.com")
        with self.assertRaises(IntegrityError):
            mixer.blend(User, email="test@user.com")
