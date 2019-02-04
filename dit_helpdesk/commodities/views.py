from django.conf import settings
# from django.views.decorators.cache import cache_page
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest #HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

from .models import Commodity

TTS_COUNTRIES = settings.TTS_COUNTRIES


def commodity_detail(request, commodity_code):

    selected_country = request.session.get('origin_country', '').upper()

    if (not selected_country) or selected_country not in TTS_COUNTRIES:
        messages.error(request, 'Invalid originCountry')
        return redirect(reverse('choose-country'))

    commodity = get_object_or_404(
        Commodity, commodity_code=commodity_code,
    )

    context = {
        'selected_origin_country': selected_country,
        'country_options': TTS_COUNTRIES,
        'commodity': commodity
    }
    return render(request, 'commodities/commodity_detail.html', context)


def get_measure_table_data(request, commodity_code, origin_country):

    if origin_country not in settings.TTS_COUNTRIES:
        raise HttpResponseBadRequest('invalid originCode code')

    commodity = get_object_or_404(
        Commodity, commodity_code=commodity_code,
    )
    import_measures = commodity.tts_obj.get_import_measures(origin_country)

    table_data = [
        measure_json.get_vue_table_dict() for measure_json in import_measures
    ]
    table_data.sort(key=lambda di: di['table_rank'])

    return JsonResponse({'gridData': table_data})
