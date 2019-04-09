from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from countries.models import Country


def choose_country_view(request):
    countries = Country.objects.all()
    COUNTRY_NOT_SELECTED_SUMMARY_ERROR_MESSAGE = 'Enter a country'
    COUNTRY_NOT_SELECTED_INPUR_ERROR_MESSAGE = 'Enter a country'
    if request.session.has_key('origin_country'):
        selected_country = request.session['origin_country']
    else:
        selected_country = False

    if request.method == 'POST':
        origin_country = request.POST.get('origin_country', '').strip().upper()
        if origin_country and Country.objects.filter(country_code=origin_country).exists():
            request.session['origin_country'] = origin_country
            return redirect(reverse('search-view') + 'country/' + origin_country.lower())
        else:
            context = {
                'country_options': [(c.country_code, c.name) for c in countries],
                'isError': True,
                'errorSummaryMessage' : COUNTRY_NOT_SELECTED_SUMMARY_ERROR_MESSAGE,
                'errorInputMessage' : COUNTRY_NOT_SELECTED_INPUR_ERROR_MESSAGE,
            }
            return render(request, 'countries/choose_country.html', context)

    context = {
        'country_options': [(c.country_code, c.name) for c in countries],
        'selected_country': selected_country
    }
    return render(request, 'countries/choose_country.html', context)
