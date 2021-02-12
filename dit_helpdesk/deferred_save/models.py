from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.module_loading import import_string


class DeferredSave(models.Model):
    data = JSONField()
    form_class = models.CharField(max_length=255)

    def apply(self):
        form_class = import_string(self.form_class)

        form = form_class(self.data)
        instance = form.save()

        return form, instance
