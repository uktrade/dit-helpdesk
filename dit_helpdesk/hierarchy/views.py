import json
import re

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from commodities.models import Commodity
from hierarchy.models import Section, Chapter, Heading, SubHeading

def _get_expanded_context(selected_node_id):
    """
    Given a selected_node_id (a location in the hierarchy), return
    a list of currently expanded nodes.
    """
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
        # print(dir(child))
        if child.hierarchy_key in expanded:
            openclass = 'open'
        else:
            openclass = 'closed'

        code_html = '';
        if (type(child) is not Section):
            if type(child) is Commodity:
                child.harmonized_code = child.tts_obj.code
            code_regex = re.search('([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})', child.harmonized_code)
            code_split = [
                code_regex.group(1),
                code_regex.group(2),
                code_regex.group(3),
                code_regex.group(4)
            ]
            for index, code_segment in enumerate(code_split):
                counter = str(int(index) + 1)
                code_html = code_html + '<span class="app-commodity-code__highlight app-commodity-code__highlight--' + counter + '">' + code_segment + '</span>'

        if type(child) is Section:
            li = '\n<li id="' + child.hierarchy_key + '" class="app-hierarchy-tree__section app-hierarchy-tree__parent--' + openclass +'">\n<a href="' + child.get_hierarchy_url() + '#' + child.hierarchy_key + '" class="app-hierarchy-tree__link app-hierarchy-tree__link--parent">\n' + child.tts_title + '\n</a> - Section ' + child.roman_numeral + ' ; ' + child.chapter_range_str
        elif type(child) is Chapter:
            li = '\n<li id="' + child.hierarchy_key + '" class="app-hierarchy-tree__chapter app-hierarchy-tree__parent--' + openclass +'">\n<a href="' + child.get_hierarchy_url() + '#' + child.hierarchy_key + '" class="app-hierarchy-tree__link app-hierarchy-tree__link--parent">\n' + child.tts_title + '\n</a>\n' + code_html
        elif type(child) is Heading:
            li = '\n<li id="' + child.hierarchy_key + '" class="app-hierarchy-tree__heading app-hierarchy-tree__parent--' + openclass +'">\n<a href="' + child.get_hierarchy_url() + '#' + child.hierarchy_key + '" class="app-hierarchy-tree__link app-hierarchy-tree__link--parent">\n' + child.tts_title + '\n</a>\n' + code_html
        elif type(child) is SubHeading:
            li = '\n<li id="' + child.hierarchy_key + '" class="app-hierarchy-tree__subheading app-hierarchy-tree__parent--' + openclass +'">\n<a href="' + child.get_hierarchy_url() + '#' + child.hierarchy_key + '" class="app-hierarchy-tree__link app-hierarchy-tree__link--parent">\n' + child.tts_title + '\n</a>\n' + code_html
        elif type(child) is Commodity:
            li = ('\n<li id="' + child.hierarchy_key + '" class="app-hierarchy-tree__commodity">\n<a href="%s" class="app-hierarchy-tree__link app-hierarchy-tree__link--child">' % child.get_absolute_url()) + child.tts_title + '\n<span class="govuk-visually-hidden"> &ndash; </span>\n<b>Select</b>\n</a>\n' + code_html + '</li>'
        else:
            li = '\n<li id="' + child.hierarchy_key + '" class="app-hierarchy-tree__other app-hierarchy-tree__parent--' + openclass +'">\n<a href="' + child.get_hierarchy_url() + '#' + child.hierarchy_key + '" class="app-hierarchy-tree__link app-hierarchy-tree__link--parent">\n' + child.tts_title + '\n</a>\n' + code_html

        html = html + li

        if child.hierarchy_key in expanded:
            html = html +  _get_hierarchy_level_html(child, expanded)

    html = html + end

    return html


@login_required
def hierarchy_view(request, node_id):

    node_id = node_id.rstrip('/')
    expanded = _get_expanded_context(node_id)
    html = _get_hierarchy_level_html('root', expanded)

    context = {'hierarchy_html': html}
    return render(request, 'hierarchy/hierarchy.html', context)
