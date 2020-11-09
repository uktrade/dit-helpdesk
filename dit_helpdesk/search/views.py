import logging
import re
from urllib.parse import urlencode

from rest_framework import generics
from rest_framework.response import Response

from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.edit import FormView

from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet

from analytics.track import track_event
from countries.models import Country
from hierarchy.models import Chapter, Heading
from hierarchy.views import hierarchy_data, _commodity_code_html
from search import helpers

from search.documents.commodity import CommodityDocument
from search.forms import CommoditySearchForm
from search.serializers import (
    CommodityDocumentSerializer,
    CommoditySearchSerializer,
    HierarchySearchSerializer,
)


logger = logging.getLogger(__name__)


def search_hierarchy(request, node_id="root", country_code=None):
    """
    build and return the hierarchy html
    :param request:
    :param node_id:
    :param country_code:
    :return:
    """
    if country_code is None:
        country_code = request.session.get("origin_country")

    if country_code is None:
        return redirect(reverse("choose-country"))

    country = Country.objects.get(country_code=country_code.upper())

    context = {
        "hierarchy_html": hierarchy_data(country_code, node_id),
        "country_code": country_code,
        "selected_origin_country_name": country.name,
    }

    return render(request, "search/commodity_search.html", context)


class CommoditySearchView(FormView):

    form_class = CommoditySearchForm
    template_name = "search/commodity_search.html"

    EMPTY_RESULTS_SUFFIX = " (no results)"

    def get_initial(self):
        initial = super(CommoditySearchView, self).get_initial()
        country_code = self.kwargs.get("country_code")
        initial["country"] = country_code.lower()
        return initial

    def get(self, request, *args, **kwargs):
        self.initial = self.get_initial()
        form = self.form_class(request.GET)

        context = self.get_context_data(kwargs={"country_code": kwargs["country_code"]})
        context["title_suffix"] = ""

        if form.is_valid():

            form_data = form.cleaned_data

            page = int(form_data.get("page")) if form_data.get("page") else 1

            normalised_q = helpers.normalise_commodity_code(form_data.get("q"))
            if normalised_q.isdigit():
                response = helpers.search_by_code(code=normalised_q)
                hits = [hit for hit in response.scan()]

                if hits:
                    hit = hits[0]
                    item = helpers.get_object_from_hit(hit)
                    hit.meta["index"] = helpers.get_alias_from_hit(hit)

                    country_code = form_data.get("country")

                    try:
                        return redirect(item.get_detail_url(country_code))
                    except helpers.ObjectNotFoundFromHit:
                        # response for no results found for commodity code
                        context["message"] = "nothing found for that number"
                        context["results"] = []
                        context["title_suffix"] = self.EMPTY_RESULTS_SUFFIX
                        return self.render_to_response(context)
                else:
                    context["results"] = []
                    context["title_suffix"] = self.EMPTY_RESULTS_SUFFIX
                    return self.render_to_response(context)
            else:
                context.update(helpers.search_by_term(form_data=form_data))

                curr_url_items = dict((x, y) for x, y in request.GET.items())

                next_urls_items = curr_url_items.copy()
                next_urls_items["page"] = str(int(next_urls_items["page"]) + 1)

                prev_url_items = curr_url_items.copy()
                prev_url_items["page"] = str(int(prev_url_items["page"]) - 1)

                context["next_url"] = "?{0}".format(urlencode(next_urls_items))
                context["previous_url"] = "?{0}".format(urlencode(prev_url_items))
                context["current_page"] = page
                context["results_per_page"] = settings.RESULTS_PER_PAGE
                context["page_total"] = len(context["results"])

                if not context["results"]:
                    context["title_suffix"] = self.EMPTY_RESULTS_SUFFIX

                search_term = form_data.get('q')
                total_results = context['total_results']

                logger.info(
                    f"Performed search for {search_term}",
                    extra={
                        'search_term': search_term,
                        'search_count': total_results,
                    })

                track_event(
                    "search",
                    "results",
                    search_term,
                    total_results,
                )

                for hit in context["results"]:
                    if isinstance(hit["commodity_code"], str):
                        try:
                            item = helpers.get_object_from_hit(hit)
                        except helpers.ObjectNotFoundFromHit:
                            item = None

                        hit.meta["index"] = helpers.get_alias_from_hit(hit)
                        hit["commodity_code_html"] = _commodity_code_html(item)

                return self.render_to_response(context)

        else:

            if "q" in request.GET.keys() and form.has_error("q"):
                context["form_q_error"] = True
                error_data = form.errors.as_data()
                context["form_q_validation_message"] = error_data["q"][0]

            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(CommoditySearchView, self).get_context_data(**kwargs)

        country_code = self.kwargs["country_code"]

        if country_code is None:
            return redirect(reverse("choose-country-old"))

        country = Country.objects.get(country_code=country_code.upper())

        context["hierarchy_html"] = hierarchy_data(country_code)
        context["country_code"] = country_code.lower()
        context["selected_origin_country"] = country_code.lower()
        context["selected_origin_country_name"] = country.name

        return context


