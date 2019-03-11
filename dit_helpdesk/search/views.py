"""
Work in progress custom search view
"""

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from commodities.models import Commodity
from countries.models import Country

from hierarchy.views import hierarchy_data


def search_hierarchy(request, node_id='root', country_code=None):
    if country_code is None:
        country_code = request.session.get('origin_country')

    context = hierarchy_data(country_code, node_id)
    return render(request, 'search/commodity_search.html', context)


def search_view(request):
    countries = Country.objects.all()

    if 'q' not in request.GET:
        context = hierarchy_data(request.session.get('origin_country'))
        return render(request, 'search/commodity_search.html', context)

    query = request.GET['q'].strip()

    if len(query) == 10 and query.isdigit():
        code = query

        if Commodity.objects.filter(commodity_code=code).exists():
            return redirect(reverse(
                'commodity-detail', kwargs={'commodity_code':code,
                                            'country_code': request.session.get('origin_country')}
            ))
        else:
            #messages.error('Commodity "%s" not found' % code)
            return redirect(reverse('search-view'))
    else:
        #print('else')
        #messages.error('Expected 10-digit code')
        return redirect(reverse('search-view'))

    return render(request, 'countries/choose_country.html', context)
