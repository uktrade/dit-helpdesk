import json
import re
import datetime
import os

# from django.views.decorators.cache import cache_page
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from commodities.models import Commodity
from countries.models import Country
from trade_tariff_service.tts_api import COMMODITY_DETAIL_TABLE_KEYS

ROO_FP = os.path.join(
    settings.BASE_DIR, 'rules_of_origin/management/commands/roo.json'
)

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

@login_required
def commodity_detail(request, commodity_code):

    selected_country = request.session.get('origin_country', '').upper()

    country = Country.objects.filter(
        country_code=selected_country
    )

    country_exists = False

    country_name = country.values()[0]['name']

    if selected_country:
        country_exists = country.exists()

    if (not selected_country) or (not country_exists):
        messages.error(request, 'Invalid originCountry')
        return redirect(reverse('choose-country'))

    commodity = get_object_or_404(
        Commodity, commodity_code=commodity_code,
    )

    commodity_code_regex = re.search('([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})', commodity.commodity_code)

    commodity_code_split = [
        commodity_code_regex.group(1),
        commodity_code_regex.group(2),
        commodity_code_regex.group(3),
        commodity_code_regex.group(4)
    ]

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
            for html_fragment in RULES_OF_ORIGIN_DATA[key]:
                html_fragment = html_fragment.replace(
                    '<td class="table" valign="top">',
                    '<td class="govuk-table__cell app-table__cell">'
                )
                roo_fragments.append(html_fragment)

    context = {
        'selected_origin_country': selected_country, 'commodity': commodity,
        'selected_origin_country_name': country_name,
        'commodity_code': commodity_code_split,
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