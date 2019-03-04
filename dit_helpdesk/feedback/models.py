from django.db import models
from django.conf import settings


class Feedback(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField(max_length=settings.FEEDBACK_MAX_LENGTH)
    created_on = models.DateTimeField(auto_now_add=True)
