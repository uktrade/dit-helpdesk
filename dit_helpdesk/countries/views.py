from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from countries.models import Country


def choose_country_view(request):
    if request.session.has_key('origin_country'):
        selected_country = request.session['origin_country']
    else:
        selected_country = False

    if request.method == 'POST':
        origin_country = request.POST.get('origin_country', '').strip().upper()
        if origin_country and Country.objects.filter(country_code=origin_country).exists():
            request.session['origin_country'] = origin_country
            return redirect(reverse('search-view'))
        else:
            messages.error(request, 'Invalid origin_country: %s' % origin_country)

    countries = Country.objects.all()
    context = {
        'country_options': [(c.country_code, c.name) for c in countries],
        'selected_country': selected_country
    }
    return render(request, 'countries/choose_country.html', context)
