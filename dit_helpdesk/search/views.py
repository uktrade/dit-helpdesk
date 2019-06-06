import re
from pprint import pprint

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.forms import forms
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.edit import FormMixin, FormView
from django.contrib import messages
from django_elasticsearch_dsl.search import Search
from django_elasticsearch_dsl_drf.constants import LOOKUP_FILTER_RANGE, LOOKUP_QUERY_IN, LOOKUP_FILTER_TERMS, \
    LOOKUP_FILTER_PREFIX, LOOKUP_FILTER_WILDCARD, LOOKUP_QUERY_EXCLUDE
from elasticsearch import Elasticsearch

from commodities.models import Commodity
from countries.models import Country

from hierarchy.views import hierarchy_data
from hierarchy.models import Chapter, Heading, SubHeading

from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    SearchFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet

from search.documents.chapter import ChapterDocument
from search.documents.commodity import CommodityDocument
from search.documents.heading import HeadingDocument
from search.documents.section import SectionDocument
from search.documents.subheading import SubHeadingDocument
from search.forms import CommoditySearchForm, KeywordSearchForm
from search.serializers import CommodityDocumentSerializer, SubHeadingDocumentSerializer, HeadingDocumentSerializer, ChapterDocumentSerializer, SectionDocumentSerializer


def search_hierarchy(request, node_id='root', country_code=None):
    if country_code is None:
        country_code = request.session.get('origin_country')

    if country_code is None:
        return redirect(reverse('choose-country'))

    country = Country.objects.get(
        country_code=country_code.upper()
    )

    context = {
        'hierarchy_html': hierarchy_data(country_code, node_id),
        'country_code': country_code,
        'selected_origin_country_name': country.name
    }

    return render(request, 'search/commodity_search.html', context)


class CommoditySearchView(FormView):

    form_class = CommoditySearchForm
    template_name = 'search/commodity_search.html'

    def get_success_url(self):
        return '/search/country/{0}'.format(self.kwargs['origin_url'])

    def get(self, request, *args, **kwargs):

        self.form = self.get_form(self.form_class)
        context = self.get_context_data(kwargs={"country_code": kwargs["country_code"]})

        if 'q' in self.request.GET:

            if self.form.is_valid():
                query = self.request.GET.get('q')
                context["query"] = query

                print("Digit: ", query.isdigit())
                print("Not Digit: ", not query.isdigit())

                client = Elasticsearch(hosts=[settings.ES_URL])

                if query.isdigit():

                    query_object = {"term": {"commodity_code": process_commodity_code(query)}}

                    request = Search().using(client).query(query_object)

                else:

                    query_object = {
                            "multi_match": {
                                "query": query,
                                "type": "most_fields",
                                "fields": ["keywords", "description"],
                                "operator": "and" if "," not in query else "or",
                                # "tie_breaker": 0.3,
                            }
                    }
                    sort_object = {"ranking": {"order": "desc"}}
                    request = Search().using(client).query(query_object).sort(sort_object)

                total = request.count()
                context['total'] = total

                request = request[0:total]
                response = request.execute()

                print("response: ", response, len(response), dir(response), response.to_dict())

                seen = []
                results = []

                for hit in response:
                    if (hit["commodity_code"], hit["description"]) not in seen:
                        results.append(hit)
                    seen.append((hit["commodity_code"], hit["description"]))

                print("results: ", results[0].to_dict(), len(results), dir(results[0]), results[0].meta)

                if len(results) == 1:
                    hit = results[0]
                    if hit.meta["index"] == "commodity":
                        return redirect(reverse('commodity-detail', kwargs={
                            'commodity_code': hit.commodity_code,
                            'country_code': context['country_code']
                        }))
                    else:
                        return redirect(reverse('search:search-hierarchy', kwargs={
                            'node_id': "{0}-{1}".format(hit.meta["index"], hit.id),
                            'country_code': context["country_code"]
                        }))

                for hit in results:
                    if isinstance(hit["commodity_code"], str):
                        hit["commodity_code"] = _generate_commodity_code_html(hit["commodity_code"])

                context["results"] = results
                context["total"] = len(results)

                print("returning result:")
                return self.render_to_response(context)
            else:
                print("form not valid")
                return self.form_invalid(self.form)
        else:
            print("query not in request")
            return self.render_to_response(context)

    def get_form(self, form_class=None):
        form = CommoditySearchForm(self.request.GET or form_class)
        return form

    def get_context_data(self, **kwargs):
        context = super(CommoditySearchView, self).get_context_data(**kwargs)

        country_code = self.kwargs['country_code']

        if country_code is None:
            return redirect(reverse('choose-country'))

        country = Country.objects.get(
            country_code=country_code.upper()
        )

        context['hierarchy_html'] = hierarchy_data(country_code)
        context['country_code'] = country_code.lower()
        context['selected_origin_country_name'] = country.name

        return context


