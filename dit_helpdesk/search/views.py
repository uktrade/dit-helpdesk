"""
Work in progress custom search view
"""

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from commodities.models import Commodity
from countries.models import Country


def search_view(request):

    countries = Country.objects.all()

    # context = {
    #     'country_options': [(c.country_code, c.name) for c in countries],
    # }

    # for country in context['country_options']:
    #     if country[0] == request.session['origin_country']:
    #         context['currently_selected_country'] = country

    if 'q'not in request.GET:
        # return render(request, 'search/commodity_search.html', context)
        return render(request, 'search/commodity_search.html')

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

    # return render(request, 'countries/choose_country.html', context)
