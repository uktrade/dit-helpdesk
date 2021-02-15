from .models import DeferredSave
from .utils import get_form_class_name


class DeferredSaveFormMixin:

    def defer_save(self):
        data = {
            k: v
            for k, v in self.data.items()
            if k in self.fields
        }

        deferred_save = DeferredSave.objects.create(
            data=data,
            form_class=get_form_class_name(self),
        )

        return deferred_save
