from django.db import models


class Feedback(models.Model):
    message = models.TextField()
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
