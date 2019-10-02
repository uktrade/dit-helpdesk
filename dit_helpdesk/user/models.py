from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)

    @property
    def username(self):
        return self.email

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
