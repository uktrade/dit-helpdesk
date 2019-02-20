import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest

from commodities.models import Commodity
from hierarchy.models import Section, Chapter, Heading, SubHeading

def _get_expanded_context(selected_node_id):
    if selected_node_id == 'root':
        return []

    expanded = []
    node_type, node_pk = selected_node_id.split('-')

    if node_type == 'section':
        expanded.append(selected_node_id)

    elif node_type == 'chapter':
        chapter_obj = Chapter.objects.get(pk=node_pk)
        expanded.append('section-%s' % chapter_obj.section.pk)
        expanded.append('chapter-%s' % node_pk)

    elif node_type == 'heading':
        heading_obj = Heading.objects.get(pk=node_pk)

        expanded.append('section-%s' % heading_obj.chapter.section.pk)
        expanded.append('chapter-%s' % heading_obj.chapter.pk)
        expanded.append('heading-%s' % heading_obj.pk)

    elif node_type == 'sub_heading':

        current = SubHeading.objects.get(pk=node_pk)
        while True:
            expanded.append('sub_heading-%s' % current.pk)
            current = current.get_parent()
            if type(current) is Heading:
                break
        heading_obj = current

        expanded.append('section-%s' % heading_obj.chapter.section.pk)
        expanded.append('chapter-%s' % heading_obj.chapter.pk)
        expanded.append('heading-%s' % heading_obj.pk)

    return expanded


def _get_hierarchy_level_html(node, expanded):
    if node == 'root':
        children = Section.objects.all()
        html = '<ul class="app-hierarchy-tree">'
        end = '\n</ul>'

    else:
        children = node.get_hierarchy_children()
        html = '\n<ul class="app-hierarchy-tree--child">'
        end = '\n</ul>\n</li>'

    for child in children:
        if type(child) is Commodity:
            li = ('\n<li id="' + child.hierarchy_key + '" class="app-hierarchy-tree__child">\n<a href="%s" class="app-hierarchy-tree__link app-hierarchy-tree__link--child">' % child.get_absolute_url()) + child.tts_title + '\n<span class="govuk-visually-hidden"> &ndash; </span>\n<b>Select</b>\n</a>\n</li>'
        else:
            openclass = 'closed'
            if child.hierarchy_key in expanded:
                openclass = 'open'
            li = '\n<li id="' + child.hierarchy_key + '" class="app-hierarchy-tree__parent app-hierarchy-tree__parent--' + openclass +'">\n<a href="' + child.get_hierarchy_url() + '#' + child.hierarchy_key + '" class="app-hierarchy-tree__link app-hierarchy-tree__link--parent">\n' + child.tts_title + '\n</a>'

        html = html + li

        if child.hierarchy_key in expanded:
            html = html +  _get_hierarchy_level_html(child, expanded)

    html = html + end

    return html

@login_required
def hierarchy_view(request, node_id):

    expanded = _get_expanded_context(node_id)
    html = _get_hierarchy_level_html('root', expanded)

    context = {'hierarchy_html': html}
    return render(request, 'hierarchy/hierarchy.html', context)

# -----------------------------------------------
# old vue.js stuff:


def get_hierarchy_data(request):

    root_di = {'name': 'root', 'children': [], 'node_id': "root"}

    for section in Section.objects.all():
        section_di = _get_section_hierarchy_data(section)
        root_di['children'].append(section_di)

    return JsonResponse({'treeData': root_di})


def get_hierarchy_data_cached(request):
    HIERARCHY_JSON_PATH = 'hierarchy/hierarchy_cached.json'
    HIERARCHY_CACHED = json.loads(open(HIERARCHY_JSON_PATH).read())
    return JsonResponse(HIERARCHY_CACHED)


def hierarchy(request):
    return render(request, 'hierarchy/hierarchy_old.html', {})


def _get_section_hierarchy_data(section):
    from headings.views import get_heading_data
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
