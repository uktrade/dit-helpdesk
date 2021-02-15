from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
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


class DeferredFormChange(DeferredChange):
    class Meta:
        abstract = True

    data = JSONField()
    form_class = models.CharField(max_length=255)

    def get_form_kwargs(self):
        return {}

    def apply(self):
        form_class = import_string(self.form_class)

        form = form_class(self.data, **self.get_form_kwargs())
        if not form.is_valid():
            raise InvalidDataError(form)

        instance = form.save()

        return form, instance


class DeferredCreate(DeferredFormChange):
    pass


class DeferredUpdate(DeferredFormChange):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    instance = GenericForeignKey('content_type', 'object_id')

    def get_form_kwargs(self):
        return {"instance": self.instance}
