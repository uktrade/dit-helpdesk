from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from commodities.models import Commodity
from countries.models import Country

from hierarchy.views import hierarchy_data


def search_hierarchy(request, node_id='root', country_code=None):
    if country_code is None:
        country_code = request.session.get('origin_country')

    print(hierarchy_data(country_code, node_id))
    context = {
        'hierarchy_html': hierarchy_data(country_code, node_id),
        'country_code': country_code
    }

    return render(request, 'search/commodity_search.html', context)


def search_view(request, country_code=None):
    if country_code is None:
        if 'country' in request.GET:
            country_code = request.GET['country']
        else:
            return redirect(reverse('choose-country'))

    countries = Country.objects.all()

    if 'q' not in request.GET:
        context = {
            'hierarchy_html': hierarchy_data(country_code),
            'country_code' : country_code
        }

        return render(request, 'search/commodity_search.html', context)

    query = request.GET['q'].strip()

    if len(query) == 10 and query.isdigit():
        code = query

        if Commodity.objects.filter(commodity_code=code).exists():
            return redirect(reverse(
                'commodity-detail', kwargs={'commodity_code':code,
                                            'country_code': country_code.lower() }
            ))
        else:
            #messages.error('Commodity "%s" not found' % code)
            return redirect(reverse('search-view'))
    else:
        #print('else')
        #messages.error('Expected 10-digit code')
        return redirect(reverse('search-view'))

    return render(request, 'countries/choose_country.html', context)
