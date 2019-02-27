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
        end = '</ul>'

    else:
        children = node.get_hierarchy_children()
        html = '\n   <ul>'
        end = '  </ul>\n</li>'

    for child in children:
        if type(child) is Commodity:
            li = ('\n      <li><strong><a href="%s">' % child.get_absolute_url()) + child.tts_title + '</a></strong></li>'
        else:
            li = ('\n      <li><a href="%s">' % child.get_hierarchy_url()) + child.tts_title + '</a>'
        html = html + li
        if child.hierarchy_key in expanded:
            html = html + _get_hierarchy_level_html(child, expanded)

    html = html + end

    return html


@login_required
def hierarchy_view(request, node_id):

    node_id = node_id.rstrip('/')
    expanded = _get_expanded_context(node_id)
    html = _get_hierarchy_level_html('root', expanded)

    context = {'hierarchy_html': html}
    return render(request, 'hierarchy/hierarchy.html', context)