class CommodityDocumentViewSet(DocumentViewSet):
    document = CommodityDocument
    serializer_class = CommodityDocumentSerializer

    lookup_field = 'id'
    # filter_backends = [
    #     FilteringFilterBackend,
    #     OrderingFilterBackend,
    #     DefaultOrderingFilterBackend,
    #     SearchFilterBackend,
    # ]

    # Define search fields
    search_fields = (
        'commodity_code',
        'description',
    )

    # # # Filter fields
    # filter_fields = {
    #     'commodity_code': 'commodity_code',
    #     'description': 'description',
    # }
    # #
    # # # Define ordering fields
    # ordering_fields = {
    #     'commodity_code': 'commodity_code',
    #     'description': 'description',
    # }
    # #
    # # # Specify default ordering
    # ordering = ('commodity_code',)


class SearchView(FormView):

    form_class = KeywordSearchForm
    template_name = 'search/search.html'

    def get(self, request, *args, **kwargs):

        self.form = self.get_form(self.form_class)
        context = self.get_context_data(kwargs={"country_code": kwargs["country_code"]})

        if 'q' in self.request.GET:

            if self.form.is_valid():
                query = self.request.GET.get('q')

                print("Digit: ", query.isdigit())
                print("Not Digit: ", not query.isdigit())
                sort_object = None

                client = Elasticsearch(hosts=[settings.ES_URL])

                if query.isdigit():

                    query_object = {"term": {"commodity_code": process_commodity_code(query)}}

                    request = Search().using(client).query(query_object)

                else:

                    query_object = {
                            "multi_match": {
                                "query": query,
                                "type": "most_fields",
                                "fields": ["keywords", "description"],
                                "operator": "and" if "," not in query else "or",
                                # "tie_breaker": 0.3,
                            }
                    }
                    sort_object = {"ranking": {"order": "desc"}}
                    request = Search().using(client).query(query_object).sort(sort_object)

                total = request.count()
                context['total'] = total

                request = request[0:total]
                response = request.execute()

                print("response: ", response, len(response), dir(response), response.to_dict())

                seen = []
                results = []

                for hit in response:
                    if (hit["commodity_code"], hit["description"]) not in seen:
                        results.append(hit)
                    seen.append((hit["commodity_code"], hit["description"]))

                print("results: ", results[0].to_dict(), len(results), dir(results[0]), results[0].meta)

                if len(results) == 1:
                    hit = results[0]
                    if hit.meta["index"] == "commodity":
                        return redirect(reverse('commodity-detail', kwargs={
                            'commodity_code': hit.commodity_code,
                            'country_code': context['country_code']
                        }))
                    else:
                        return redirect(reverse('search:search-hierarchy', kwargs={
                            'node_id': "{0}-{1}".format(hit.meta["index"], hit.id),
                            'country_code': context["country_code"]
                        }))

                for hit in results:
                    hit['commodity_code'] = _generate_commodity_code_html(hit['commodity_code'])

                context["results"] = results
                context["total"] = len(results)

                print("returning result:")
                return self.render_to_response(context)
            else:
                print("form not valid")
                return self.form_invalid(self.form)
        else:
            print("query not in request")
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)

        country_code = self.kwargs['country_code']

        if country_code is None:
            return redirect(reverse('choose-country'))

        country = Country.objects.get(
            country_code=country_code.upper()
        )

        context['country_code'] = country_code.lower()
        context['selected_origin_country_name'] = country.name

        return context

    def get_form(self, form_class=None):
        form = KeywordSearchForm(self.request.GET or form_class)
        return form

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        print("dispatch")
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        print("HANDLER:", handler, args, kwargs)
        return handler(request, *args, **kwargs)


class CommodityViewSet(DocumentViewSet):

    document = CommodityDocument
    serializer_class = CommodityDocumentSerializer

    lookup_field = 'id'

    filter_backends = [
        FilteringFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
    ]

    search_fields = {
        'keywords': {'boost': 4},
        'description': {'boost': 2},
    }

    filter_fields = {
        'id': {
            'field': '_id',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
            ],
        },
        'keywords': {
            'field': 'keywords',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
            ],
        },
        'keywords.raw': {
            'field': 'keywords.raw',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
            ],
        },

        'commodity_code': 'commodity_code'
    }

    # Define ordering fields
    ordering_fields = {
        'id': 'id',
        'keywords': 'keywords.raw',
        'description': 'description',
        'ranking': 'ranking',
    }

    # Specify default ordering
    ordering = ('_score', 'ranking',)


