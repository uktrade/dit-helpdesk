import json

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages

from commodities.models import Commodity
from countries.models import Country
from trade_tariff_service.tts_api import COMMODITY_DETAIL_TABLE_KEYS


ROO_FP = 'rules_of_origin/management/commands/roo.json'
RULES_OF_ORIGIN_DATA = json.loads(open(ROO_FP).read())

TABLE_COLUMN_TITLES = [
    tup[1] for tup in COMMODITY_DETAIL_TABLE_KEYS
]

'''
example commodities with rules of origin:

0403103900
0403101300
0403101900
0403103100
0403103300
1106309080
1106100000
0901110000
0901120000
0910911000
'''


def commodity_detail(request, commodity_code):

    selected_country = request.session.get('origin_country', '').upper()
    country_exists = False
    if selected_country:
        country_exists = Country.objects.filter(
            country_code=selected_country
        ).exists()

    if (not selected_country) or (not country_exists):
        messages.error(request, 'Invalid originCountry')
        return redirect(reverse('choose-country'))

    commodity = get_object_or_404(
        Commodity, commodity_code=commodity_code,
    )

    heading = commodity.get_heading()
    heading_code = heading.heading_code[:4]
    chapter_code = heading.chapter.chapter_code[:2]

    import_measures = commodity.tts_obj.get_import_measures(selected_country)
    table_data = [
        measure_json.get_table_row() for measure_json in import_measures
    ]

    roo_keys = [
        'heading__'+heading_code, 'heading_exclusion__'+heading_code,
        'chapter__'+chapter_code, 'chapter_exclusion__'+chapter_code
    ]
    roo_fragments = []
    for key in roo_keys:
        if key in RULES_OF_ORIGIN_DATA:
            roo_fragments.extend(RULES_OF_ORIGIN_DATA[key])

    context = {
        'selected_origin_country': selected_country, 'commodity': commodity,
        'roo_fragments': roo_fragments, 'table_data': table_data,
        'column_titles': TABLE_COLUMN_TITLES,
    }
    return render(request, 'commodities/commodity_detail.html', context)


'''
old vue.js ajax call:

def get_measure_table_data(request, commodity_code, origin_country):

    if not Country.objects.filter(country_code=origin_country).exists():
        raise HttpResponseBadRequest('invalid originCountry code')

    commodity = get_object_or_404(
        Commodity, commodity_code=commodity_code,
    )
    import_measures = commodity.tts_obj.get_import_measures(origin_country)

    table_data = [
        measure_json.get_vue_table_dict() for measure_json in import_measures
    ]
    table_data.sort(key=lambda di: di['table_rank'])

    return JsonResponse({'gridData': table_data})
'''