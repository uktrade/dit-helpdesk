from django import forms

from .models import DeferredCreate, DeferredUpdate
from .utils import get_form_class_name


def get_field_value(form, key):
    field = form.fields[key]

    if isinstance(field, forms.ModelMultipleChoiceField):
        return form.data.getlist(key)

    return form.data[key]


def get_form_data(form):
    data = {k: get_field_value(form, k) for k in form.data if k in form.fields}

    return data


class DeferredFormMixin:
    def defer_create(self):
        data = get_form_data(self)

        deferred_create = DeferredCreate.objects.create(
            data=data, form_class=get_form_class_name(self)
        )

        return deferred_create

    def defer_update(self):
        data = get_form_data(self)
        instance = self.instance

        deferred_update = DeferredUpdate.objects.create(
            data=data, instance=instance, form_class=get_form_class_name(self)
        )

        return deferred_update
