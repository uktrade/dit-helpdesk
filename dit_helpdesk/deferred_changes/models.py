from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.module_loading import import_string

from polymorphic.models import PolymorphicModel


class InvalidDataError(Exception):

    def __init__(self, form, *args, **kwargs):
        self.form = form
        super().__init__(*args, **kwargs)


class DeferredChange(PolymorphicModel):

    def apply(self):
        raise NotImplementedError(f"Deferred change subclass requires `apply` method.")


class DeferredCreate(DeferredChange):
    data = JSONField()
    form_class = models.CharField(max_length=255)

    def apply(self):
        form_class = import_string(self.form_class)

        form = form_class(self.data)
        if not form.is_valid():
            raise InvalidDataError(form)

        instance = form.save()

        return form, instance
