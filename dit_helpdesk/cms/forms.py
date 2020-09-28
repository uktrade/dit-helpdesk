from django import forms


class RegulationSearchForm(forms.Form):
    q = forms.CharField(label="Search regulations")
