from django.db import models


class ReloadDataTracking(models.Model):

    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    run_time = models.DurationField(null=True)
    reason = models.CharField(null=True, max_length=255)

    def __str__(self):
        return f"{self.start_time} - {self.end_time} - {self.run_time}"
