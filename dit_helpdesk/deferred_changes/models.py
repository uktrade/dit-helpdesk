from django import forms
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


class DeferredValue:

    def __init__(self, bound_field):
        self.bound_field = bound_field
        self.field = bound_field.field

    @property
    def description(self):
        return self.bound_field.label

    @property
    def single_value(self):
        return not isinstance(self.field, forms.ModelMultipleChoiceField)

    @property
    def value(self):
        return self.bound_field.value()

    @property
    def values(self):
        if isinstance(self.field, forms.ModelMultipleChoiceField):
            values = self.bound_field.value()

            return (
                desc
                for pk, desc in self.field.choices
                if str(pk) in values
            )

        return self.bound_field.value()


class DeferredFormChange(DeferredChange):
    class Meta:
        abstract = True

    data = JSONField()
    form_class = models.CharField(max_length=255)

    def get_form_kwargs(self):
        return {}

    def apply(self):
        form = self.get_bound_form()

        if not form.is_valid():
            raise InvalidDataError(form)

        instance = form.save()

        return form, instance

    def get_bound_form(self):
        form_class = import_string(self.form_class)

        return form_class(self.data, **self.get_form_kwargs())

    def get_deferred_changes(self):
        form = self.get_bound_form()

        return (
            DeferredValue(bound_field)
            for bound_field in form
        )


class DeferredCreate(DeferredFormChange):
    pass


class DeferredUpdate(DeferredFormChange):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    instance = GenericForeignKey('content_type', 'object_id')

    def get_form_kwargs(self):
        return {"instance": self.instance}
