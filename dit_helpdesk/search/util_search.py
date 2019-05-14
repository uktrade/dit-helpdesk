
from django.db.models import Q
from haystack.forms import SearchForm
from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet

from hierarchy.models import Heading

'''
class CommoditySearchForm(SearchForm):

    origin_country = forms.CharField(required=True, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(CommoditySearchForm, self).__init__(*args, **kwargs)

    def search(self):

        origin_country = self.request.session.get('origin_country', '').upper()
        if origin_country not in settings.TTS_COUNTRIES:
            # todo: add error message for user
            raise RedirectException(reverse('choose-country'))

        sqs = super(CommoditySearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()

        return sqs.filter(origin_country=origin_country)
'''


class HeadingSearchForm(SearchForm):
    models = [
        Heading
    ]

    def get_models(self):
        return self.models

    def search(self):
        sqs = super(HeadingSearchForm, self).search().models(*self.get_models())
        return sqs


class CommoditySearchView(SearchView):
    """ Use this to customise search form"""

    template = "search/search_results.html"
    form = HeadingSearchForm

    def build_form(self, form_kwargs=None):
        super(CommoditySearchView, self).build_form(
            form_kwargs=form_kwargs
        )

    def get_queryset(self):
        queryset = super(CommoditySearchView, self).get_queryset().models(Heading)  # .filter(model_name='Headings')
        return queryset

    def get_context_data(self, *args, **kwargs):
        return super(CommoditySearchView, self).get_context_data(*args, **kwargs)

