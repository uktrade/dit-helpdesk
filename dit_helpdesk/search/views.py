from django.core.exceptions import ObjectDoesNotExist
from django.forms import forms
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.edit import FormMixin, FormView
from django.contrib import messages

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

from search.documents.commodity import CommodityDocument
from search.forms import CommoditySearchForm
from search.serializers import CommodityDocumentSerializer


def search_hierarchy(request, node_id='root', country_code=None):
    if country_code is None:
        country_code = request.session.get('origin_country')

    context = {
        'hierarchy_html': hierarchy_data(country_code, node_id),
        'country_code': country_code
    }

    return render(request, 'search/commodity_search.html', context)


class CommoditySearchView(FormView):

    form_class = CommoditySearchForm
    template_name = 'search/commodity_search.html'

    def get_success_url(self):
        return '/search/country/{0}'.format(self.kwargs['origin_url'])

    def get(self, request, *args, **kwargs):

        print(request, args, kwargs)
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
                            return redirect(reverse('search-hierarchy', kwargs={
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
                                return redirect(reverse('search-hierarchy', kwargs={
                                    'node_id': 'heading-%s' % Heading.objects.filter(heading_code=code).first().id,
                                    'country_code': context["country_code"]
                                }))
                        elif (Heading.objects.filter(heading_code=code).exists()
                              and SubHeading.objects.filter(commodity_code=code).exists()):

                            if heading.description == subheading.description:
                                print("return 4 sub")
                                return redirect(reverse('search-hierarchy', kwargs={
                                    'node_id': 'sub_heading-%s' % SubHeading.objects.filter(
                                        commodity_code=code).first().id,
                                    'country_code': context["country_code"]
                                }))
                            else:
                                print("return 4 head")
                                return redirect(reverse('search-hierarchy', kwargs={
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
                                return redirect(reverse('search-hierarchy', kwargs={
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
                            return redirect(reverse('search-hierarchy', kwargs={
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
                                return redirect(reverse('search-hierarchy', kwargs={
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
                            return redirect(reverse('search-hierarchy', kwargs={
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
