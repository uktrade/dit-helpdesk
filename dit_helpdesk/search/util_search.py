
from django import forms
from django.conf import settings
from django.urls import reverse

from haystack.forms import SearchForm
from haystack.generic_views import SearchView

# from requirements_documents.middleware import RedirectException
# from requirements_documents.models import Commodity, SubHeading, Heading

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

from haystack.query import SearchQuerySet
from django.db.models import Q


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

    template = "search/search.html"
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

    def get_context_data__hierarchical_search_prototype(self, *args, **kwargs):

        context = super(CommoditySearchView, self).get_context_data(*args, **kwargs)

        if not self.request.GET.get('q'):
            return context

        context['object_list'] = [o for o in context['object_list'] if o.model is Heading]

        context['page_obj'].object_list = [
            o for o in context['page_obj'].object_list if o.model is Heading
        ]

        commodity_pks, subheading_pks = [], []
        for result_item in context['object_list']:
            heading = result_item.object
            for model_name, pk in heading.get_commodity_keys_flattened():
                if model_name == 'Commodity':
                    commodity_pks.append(pk)
                elif model_name == 'SubHeading':
                    subheading_pks.append(pk)

        query_str = self.request.GET['q']
        related_items = SearchQuerySet().models(Commodity, SubHeading).filter(
            Q(commodity_pk__in=commodity_pks) | Q(subheading_pk__in=subheading_pks)).filter(
            content=query_str)

        related_items_by_key = {}
        for result_item in related_items:
            key = (result_item.object.__class__.__name__, result_item.object.pk)
            related_items_by_key[key] = result_item.object

        return context
