from django import forms

SORT_CHOICES = (("ranking", "Relevance"), ("commodity_code", "Code"))
TOGGLE_CHOICES = ((0, "All Results"), (1, "Complete commodity codes only"))
SORT_ORDER = (("desc", "Descending"), ("asc", "Ascending"))


class CommoditySearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CommoditySearchForm, self).__init__(*args, **kwargs)

        self.fields["q"].widget.attrs["id"] = "search"
        self.fields["q"].widget.attrs["class"] = "govuk-input govuk-input--width-20"

        self.fields["q"].error_messages[
            "required"
        ] = "required: please enter a commodity code or search term"

        self.fields["q"].error_messages[
            "invalid"
        ] = "invalid: please enter a commodity code or search term"

        self.fields["q"].widget.attrs[
            "placeholder"
        ] = "Enter a Commodity Code or Search Term"

        self.fields["sort"].widget.attrs["id"] = "sort"
        self.fields["q"].widget.attrs["class"] = "govuk-select"

        self.fields["sort"].initial = "ranking"
        self.fields["sort_order"].initial = "desc"
        self.fields["toggle_headings"].initial = 0
        self.fields["page"].initial = 1

    q = forms.CharField()
    toggle_headings = forms.ChoiceField(
        choices=TOGGLE_CHOICES, widget=forms.HiddenInput
    )
    sort = forms.ChoiceField(choices=SORT_CHOICES, widget=forms.HiddenInput)
    sort_order = forms.ChoiceField(choices=SORT_ORDER, widget=forms.HiddenInput)
    page = forms.CharField(widget=forms.HiddenInput())
    country = forms.CharField(widget=forms.HiddenInput())
