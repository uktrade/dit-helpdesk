from django import forms


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

    q = forms.CharField()

    country = forms.CharField(required=True, max_length=2, widget=forms.HiddenInput())