class SectionViewSet(DocumentViewSet):

    document = SectionDocument
    serializer_class = SectionDocumentSerializer

    lookup_field = 'id'

    filter_backends = [
        FilteringFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
    ]

    search_fields = [
        'keywords',
        'title'
    ]

    filter_fields = {
        'id': {
            'field': '_id',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
            ],
        },
        'keywords': {
            'field': 'keywords',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
            ],
        },
        'keywords.raw': {
            'field': 'keywords.raw',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
            ],
        },

        'commodity_code': 'commodity_code.raw'
    }

    # Define ordering fields
    ordering_fields = {
        'id': 'id',
        'keywords': 'keywords.raw',
        'title': 'title.raw',
        'ranking': 'ranking.raw',
    }

    # Specify default ordering
    ordering = ('ranking',)


class ChapterViewSet(DocumentViewSet):

    document = ChapterDocument
    serializer_class = ChapterDocumentSerializer

    lookup_field = 'id'

    filter_backends = [
        FilteringFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
    ]

    search_fields = [
        'keywords',
        'description'
    ]

    filter_fields = {
        'id': {
            'field': '_id',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
            ],
        },
        'keywords': {
            'field': 'keywords',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
            ],
        },
        'keywords.raw': {
            'field': 'keywords.raw',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
            ],
        },

        'commodity_code': 'commodity.raw'
    }

    # Define ordering fields
    ordering_fields = {
        'id': 'id',
        'keywords': 'keywords.raw',
        'description': 'description.raw',
        'ranking': 'ranking.raw',
    }

    # Specify default ordering
    ordering = ('ranking',)


class HeadingViewSet(DocumentViewSet):

    document = HeadingDocument
    serializer_class = HeadingDocumentSerializer

    lookup_field = 'id'

    filter_backends = [
        FilteringFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
    ]

    search_fields = [
        'keywords',
        'description'
    ]

    filter_fields = {
        'id': {
            'field': '_id',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
            ],
        },
        'keywords': {
            'field': 'keywords',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
            ],
        },
        'keywords.raw': {
            'field': 'keywords.raw',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
            ],
        },

        'commodity_code': 'commodity.raw'
    }

    # Define ordering fields
    ordering_fields = {
        'id': 'id',
        'keywords': 'keywords.raw',
        'description': 'description.raw',
        'ranking': 'ranking.raw',
    }

    # Specify default ordering
    ordering = ('ranking',)


class SubHeadingViewSet(DocumentViewSet):

    document = SubHeadingDocument
    serializer_class = SubHeadingDocumentSerializer

    lookup_field = 'id'

    filter_backends = [
        FilteringFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
    ]

    search_fields = [
        'keywords',
        'description'
    ]

    filter_fields = {
        'id': {
            'field': '_id',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
            ],
        },
        'keywords': {
            'field': 'keywords',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
            ],
        },
        'keywords.raw': {
            'field': 'keywords.raw',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
            ],
        },

        'commodity_code': 'commodity.raw'
    }

    # Define ordering fields
    ordering_fields = {
        'id': 'id',
        'keywords': 'keywords.raw',
        'description': 'description.raw',
        'ranking': 'ranking.raw',
    }

    # Specify default ordering
    ordering = ('ranking',)


def process_commodity_code(query):

    if len(query) == 1:
        query = "0" + query

    if query in ['00', '99']:
        query = '9999'

    if len(query) == 4 and query[2:] == '00':
        query = query[:2]

    if len(query) == 6 and query[2:] == '0000':
        query = query[:2]

    if len(query) in [3, 5, 7, 9]:
        query = query[:-1]

    if len(query) > 10:
        query = query[:10]

    if len(query) < 10:

        if len(query) == 2:
            return query + "00000000"

        if len(query) == 4:
            return query + '000000'

        if len(query) == 6:
            return query + '0000'

        if len(query) == 8:
            return query + "00"

    else:
        return query


# This might need to be moved in a better place
def _generate_commodity_code_html(code):
    """
    View helper function that genrates an html representation of the ten digit commodity code broken into three groups
    of 6, 2 and  digits and colour code formatted
    :param item: model instance
    :return: html
    """
    commodity_code_html = '<span class="app-commodity-code app-hierarchy-tree__commodity-code">'

    code_regex = re.search('([0-9]{2})([0-9]{2})([0-9]{6})', code)
    code_split = [
        code_regex.group(1),
        code_regex.group(2),
        code_regex.group(3)
    ]

    for index, code_segment in enumerate(code_split):
        counter = str(int(index) + 1)
        commodity_code_html = commodity_code_html + \
            '<span class="app-commodity-code__highlight app-commodity-code__highlight--' + counter + '">' + code_segment + '</span>'

    commodity_code_html = commodity_code_html + '</span>'

    return commodity_code_html