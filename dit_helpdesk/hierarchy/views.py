from django.shortcuts import render

import json

# from django.conf import settings
# from django.views.decorators.cache import cache_page
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest # HttpResponseRedirect
#from django.urls import reverse

#from .models import Section, Commodity, RequirementDocument, EuTradeHelpdeskDocument, Heading, CommodityHasDocTitle
from hierarchy.models import Section
from headings.views import get_heading_data


HIERARCHY_JSON_PATH = '/Users/rossrochford/code/DIT/dit-helpdesk/dit_helpdesk/hierarchy/hierarchy_cached.json'
HIERARCHY_CACHED = json.loads(open(HIERARCHY_JSON_PATH).read())


def get_hierarchy_data(request):

    root_di = {'name': 'root', 'children': [], 'node_id': "root"}

    for section in Section.objects.all():
        section_di = _get_section_hierarchy_data(section)
        root_di['children'].append(section_di)

    return JsonResponse({'treeData': root_di})


def get_hierarchy_data_cached(request):
    return JsonResponse(HIERARCHY_CACHED)


def hierarchy(request):
    return render(request, 'hierarchy/hierarchy.html', {})


def _get_section_hierarchy_data(section):

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
            heading_di, _, _ = get_heading_data(heading, 'H: ' + heading.tts_title)
            chapter_di['children'].append(heading_di)

        section_di['children'].append(chapter_di)

    return section_di