def _construct_result(item):
    """Constructs a dictionary which is mostly compatible with ElasticSearch Hit and
    can be used in it's place in templates

    """

    result = {
        "description": item.description,
        "id": item.goods_nomenclature_sid,
        "commodity_code": item.commodity_code,
        "commodity_code_html": _commodity_code_html(item, ignore_duplicate=False),
    }

    return result


class GroupedCommoditySearchView(FormView):

    form_class = CommoditySearchForm
    template_name = "search/grouped_commodity_search.html"

    EMPTY_RESULTS_SUFFIX = " (no results)"

    def get_initial(self):
        initial = super(GroupedCommoditySearchView, self).get_initial()
        country_code = self.kwargs.get("country_code")
        initial["country"] = country_code.lower()
        return initial

    def get(self, request, *args, **kwargs):

        self.initial = self.get_initial()
        form = self.form_class(request.GET)

        context = self.get_context_data(
            kwargs={
                "country_code": kwargs["country_code"],
                "selected_origin_country": kwargs["country_code"]
            })
        context["title_suffix"] = ""

        if form.is_valid():

            form_data = form.cleaned_data

            normalised_q = helpers.normalise_commodity_code(form_data.get("q"))
            if normalised_q.isdigit():
                response = helpers.search_by_code(code=normalised_q)
                hits = [hit for hit in response.scan()]

                if hits:
                    hit = hits[0]
                    index = helpers.get_alias_from_hit(hit)
                    hit.meta["index"] = index

                    if index == "chapter":
                        return redirect(
                            reverse(
                                "chapter-detail",
                                kwargs={
                                    "chapter_code": hit.commodity_code,
                                    "country_code": form_data.get("country"),
                                    "nomenclature_sid": hit.id,
                                },
                            )
                        )
                    elif index == "commodity":
                        return redirect(
                            reverse(
                                "commodity-detail",
                                kwargs={
                                    "commodity_code": hit.commodity_code,
                                    "country_code": form_data.get("country"),
                                    "nomenclature_sid": hit.id,
                                },
                            )
                        )
                    elif index == "heading":
                        return redirect(
                            reverse(
                                "heading-detail",
                                kwargs={
                                    "heading_code": hit.commodity_code,
                                    "country_code": form_data.get("country"),
                                    "nomenclature_sid": hit.id,
                                },
                            )
                        )

                    elif index == "subheading":
                        return redirect(
                            reverse(
                                "subheading-detail",
                                kwargs={
                                    "commodity_code": hit.commodity_code,
                                    "country_code": form_data.get("country"),
                                    "nomenclature_sid": hit.id,
                                },
                            )
                        )

                    else:
                        # response for no results found for commodity code
                        context["message"] = "nothing found for that number"
                        context["results"] = []
                        context["title_suffix"] = self.EMPTY_RESULTS_SUFFIX
                        return self.render_to_response(context)
                else:
                    context["results"] = []
                    context["title_suffix"] = self.EMPTY_RESULTS_SUFFIX
                    return self.render_to_response(context)
            else:

                grouped_context = helpers.group_search_by_term(form_data=form_data)
                grouped_hits = grouped_context["grouped_hits"]
                chapter_sort_order = grouped_context["chapter_sort_order"]
                heading_sort_order = grouped_context["heading_sort_order"]

                context.update(grouped_context)

                chapters = Chapter.objects.filter(
                    chapter_code__in=grouped_context["group_chapters"]
                ).order_by('chapter_code').all()

                headings = Heading.objects.filter(
                    heading_code__in=grouped_context["group_headings"]
                ).order_by("heading_code").all()

                # to facilitate lookup
                chapters_dict = {ch.chapter_code: ch for ch in chapters}
                headings_dict = {h.heading_code: h for h in headings}

                results = []
                for chapter_code in chapter_sort_order:
                    chapter = chapters_dict[chapter_code]
                    chapter_result = _construct_result(chapter)
                    chapter_result["headings"] = []

                    heading_codes = grouped_hits[chapter.commodity_code].keys()
                    heading_codes = sorted(heading_codes)

                    headings_in_chapter_order = [
                        heading_code for heading_code in heading_sort_order
                        if heading_code in heading_codes
                    ]

                    for heading_code in headings_in_chapter_order:
                        heading = headings_dict[heading_code]
                        heading_result = _construct_result(heading)
                        chapter_result["headings"].append(heading_result)

                    results.append(chapter_result)

                if not results:
                    context["title_suffix"] = self.EMPTY_RESULTS_SUFFIX

                context["results"] = results

                logger.info(
                    f"Performed search for {form_data.get('q')}",
                    extra={
                        'search_term': form_data.get('q'),
                        'search_count': context['total_results'],
                    })

                return self.render_to_response(context)

        else:

            if "q" in request.GET.keys() and form.has_error("q"):
                context["form_q_error"] = True
                error_data = form.errors.as_data()
                context["form_q_validation_message"] = error_data["q"][0]

            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(GroupedCommoditySearchView, self).get_context_data(**kwargs)

        country_code = self.kwargs["country_code"]

        if country_code is None:
            return redirect(reverse("choose-country"))

        country = Country.objects.get(country_code=country_code.upper())

        context["hierarchy_html"] = hierarchy_data(country_code)
        context["country_code"] = country_code.lower()
        context["selected_origin_country"] = country_code.lower()
        context["selected_origin_country_name"] = country.name

        return context


