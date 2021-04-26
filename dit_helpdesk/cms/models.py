import logging
import reversion

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from deferred_changes.models import DeferredChange


logger = logging.getLogger(__name__)


User = get_user_model()


class ApprovalManager(models.Manager):
    def pending(self):
        return self.filter(approved_at__isnull=True)


class Approval(models.Model):
    objects = ApprovalManager()

    approved_at = models.DateTimeField(null=True)
    approved_by = models.ForeignKey(
        User, null=True, on_delete=models.PROTECT, related_name="approved_approvals"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="created_approvals"
    )
    deferred_change = models.OneToOneField(DeferredChange, on_delete=models.PROTECT)
    description = models.CharField(max_length=255)

    @property
    def approved(self):
        return self.approved_at is not None

    def approve(self, user):
        with reversion.create_revision():
            deferred_change = self.deferred_change

            form, instance = self.deferred_change.apply()

            reversion.set_user(user)
            reversion.set_comment(f"Created revision from approval {self.pk}")

            logger.info(
                "%s %s (%s)",
                deferred_change.action_type.title(),
                instance.__class__.__name__,
                instance.pk,
                extra={
                    "user": self.created_by,
                    "cms.audit": {
                        "action_type": deferred_change.action_type,
                        "object_type": instance.__class__.__name__,
                        "pk": instance.pk,
                    },
                },
            )

        self.approved_at = timezone.datetime.now()
        self.approved_by = user

        logger.info(
            'Approve "%s" (%s)',
            self.description,
            self.pk,
            extra={
                "user": self.approved_by,
                "cms.audit": {
                    "action_type": "approve",
                    "object_type": self.__class__.__name__,
                    "pk": self.pk,
                },
            },
        )

        self.save()

        return form, instance

    def get_bound_form(self):
        form = self.deferred_change.get_bound_form()

        return form

    def can_approve(self, user):
        if user.is_superuser:
            return True

        return not self.approved and self.created_by != user
