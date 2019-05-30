from pprint import pprint

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

        # print("get context", context)
        if 'q' in self.request.GET:

            if self.form.is_valid():
                query = self.request.GET.get('q')

                if not query.isdigit():
                    context['is_error'] = True
                    context["error_summary_message"] = "Enter a commodity code"

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
                        code = query + "00000000"

                        if Chapter.objects.filter(chapter_code=code).exists():
                            print("returning chapter")
                            return redirect(reverse('search:search-hierarchy', kwargs={
                                'node_id': 'chapter-%s' % Chapter.objects.filter(chapter_code=code).first().id,
                                'country_code': context["country_code"]
                            }))
                        else:
                            print("returning chapter error")
                            context["is_error"] = True,
                            context["error_summary_message"] = "Enter a commodity code"
                            return self.render_to_response(self.get_context_data(kwargs={

                            }))

                    elif len(query) == 4:
                        code = query + '000000'

                        heading = Heading.objects.filter(heading_code=code).first()
                        subheading = SubHeading.objects.filter(commodity_code=code).first()
                        commodity = Commodity.objects.filter(commodity_code=code).first()

                        if (Heading.objects.filter(heading_code=code).exists()
                                and Commodity.objects.filter(commodity_code=code).exists()):

                            if heading.description == commodity.description:
                                print("return 4 com")
                                return redirect(reverse('commodity-detail', kwargs={
                                    'commodity_code': code,
                                    'country_code': context['country_code']
                                }))

                            else:
                                print("return 4 head")
                                return redirect(reverse('search:search-hierarchy', kwargs={
                                    'node_id': 'heading-%s' % Heading.objects.filter(heading_code=code).first().id,
                                    'country_code': context["country_code"]
                                }))
                        elif (Heading.objects.filter(heading_code=code).exists()
                              and SubHeading.objects.filter(commodity_code=code).exists()):

                            if heading.description == subheading.description:
                                print("return 4 sub")
                                return redirect(reverse('search:search-hierarchy', kwargs={
                                    'node_id': 'sub_heading-%s' % SubHeading.objects.filter(
                                        commodity_code=code).first().id,
                                    'country_code': context["country_code"]
                                }))
                            else:
                                print("return 4 head")
                                return redirect(reverse('search:search-hierarchy', kwargs={
                                    'node_id': 'heading-%s' % Heading.objects.filter(heading_code=code).first().id,
                                    'country_code': context["country_code"]
                                }))
                        print("return 4 error")
                        context["is_error"] = True,
                        context["error_summary_message"] = "Enter a commodity code"
                        return self.render_to_response(context)

                    elif len(query) == 6:
                        code = query + '0000'

                        subheading = SubHeading.objects.filter(commodity_code=code).first()
                        commodity = Commodity.objects.filter(commodity_code=code).first()

                        if (SubHeading.objects.filter(commodity_code=code).exists() and
                                Commodity.objects.filter(commodity_code=code).exists()):

                            if subheading.description == commodity.description:
                                print("returning 6 com")
                                return redirect(reverse('commodity-detail', kwargs={
                                    'commodity_code': code,
                                    'country_code': context['country_code']
                                }))
                            else:
                                print("returning 6 sub")
                                return redirect(reverse('search:search-hierarchy', kwargs={
                                    'node_id': 'sub_heading-%s' % SubHeading.objects.filter(
                                        commodity_code=code).first().id,
                                    'country_code': context["country_code"]
                                }))
                        elif (Commodity.objects.filter(commodity_code=code).exists() and not
                                SubHeading.objects.filter(commodity_code=code).exists()):
                            print("returning 6 com 2")
                            return redirect(reverse('commodity-detail', kwargs={
                                'commodity_code': code,
                                'country_code': context['country_code']
                            }))

                        elif (SubHeading.objects.filter(commodity_code=code).exists() and not
                                Commodity.objects.filter(commodity_code=code).exists()):
                            print("returning 6 sub 2")
                            return redirect(reverse('search:search-hierarchy', kwargs={
                                'node_id': 'sub_heading-%s' % SubHeading.objects.filter(
                                    commodity_code=code).first().id,
                                'country_code': context["country_code"]
                            }))

                        else:
                            print("returning 6 err")
                            context["is_error"] = True
                            context["error_summary_message"] = "Code Not Found"
                            return self.render_to_response(context)

                    elif len(query) == 8:
                        code = query + "00"

                        subheading = SubHeading.objects.filter(commodity_code=code).first()
                        commodity = Commodity.objects.filter(commodity_code=code).first()

                        if (SubHeading.objects.filter(commodity_code=code).exists() and
                                Commodity.objects.filter(commodity_code=code).exists()):

                            if subheading.description == commodity.description:
                                print("returning 8 com")
                                return redirect(reverse('commodity-detail', kwargs={
                                    'commodity_code': code,
                                    'country_code': context['country_code']
                                }))
                            else:
                                print("returning 8 sub")
                                return redirect(reverse('search:search-hierarchy', kwargs={
                                    'node_id': 'sub_heading-%s' % SubHeading.objects.filter(
                                        commodity_code=code).first().id,
                                    'country_code': context["country_code"]
                                }))
                        elif (Commodity.objects.filter(commodity_code=code).exists() and not
                                SubHeading.objects.filter(commodity_code=code).exists()):
                            print("returning 8 com 2")
                            return redirect(reverse('commodity-detail', kwargs={
                                'commodity_code': code,
                                'country_code': context['country_code']
                            }))

                        elif (SubHeading.objects.filter(commodity_code=code).exists() and not
                                Commodity.objects.filter(commodity_code=code).exists()):
                            print("returning 8 sub 2")
                            return redirect(reverse('search:search-hierarchy', kwargs={
                                'node_id': 'sub_heading-%s' % SubHeading.objects.filter(
                                    commodity_code=code).first().id,
                                'country_code': context["country_code"]
                            }))

                        else:
                            print("returning 8 err")
                            context["is_error"] = True
                            context["error_summary_message"] = "Code Not Found"
                            return self.render_to_response(context)

                    else:
                        print("returning else")
                        context["is_error"] = True,
                        context["error_summary_message"] = "Code Not Found"
                        return self.render_to_response(context)

                else:
                    context['commodity_code'] = query

                    if Commodity.objects.filter(commodity_code=query).exists():
                        print("returning com 10")
                        return redirect(reverse('commodity-detail', kwargs={
                            'commodity_code': context['commodity_code'],
                            'country_code': context['country_code']}
                        ))

            else:
                print("returning invalid form response")
                return self.form_invalid(self.form)

            print("returning context")
            return self.render_to_response(context)

        else:

            print("returning context")
            return self.render_to_response(context)

    def get_form(self, form_class=None):
        form = CommoditySearchForm(self.request.GET or None)
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

                client = Elasticsearch(hosts=["es"])

                search = Search().using(client).query("match", keywords=query).sort({"ranking": {"order": "desc"}})

                total = search.count()
                context['total'] = total
                search = search[0:total]
                results = search.execute()

                for hit in search:
                    print("Commodity Code: {0} , ".format(hit.commodity_code))
                    print("Description: {0}".format(hit.description))
                    print("Id: {0}".format(hit.id))
                    print("keywords: {0}".format(hit.keywords))
                    print("meta: {0}".format(hit.meta))
                    print("ranking: {0}".format(hit.ranking))

                    print(dir(hit))

                context["results"] = results

                return self.render_to_response(context)
            else:
                print("Search: returning invalid form")
                return self.form_invalid(self.form)
        else:
            print("Search: empty form")
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