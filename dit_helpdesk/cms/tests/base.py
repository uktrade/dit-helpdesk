from django.contrib.auth import get_user_model
from django.test import TestCase


User = get_user_model()


class CMSTestCase(TestCase):
    def login(self):
        username = "testuser"
        email = "test@example.com"
        password = "test"
        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()
        self.client.login(username=user.username, password=password)
