from .models import DeferredCreate
from .utils import get_form_class_name


class DeferredFormMixin:

    def defer_create(self):
        data = {
            k: v
            for k, v in self.data.items()
            if k in self.fields
        }

        deferred_create = DeferredCreate.objects.create(
            data=data,
            form_class=get_form_class_name(self),
        )

        return deferred_create
