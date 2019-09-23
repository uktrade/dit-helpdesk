from django.db import models
from django.conf import settings


class Feedback(models.Model):
    """
    Feedback form for model
    """
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField(max_length=settings.FEEDBACK_MAX_LENGTH)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Form {0}".format(self.created_on.strftime("%B %d, %Y, %H:%M:%S"))
