from django import forms


def get_form_class_name(o):
    if not isinstance(o, forms.ModelForm):
        raise TypeError(f"{o} is not an instance of ModelForm")

    module = o.__class__.__module__
    class_name = o.__class__.__name__

    return f"{module}.{class_name}"
