from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from deferred_save.models import DeferredSave


User = get_user_model()


class Approval(models.Model):
    approved_at = models.DateTimeField(null=True)
    approved_by = models.ForeignKey(
        User,
        null=True,
        on_delete=models.PROTECT,
        related_name="approved_approvals",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="created_approvals",
    )
    deferred_save = models.OneToOneField(DeferredSave, on_delete=models.PROTECT)

    def approve(self, user):
        form, instance = self.deferred_save.apply()

        self.approved_at = timezone.datetime.now()
        self.approved_by = user

        self.save()

        return form, instance
