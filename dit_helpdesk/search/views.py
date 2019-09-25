import json
import logging
import re

from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.edit import FormView
from django_elasticsearch_dsl.search import Search
from django_elasticsearch_dsl_drf.constants import LOOKUP_FILTER_RANGE, LOOKUP_QUERY_IN, LOOKUP_FILTER_TERMS, \
    LOOKUP_FILTER_PREFIX, LOOKUP_FILTER_WILDCARD, LOOKUP_QUERY_EXCLUDE
from django_elasticsearch_dsl_drf.filter_backends import FilteringFilterBackend, OrderingFilterBackend, \
    DefaultOrderingFilterBackend, SearchFilterBackend

from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from elasticsearch import Elasticsearch

from countries.models import Country
from hierarchy.models import Heading
from hierarchy.views import hierarchy_data
from search.documents.chapter import ChapterDocument
from search.documents.commodity import CommodityDocument
from search.documents.heading import HeadingDocument
from search.documents.section import SectionDocument
from search.documents.subheading import SubHeadingDocument
from search.forms import CommoditySearchForm
from search.serializers import CommodityDocumentSerializer, SubHeadingDocumentSerializer, HeadingDocumentSerializer, \
    ChapterDocumentSerializer, SectionDocumentSerializer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def search_hierarchy(request, node_id='root', country_code=None):
    """
    build and return the hierarchy html
    :param request:
    :param node_id:
    :param country_code:
    :return:
    """
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

    def get(self, request, *args, **kwargs):

        self.form = self.get_form(self.form_class)
        context = self.get_context_data(kwargs={"country_code": kwargs["country_code"]})

        if 'q' in self.request.GET:

            if self.form.is_valid():
                query = self.request.GET.get('q')
                context["query"] = query

                client = Elasticsearch(hosts=[settings.ES_URL])

                if query.isdigit():

                    processed_query = process_commodity_code(query)
                    query_object = {"term": {"commodity_code": processed_query}}
                    request = Search().using(client).query(query_object)
                    response = request.execute()

                    hit = response[0]
                    if hit.meta["index"] == "commodity":
                        return redirect(reverse('commodity-detail', kwargs={
                            'commodity_code': hit.commodity_code,
                            'country_code': context['country_code']
                        }))
                    elif hit.meta["index"] == "heading":
                        heading = Heading.objects.filter(heading_code=hit.commodity_code).first()
                        if heading.leaf:
                            return redirect(reverse('heading-detail', kwargs={
                                'heading_code': hit.commodity_code,
                                'country_code': context['country_code']
                            }))
                    else:
                        return redirect(reverse('search:search-hierarchy', kwargs={
                            'node_id': "{0}-{1}".format(hit.meta["index"], hit.id),
                            'country_code': context["country_code"]
                        }))

                else:

                    sort_object = {"ranking": {"order": "desc"}}
                    query_object = {
                            "multi_match": {
                                "query": query,
                                "type": "most_fields",
                                "fields": ["keywords", "description"],
                                "operator": "and" if "," not in query else "or"
                            }
                    }
                    request = Search().using(client).query(query_object).sort(sort_object)

                    page = int(self.request.GET.get('page', '1'))
                    start = (page - 1) * settings.RESULTS_PER_PAGE
                    end = start + settings.RESULTS_PER_PAGE

                    total_results = len(list(request.scan()))
                    total_full_pages = int(total_results / settings.RESULTS_PER_PAGE)
                    orphan_results = total_results % settings.RESULTS_PER_PAGE

                    context["total_pages"] = total_full_pages + 1 if orphan_results > 0 else total_full_pages
                    context['total_results'] = total_results

                    total = request.count()

                    request = request[0:total]
                    response = request[start:end].execute()

                    # filter out duplicate headings and subheadings from the results
                    seen = []
                    results = []

                    for hit in response:
                        if (hit["commodity_code"], hit["description"]) not in seen:
                            results.append(hit)
                        seen.append((hit["commodity_code"], hit["description"]))

                    for hit in results:
                        if isinstance(hit["commodity_code"], str):
                            hit["commodity_code_html"] = _generate_commodity_code_html(hit["commodity_code"])
                            try:
                                hit["hierarchy_context"] = json.loads(hit["hierarchy_context"])
                            except KeyError as exception:
                                logger.info("{0} {1}".format(hit["commodity_code_html"] , exception.args))

                    context["current_page"] = page
                    context["results_per_page"] = settings.RESULTS_PER_PAGE
                    context["next_url"] = "/search/country/{0}/?q={1}&country={2}&page={3}#search-results".format(
                        self.request.GET.get('country'),
                        self.request.GET.get('q'),
                        self.request.GET.get('country'),
                        page+1
                    )
                    context["previous_url"] = "/search/country/{0}/?q={1}&country={2}&page={3}#search-results".format(
                        self.request.GET.get('country'),
                        self.request.GET.get('q'),
                        self.request.GET.get('country'),
                        page-1
                    )
                    context["results"] = results
                    context["page_range_start"] = start if start != 0 else start + 1
                    context["page_range_end"] = end if len(results) == settings.RESULTS_PER_PAGE else start + len(results)
                    context["page_total"] = len(results)
                    return self.render_to_response(context)
            else:
                return self.form_invalid(self.form)
        else:
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

    # Define search fields
    search_fields = (
        'commodity_code',
        'description',
    )


def process_commodity_code(code):

    if len(code) == 1:
        code = "0" + code

    if code in ['00', '99']:
        code = '9999'

    if len(code) == 4 and code[2:] == '00':
        code = code[:2]

    if len(code) == 6 and code[2:] == '0000':
        code = code[:2]

    if len(code) in [3, 5, 7, 9]:
        code = code[:-1]

    if len(code) < 10:

        if len(code) == 2:
            result = code + "00000000"
            return result

        if len(code) == 4:
            result = code + '000000'
            return result

        if len(code) == 6:
            result = code + '0000'
            return result

        if len(code) == 8:
            result = code + "00"
            return result

    elif len(code) > 10:
        result = code[:8] + "00"
        return result

    else:
        print("code: ", code)
        result = code
        return result


def _generate_commodity_code_html(code):
    """
    View helper function that genrates an html representation of the ten digit commodity code broken into three groups
    of 6, 2 and  digits and colour code formatted
    :param item: model instance
    :return: html
    """

    commodity_code_html = '<span class="app-commodity-code app-hierarchy-tree__commodity-code">'

    if len(code) > 2 and code.isdigit():

        code_regex = re.search('([0-9]{2})([0-9]{2})([0-9]{6})', code)
        code_split = [
            code_regex.group(1),
            code_regex.group(2),
            code_regex.group(3)
        ]

        for index, code_segment in enumerate(code_split):
            counter = str(int(index) + 1)
            commodity_code_html = commodity_code_html + \
                                  f'<span class="app-commodity-code__highlight ' \
                                  f'app-commodity-code__highlight--{counter}">{code_segment}</span>'
    else:
        commodity_code_html + code

    commodity_code_html = commodity_code_html + '</span>'

    return commodity_code_html
