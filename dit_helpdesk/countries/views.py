from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from countries.models import Country


# @login_required
def choose_country_view(request):

    if request.method == 'POST':
        origin_country = request.POST.get('origin_country', '').strip().upper()
        if origin_country and Country.objects.filter(country_code=origin_country).exists():
            request.session['origin_country'] = origin_country
            return redirect(reverse('search-view'))
        else:
            messages.error(request, 'Invalid origin_country: %s' % origin_country)

    countries = Country.objects.all()
    context = {
        'country_options': [(c.country_code, c.name) for c in countries]
    }
    return render(request, 'countries/choose_country.html', context)
