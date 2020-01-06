import logging
import re

from rest_framework import generics
from rest_framework.response import Response

from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.edit import FormView
from django_elasticsearch_dsl.search import Search

from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from elasticsearch import Elasticsearch

from commodities.models import Commodity
from countries.models import Country
from hierarchy.models import Heading, Chapter, SubHeading
from hierarchy.views import hierarchy_data, _commodity_code_html
from search import helpers
from search.documents.chapter import ChapterDocument
from search.documents.commodity import CommodityDocument
from search.documents.heading import HeadingDocument
from search.documents.section import SectionDocument
from search.documents.subheading import SubHeadingDocument
from search.forms import CommoditySearchForm
from search.serializers import (
    CommodityDocumentSerializer,
    SubHeadingDocumentSerializer,
    HeadingDocumentSerializer,
    ChapterDocumentSerializer,
    SectionDocumentSerializer,
    CommoditySearchSerializer,
    HierarchySearchSerializer,
)


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

    def get_success_url(self, *args, **kwargs):
        success_url = super(CommoditySearchView, self).get_success_url()
        return "{0}?q={1}&country=".format(
            success_url, self.form.cleaned_data["search"]
        )

    def get(self, request, *args, **kwargs):

        context = self.get_context_data(kwargs={"country_code": kwargs["country_code"]})

        if request.GET:
            form = CommoditySearchForm(request.GET)
            if form.is_valid() and "q" in self.request.GET:

                query = request.GET.get("q")
                context["query"] = query
                sort_order = "asc"
                sort_by = request.GET.get("sort")

                if "toggle_headings" not in request.GET.keys():
                    if not request.GET._mutable:
                        request.GET._mutable = True
                        request.GET["toggle_headings"] = "1"

                filter_on_leaf = (
                    True if request.GET.get("toggle_headings") == "1" else False
                )

                if query.isdigit():
                    response = helpers.search_by_code(code=query)
                    if response:
                        hit = response[0]
                        if hit.meta["index"] == "commodity":
                            return redirect(
                                reverse(
                                    "commodity-detail",
                                    kwargs={
                                        "commodity_code": hit.commodity_code,
                                        "country_code": context["country_code"],
                                    },
                                )
                            )
                        elif hit.meta["index"] == "heading":
                            heading = Heading.objects.filter(
                                heading_code=hit.commodity_code
                            ).first()
                            if heading.leaf:
                                return redirect(
                                    reverse(
                                        "heading-detail",
                                        kwargs={
                                            "heading_code": hit.commodity_code,
                                            "country_code": context["country_code"],
                                        },
                                    )
                                )
                            else:
                                return redirect(
                                    reverse(
                                        "search:search-hierarchy",
                                        kwargs={
                                            "node_id": "{0}-{1}".format(
                                                hit.meta["index"], hit.id
                                            ),
                                            "country_code": context["country_code"],
                                        },
                                    )
                                )
                        else:
                            context["message"] = "nothing found for that number"
                            return self.render_to_response(context)
                else:
                    page = int(request.GET.get("page", "1"))
                    sort_by = "ranking" if not sort_by else sort_by
                    sort_order = "desc" if not sort_order else sort_order

                    context.update(
                        helpers.search_by_term(
                            query=query,
                            page=page,
                            sort_by=sort_by,
                            sort_order=sort_order,
                            filter_on_leaf=filter_on_leaf,
                        )
                    )
                    context[
                        "next_url"
                    ] = "/search/country/{0}/?q={1}&country={2}&page={3}#search-results".format(
                        request.GET.get("country"),
                        request.GET.get("q"),
                        request.GET.get("country"),
                        page + 1,
                    )
                    context[
                        "previous_url"
                    ] = "/search/country/{0}/?q={1}&country={2}&page={3}#search-results".format(
                        request.GET.get("country"),
                        request.GET.get("q"),
                        request.GET.get("country"),
                        page - 1,
                    )
                    context["current_page"] = page
                    context["results_per_page"] = settings.RESULTS_PER_PAGE
                    context["page_total"] = len(context["results"])

                    for hit in context["results"]:
                        if isinstance(hit["commodity_code"], str):
                            if hit.meta["index"] == "chapter":
                                item = Chapter.objects.get(
                                    chapter_code=hit["commodity_code"]
                                )
                            elif hit.meta["index"] == "heading":
                                item = Heading.objects.get(
                                    heading_code=hit["commodity_code"]
                                )
                            elif hit.meta["index"] == "subheading":
                                res = SubHeading.objects.filter(
                                    commodity_code=hit["commodity_code"]
                                )

                                item = res.first()
                            else:
                                item = Commodity.objects.get(
                                    commodity_code=hit["commodity_code"]
                                )

                            hit["commodity_code_html"] = _commodity_code_html(item)

                    return self.render_to_response(context)

            else:
                return self.render_to_response(context)
        else:
            return self.render_to_response(context)

    def get_form(self, form_class=None):
        form = CommoditySearchForm(self.request.GET or form_class)
        return form

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
        context = helpers.search_by_term(
            query=serializer.validated_data["q"], page=serializer.validated_data["page"]
        )
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
