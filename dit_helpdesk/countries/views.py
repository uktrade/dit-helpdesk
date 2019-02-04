from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages

TTS_COUNTRIES = settings.TTS_COUNTRIES


def choose_country_view(request):

    if request.method == 'POST':
        origin_country = request.POST['origin_country'].upper()
        if origin_country in TTS_COUNTRIES:
            request.session['origin_country'] = origin_country
            return redirect(reverse('search-view'))
        else:
            messages.error(request, 'Invalid origin_country: %s' % origin_country)

    context = {'country_options': TTS_COUNTRIES}
    return render(request, 'countries/choose_country.html', context)