class CommodityTermSearchAPIView(generics.ListAPIView):
    serializer_class = CommoditySearchSerializer
    permission_classes = []
    authentication_classes = []

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = {
            'q': serializer.validated_data["q"],
            'page': serializer.validated_data["page"],
            'sort': 'ranking',
            'sort_order': 'desc', 
        }
        context = helpers.search_by_term(form_data=data)
        context["results"] = [hit.to_dict() for hit in context["results"]]
        return Response(context)


class CommodityCodeSearchAPIView(generics.ListAPIView):
    serializer_class = CommoditySearchSerializer
    permission_classes = []
    authentication_classes = []

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        context = helpers.search_by_code(code=serializer.validated_data["q"])
        return Response({"results": [hit.to_dict() for hit in context]})


class HierarchySearchAPIView(generics.ListAPIView):
    serializer_class = HierarchySearchSerializer
    permission_classes = []
    authentication_classes = []

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        hierarchy = hierarchy_data(
            country_code=serializer.validated_data["country_code"],
            node_id=serializer.validated_data["node_id"],
            content_type="json",
        )
        return Response({"results": hierarchy})


class CommodityDocumentViewSet(DocumentViewSet):
    document = CommodityDocument
    serializer_class = CommodityDocumentSerializer

    lookup_field = "id"

    # Define search fields
    search_fields = ("commodity_code", "description")
