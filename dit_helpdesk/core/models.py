from django.db import models


class ReloadDataTracking(models.Model):

    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    run_time = models.CharField(max_length=25, null=True)

    def __str__(self):
        return f"{self.start_time} - {self.end_time} - {self.run_time}"
