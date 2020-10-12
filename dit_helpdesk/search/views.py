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

from commodities.models import Commodity
from countries.models import Country
from hierarchy.models import Heading, Chapter, SubHeading
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

                logger.info(
                    f"Performed search for {form_data.get('q')}",
                    extra={
                        'search_term': form_data.get('q'),
                        'search_count': context['total_results'],
                    })

                # from elasticsearch_dsl import connections
                # es = connections.get_connection()
                # import ipdb; ipdb.set_trace()

                for hit in context["results"]:
                    if isinstance(hit["commodity_code"], str):
                        index = helpers.get_alias_from_hit(hit)
                        hit.meta["index"] = index

                        if index == "chapter":
                            item = Chapter.objects.get(
                                chapter_code=hit["commodity_code"],
                                goods_nomenclature_sid=hit.id,
                            )
                        elif index == "heading":
                            item = Heading.objects.get(
                                heading_code=hit["commodity_code"],
                                goods_nomenclature_sid=hit.id,
                            )
                        elif index == "subheading":
                            item = SubHeading.objects.get(
                                commodity_code=hit["commodity_code"],
                                goods_nomenclature_sid=hit.id,
                            )
                        elif index == "commodity":
                            item = Commodity.objects.get(
                                commodity_code=hit["commodity_code"],
                                goods_nomenclature_sid=hit.id,
                            )
                        else:
                            item = None

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
            return redirect(reverse("choose-country"))

        country = Country.objects.get(country_code=country_code.upper())

        context["hierarchy_html"] = hierarchy_data(country_code)
        context["country_code"] = country_code.lower()
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
