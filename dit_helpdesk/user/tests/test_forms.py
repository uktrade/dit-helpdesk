import logging

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from user.admin import UserCreationForm
from user.models import User

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class UserCreationFormTestCase(TestCase):
    """
    Test User Creation form
    """

    def test_saving_user_created_via_form(self):
        email = 'test@user.com'
        form_data = {'email': email}
        form = UserCreationForm(data=form_data)
        form.save(commit=True)
        user = User.objects.get(email=email)

        self.assertTrue(form.is_valid())
        self.assertTrue(form.cleaned_data['email'], user.email)

    def test_saving_user_created_via_form_without_committing(self):
        email = 'test@user.com'
        form_data = {'email': email}
        form = UserCreationForm(data=form_data)
        form.save(commit=False)

        self.assertTrue(form.is_valid())
        self.assertRaises(ObjectDoesNotExist, lambda: User.objects.get(email=email).email)
