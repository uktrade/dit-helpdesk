from django import forms
from django.core.validators import RegexValidator

from regulations.models import Regulation


class RegulationSearchForm(forms.Form):
    q = forms.CharField(label="Search regulations")


class RegulationForm(forms.ModelForm):
    class Meta:
        model = Regulation
        fields = ["title", "url"]

    url = forms.URLField(
        label="URL",
        validators=[
            RegexValidator(
                Regulation.VALID_URL_REGEX,
                "Invalid legislation URL."
            ),
        ],
    )

    def __init__(self, regulation_group, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.regulation_group = regulation_group

    def save(self, commit=True):
        instance = super().save(commit)

        if commit:
            self.regulation_group.regulation_set.add(self.instance)

        return instance
