from django import forms


class CommoditySearchForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(CommoditySearchForm, self).__init__(*args, **kwargs)
        self.fields['q'].widget.attrs['type'] = "text"
        # self.fields['q'].widget.attrs['max_length'] = 10
        # self.fields['q'].widget.attrs['min_length'] = 4
        self.fields['q'].widget.attrs['id'] = "search"
        self.fields['q'].widget.attrs['class'] = "govuk-input govuk-input--width-20"
        self.fields['q'].error_messages['required'] = "please enter a commodity code"
        self.fields['q'].error_messages['invalid'] = "You have entered text, please enter a commodity code"
        self.fields['q'].widget.attrs['placeholder'] = "Enter a Commodity Code Number"

    q = forms.IntegerField()

    country = forms.CharField(required=True, max_length=2, widget=forms.HiddenInput())

    # def clean(self):
    #     cleaned_data = super(CommoditySearchForm, self).clean()
    #     # q = cleaned_data['q']
    # #     country = cleaned_data['country']
    #     print("cleaned_data: ", cleaned_data)
    # #     if len(q) == 0 or q is None:
    # #         raise forms.ValidationError('Enter a commodity code')
    #     if not isinstance(q, int):
    #         raise forms.ValidationError('You have entered text, please enter a commodity code')
