from contextlib import contextmanager

from django.db import models
from django.utils import timezone


class ReloadDataTrackingLockedError(Exception):
    pass


class ReloadDataTracking(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    run_time = models.DurationField(null=True)
    reason = models.TextField(null=True)

    def __str__(self):
        return f"{self.start_time} - {self.end_time} - {self.run_time}"

    @classmethod
    @contextmanager
    def lock(cls):
        if cls.objects.filter(end_time__isnull=True).exists():
            raise ReloadDataTrackingLockedError()

        obj = cls.objects.create(start_time=timezone.now())
        try:
            yield obj
        except Exception as e:
            obj.reason = str(e)
            raise
        finally:
            obj.end_time = timezone.now()
            obj.run_time = obj.end_time - obj.start_time
            obj.save()
