from django.conf import settings
# from django.views.decorators.cache import cache_page
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest #HttpResponseRedirect
import requests

from .models import Section, Commodity, RequirementDocument, EuTradeHelpdeskDocument, Heading

TTS_COUNTRIES = settings.TTS_COUNTRIES

DEFAULT_COUNTRY = 'AL'
assert DEFAULT_COUNTRY in TTS_COUNTRIES


def commodity_list(request):

    # commodities = Commodity.objects.filter(
    #     tts_json__isnull=False
    # ).order_by('tts_number_indents')[:200]

    commodities = Commodity.objects.exclude(
        tts_json={}
    ).order_by('tts_number_indents')[:200]

    context = {'commodities': commodities}
    return render(request, 'commodity_list.html', context)


def _append_url_arg(url, arg_name, arg_value):
    if '?' in url:
        suffix = ('&%s=%s' % (arg_name, arg_value))
    else:
        suffix = ('?%s=%s' % (arg_name, arg_value))
    return url + suffix


def commodity_detail(request, commodity_code):

    selected_country = request.GET.get('originCountry', '').upper()

    if (not selected_country) or selected_country not in TTS_COUNTRIES:  # todo: make case insensitive
        redirect_url = _append_url_arg(request.path, 'originCountry', DEFAULT_COUNTRY)
        return redirect(redirect_url)

    commodity = get_object_or_404(
        Commodity, commodity_code=commodity_code,
        #tts_json__isnull=False,
    )

    # hasreq_objects = HasRequirementDocument.objects.filter(
    #     eu_trade_helpdesk_website_origin_country=selected_country,
    #     commodity=commodity,
    # ).select_related('document')
    # documentsOLD = [rel.document for rel in hasreq_objects]

    eu_documents = EuTradeHelpdeskDocument.objects.filter(
        commodity=commodity, origin_country=selected_country
    ).order_by('group_name')

    context = {
        'commodity': commodity, 'eu_documents': eu_documents,
        'selected_origin_country': selected_country,
        'country_options': TTS_COUNTRIES
    }
    return render(request, 'commodity_detail.html', context)


def get_measure_table_data(request, commodity_code):

    origin_country = request.GET['originCountry'].upper()

    if origin_country not in TTS_COUNTRIES:
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


def document_detail(request, document_pk):
    document = get_object_or_404(RequirementDocument, pk=document_pk)
    return HttpResponse(document.html)


def eu_document_detail(request, pk):
    document = get_object_or_404(EuTradeHelpdeskDocument, pk=pk)
    html_fragments = []
    last = None
    for url in document.query_urls:
        html = requests.get(url).content.decode()
        if 'Additional information for' in html:
            last = html
            continue
        html_fragments.append(html)
    html_fragments.append(last)

    c = {'html_fragments': html_fragments}
    return render(request, 'eu_document_detail.html', c)


def hierarchy(request):
    return render(request, 'hierarchy.html', {})


PROBLEM_TITLES = [
    "Natural honey",
    "Edible products of animal origin, not elsewhere specified or included",
    "Ambergris, castoreum, civet and musk; cantharides; bile, whether or not dried; glands and other animal products used in the preparation of pharmaceutical products, fresh, chilled, frozen or otherwise provisionally preserved",
    "Human hair, unworked, whether or not washed or scoured; waste of human hair",
    "Other animal fats and oils and their fractions, whether or not refined, but not chemically modified",
    "Glycerol, crude; glycerol waters and glycerol lyes",
]


#@cache_page(90)
def get_hierarchy_data(request):

    root_di = {'name': 'root', 'children': [], 'node_id': "root"}

    for section in Section.objects.all()[:2]:
        section_di = {
            'name': section.tts_obj.title, 'children': [],
            'node_id': 'section:%s' % section.pk
        }
        
        for chapter in section.chapter_set.all():
            chapter_di = {
                'name': chapter.tts_obj.title, 'children': [],
                'node_id': 'chapter:%s' % chapter.pk
            }

            for heading in chapter.heading_set.all():
                '''
                heading_di = {
                    'name': heading.tts_obj.title, 'children': [],
                    'node_id': 'heading:%s' % heading.pk
                }
                for commodity in heading.commodity_set.all():
                    commodity_di = {
                        'name': commodity.tts_obj.title,
                        'children': [], 'href': commodity.get_absolute_url(),
                        'node_id': 'commodity:%s' % commodity.commodity_code,
                    }
                    heading_di['children'].append(commodity_di)
                '''

                heading_di = get_heading_data(heading, 'H: ' + heading.tts_title)

                chapter_di['children'].append(heading_di)

            section_di['children'].append(chapter_di)

        root_di['children'].append(section_di)

    return JsonResponse({'treeData': root_di})


def heading_detail(request, heading_code):
    if len(heading_code) == 4:
        heading = get_object_or_404(Heading, heading_code_4=heading_code)
    else:  # len == 10
        heading = get_object_or_404(Heading, heading_code=heading_code)

    context = {'heading': heading}
    return render(request, 'heading_detail.html', context)


def heading_data(request, heading_code):

    if len(heading_code) == 4:
        heading = get_object_or_404(Heading, heading_code_4=heading_code)
    else:  # len == 10
        heading = get_object_or_404(Heading, heading_code=heading_code)

    di = get_heading_data(heading, '.')
    return JsonResponse({'treeData': di})


def get_heading_data(heading, root_name):

    root_di = {
        'name': root_name, 'node_id': "root", 'children': []
    }

    heading_leafs = heading.children_concrete.all()
    for commodity in heading_leafs:
        root_di['children'].append({
            'name': commodity.tts_title, 'node_id': commodity.pk,
            'children': [], 'href': commodity.get_absolute_url(),
            'commodity_code': commodity.commodity_code
        })
    for abstract_commodity in heading.children_abstract.all():
        root_di['children'].append(
            _get_abstract_commodity_tree(abstract_commodity)
        )
    return root_di


def _get_abstract_commodity_tree(abstract_commodity):
    abs_commodity_di = {
        'name': abstract_commodity.tts_heading_obj.title,
        'children': [], 'node_id': abstract_commodity.pk,
        'commodity_code': abstract_commodity.commodity_code
    }
    children = []
    for commodity in abstract_commodity.children_concrete.all():
        children.append({
            'name': commodity.tts_title, 'node_id': commodity.pk,
            'children': [], 'href': commodity.get_absolute_url(),
            'commodity_code': commodity.commodity_code
        })
    for child_abs_commodity in abstract_commodity.children_abstract.all():
        children.append(
            _get_abstract_commodity_tree(child_abs_commodity)
        )

    # order nodes by commodity codes with nodes labelled 'Other' last
    def child_rank(di):
        return di['name'] == 'Other', di['commodity_code']
    children.sort(key=child_rank)

    abs_commodity_di['children'] = children
    return abs_commodity_di


'''
var data = {
  name: 'My Tree',
  children: [
    { name: 'hello' },
    { name: 'wat' },
    {
      name: 'child folder',
      children: [
        {
          name: 'child folder',
          children: [
            { name: 'hello' },
            { name: 'wat' }
          ]
        },
        { name: 'hello' },
        { name: 'wat' },
        {
          name: 'child folder',
          children: [
            { name: 'hello' },
            { name: 'wat' }
          ]
        }
      ]
    }
  ]
}
'''
