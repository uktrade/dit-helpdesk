from django.db import models
from django.conf import settings


class Contact(models.Model):
    """
    Feedback form for model
    """
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    message = models.TextField(max_length=settings.CONTACT_MAX_LENGTH)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Form {0}".format(self.created_on.strftime("%B %d, %Y, %H:%M:%S"))
