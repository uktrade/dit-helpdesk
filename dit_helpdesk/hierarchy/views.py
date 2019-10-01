import os
import json
import re
from datetime import datetime, timedelta, timezone
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect, reverse

from commodities.models import Commodity
from commodities.views import TABLE_COLUMN_TITLES
from countries.models import Country
from hierarchy.models import Section, Chapter, Heading, SubHeading

code_regex = re.compile('([0-9]{6})([0-9]{2})([0-9]{2})')
HIERARCHY_JSON_PATH = os.path.join(os.path.dirname(__file__), 'hierarchy_cached.json')
with open(HIERARCHY_JSON_PATH) as f:
    HIERARCHY_CACHED = json.loads(f.read())


def _get_expanded_context(selected_node_id):
    """
    Given a selected_node_id (a location in the hierarchy), return
    a list of hierarchy ids that make up the path to the currently expanded context.
    """
    if selected_node_id == 'root':
        return []

    expanded = []
    node_type, node_pk = selected_node_id.split('-')

    if node_type == 'section':
        expanded.append(selected_node_id)

    elif node_type == 'chapter':
        chapter_obj = Chapter.objects.get(goods_nomenclature_sid=node_pk)
        expanded.append("section-{0}".format(chapter_obj.section.section_id))
        expanded.append("chapter-{0}".format(node_pk))

    elif node_type == 'heading':
        heading_obj = Heading.objects.get(goods_nomenclature_sid=node_pk)

        expanded.append("section-{0}".format(heading_obj.chapter.section.section_id))
        expanded.append("chapter-{0}".format(heading_obj.chapter.goods_nomenclature_sid))
        expanded.append("heading-{0}".format(heading_obj.goods_nomenclature_sid))

    elif node_type == 'sub_heading':

        current = SubHeading.objects.get(goods_nomenclature_sid=node_pk)
        while True:
            expanded.append("sub_heading-{0}".format(current.goods_nomenclature_sid))
            current = current.get_parent()
            if type(current) is Heading:
                break
        heading_obj = current

        expanded.append("section-{0}".format(heading_obj.chapter.section.section_id))
        expanded.append("chapter-{0}".format(heading_obj.chapter.goods_nomenclature_sid))
        expanded.append("heading-{0}".format(heading_obj.goods_nomenclature_sid))

    return expanded


def _get_hierarchy_level_html(node, expanded, origin_country):
    """
    View helper function to return the html for the selected hierarchy node
    :param node: string or model instance the current node
    :param expanded: list of hierarchy ids that make up the currently expanded path
    :param origin_country: string representing the origin country code
    :return: html snippet that represents the expanded section of the hierarchy
    """
    if node == 'root': # if root it list only sections
        children = Section.objects.all().order_by('section_id')
        html = '<ul class="app-hierarchy-tree">'
        end = '\n</ul>'
    else:
        children = node.get_hierarchy_children()
        html = '\n<ul class="app-hierarchy-tree--child">'
        end = '\n</ul>\n</li>'

    for child in children:
        if child.hierarchy_key in expanded:
            openclass = 'open'
        else:
            openclass = 'closed'

        commodity_code_html = ''
        if type(child) is not Section:
            commodity_code_html = '<span class="app-commodity-code app-hierarchy-tree__commodity-code">'

            if type(child) is Commodity:
                child.harmonized_code = child.commodity_code

            matches = code_regex.search(child.harmonized_code)
            code_split = [
                matches.group(1),
                matches.group(2),
                matches.group(3)
            ]
            for index, code_segment in enumerate(code_split):
                counter = str(int(index) + 1)
                commodity_code_html = commodity_code_html + \
                    '<span class="app-commodity-code__highlight app-commodity-code__highlight--' + counter + '">' + code_segment + '</span>'

            commodity_code_html = commodity_code_html + '</span>'

        if type(child) is Section:
            li = f'<li id="{child.hierarchy_key}" class="app-hierarchy-tree__part app-hierarchy-tree__section app-hierarchy-tree__parent--{openclass}"><a href="{child.get_hierarchy_url(origin_country)}#{child.hierarchy_key}" class="app-hierarchy-tree__link app-hierarchy-tree__link--parent">{child.title.capitalize()}</a> <span class="app-hierarchy-tree__section-numbers">Section {child.roman_numeral}</span> <span class="app-hierarchy-tree__chapter-range">{child.chapter_range_str}</span>'
        elif type(child) is Commodity or Heading and len(child.get_hierarchy_children()) is 0:
            li = f'<li id="{child.hierarchy_key}" class="app-hierarchy-tree__part app-hierarchy-tree__commodity"><a href="{child.get_absolute_url(origin_country)}" class="app-hierarchy-tree__link app-hierarchy-tree__link--child"><span>{child.description}</span><span class="govuk-visually-hidden"> &ndash; </span><b class="app-hierarchy-button">Select</b></a>{commodity_code_html}</li>'
        else:
            li = f'<li id="{child.hierarchy_key}" class="app-hierarchy-tree__part app-hierarchy-tree__chapter app-hierarchy-tree__parent--{openclass}"><a href="{child.get_hierarchy_url(origin_country)}#{child.hierarchy_key}" class="app-hierarchy-tree__link app-hierarchy-tree__link--parent">{child.description.capitalize()}</a>{commodity_code_html}'
        html = html + li

        if child.hierarchy_key in expanded:
            html = html + _get_hierarchy_level_html(child, expanded, origin_country)

    html = html + end

    return html


def _get_hierarchy_level_json(node, expanded, origin_country):
    """
    View helper function to return the JSON for the selected hierarchy node
    :param node: string or model instance the current node
    :param expanded: list of hierarchy ids that make up the currently expanded path
    :param origin_country: string representing the origin country code
    :return: dict that represents the expanded section of the hierarchy
    """

    serialized = []

    if node == 'root': # if root it list only sections
        children = Section.objects.all().order_by('section_id')
    else:
        children = node.get_hierarchy_children()

    for child in children:
        element = {'key': child.hierarchy_key}
        if type(child) is Section:
            element.update({
                'type': 'branch',
                'roman_numeral': child.roman_numeral,
                'chapter_range_str': child.chapter_range_str,
                'label': child.title,
            })
        else:
            if type(child) is Commodity or len(child.get_hierarchy_children()) is 0:
                element['type'] = 'leaf'
            else:
                element['type'] = 'parent'
            code = child.commodity_code if isinstance(child, Commodity) else child.harmonized_code
            element['commodity_code'] = code_regex.search(code).groups()
            element['label'] = child.description

        if child.hierarchy_key in expanded:
            element['children'] = _get_hierarchy_level_json(node=child, expanded=expanded, origin_country=origin_country)

        serialized.append(element)
    return serialized


def hierarchy_data(country_code, node_id='root', content_type='html'):
    """
    View helper function
    :param country_code: string representing country code
    :param node_id: string representing hierarchy node id
    :return: html snippet that represents the expanded section of the hierarchy
    """
    node_id = node_id.rstrip('/')
    expanded = _get_expanded_context(node_id)
    serializers = {
        'html': _get_hierarchy_level_html,
        'json': _get_hierarchy_level_json,
    }
    serializer = serializers[content_type]
    return serializer(node='root', expanded=expanded, origin_country=country_code)


def heading_detail(request, heading_code, country_code):
    """
    View for the heading detail page template which takes two arguments; the 10 digit code for the heading to
    display and the two character country code to provide the exporter geographical context which is
    used to display the appropriate related supporting content

    :param heading_code:
    :param request: django http request object
    :param country_code: string
    :return:
    """

    country = Country.objects.filter(
        country_code=country_code.upper()
    ).first()

    if not country:
        messages.error(request, 'Invalid originCountry')
        return redirect(reverse('choose-country'))

    heading = Heading.objects.filter(heading_code=heading_code).first()

    if heading.last_updated < datetime.now(timezone.utc) - timedelta(days=1) or heading.tts_json is None:
        heading.update_content()

    import_measures = heading.tts_obj.get_import_measures(country.country_code)
    table_data = [
        measure_json.get_table_row() for measure_json in import_measures
    ]

    heading_path = heading.get_path()
    accordion_title = heading_hierarchy_section_header(heading_path)
    rules_of_origin = heading.get_rules_of_origin(country_code=country.country_code)

    context = {
        'selected_origin_country': country.country_code,
        'heading': heading,
        'selected_origin_country_name': country.name,
        'rules_of_origin': rules_of_origin,
        'roo_footnotes': rules_of_origin,
        'table_data': table_data,
        'column_titles': TABLE_COLUMN_TITLES,
        'regulations': heading.get_regulations(),
        'accordion_title': accordion_title,
        'heading_hierarchy_context': heading_hierarchy_context(heading_path, country.country_code, heading_code)
    }

    return render(request, 'hierarchy/heading_detail.html', context)


def heading_hierarchy_section_header(reversed_heading_tree):
    """
    View helper function to extract the Section Numeral and title for the hierarchy context of the heading
    and returned as formatted html string
    :param reversed_heading_tree:
    :return: html
    """
    section_index = len(reversed_heading_tree) - 1
    section = reversed_heading_tree[section_index][0]
    html = f'Section {section.roman_numeral}: {section.title.capitalize()}'
    return html


def heading_hierarchy_context(heading_path, country_code, heading_code):
    """
    View helper function that returns an html representation of the context of the heading within the
    hierarchy takes three arguments: the path to the heading, the country code of the exporting country and the
    heading code
    :param heading_code:
    :param heading_path:
    :param country_code: string
    :return: html
    """
    listSize = len(heading_path)
    html = ''
    reversedList = reversed(heading_path)

    for index, lista in enumerate(reversedList):
        if index is 0:
            # We dont want to retrieve section as it is explicity renders by commodity_hierarchy_section_header
            html += ''
        else:
            html += f'<ul id="hierarchy-tree-list-{index}" class="app-hierarchy-tree--child">'
            for i, item in enumerate(lista):
                expand = 'open'
                if index is listSize:
                    expand = 'closed'
                if type(item) is Heading:
                    if item.heading_code == heading_code:
                        html += f"""
                            <li id="tree-list-{index}-item-{i}" class="app-hierarchy-tree__part app-hierarchy-tree__heading">
                                <span class="govuk-!-font-weight-bold app-hierarchy-tree__link">{item.description}</span><span class="govuk-visually-hidden"> &ndash; </span>{_generate_commodity_code_html(item)}
                            </li>
                            """
                    else:
                        html += f"""
                           <li id="tree-list-{index}-item-{i}" class="app-hierarchy-tree__part app-hierarchy-tree__heading">
                                <a href="{item.get_absolute_url(country_code)}" class="app-hierarchy-tree__link app-hierarchy-tree__link--child">
                                <span>{item.description}</span><span class="govuk-visually-hidden"> &ndash; </span></a>{_generate_commodity_code_html(item)}
                            </li>
                            """
                elif hasattr(item,'description'):
                    html += f"""
                       <li id="tree-list-{index}-item-{i}" class="app-hierarchy-tree__part app-hierarchy-tree__chapter app-hierarchy-tree__parent--{expand}">
                            <a href="{item.get_hierarchy_url(country_code)}#{item.hierarchy_key}" class="app-hierarchy-tree__link app-hierarchy-tree__link--parent">{item.description.capitalize()}</a>{_generate_commodity_code_html(item)}"""
                    if index is listSize:
                        html += '</li>'

            if index is listSize:
                for i in range(0, listSize):
                    # close
                    html += '</ul>'
    return html


def _generate_commodity_code_html(item):
    """
    View helper function that genrates an html representation of the ten digit commodity code broken into three groups
    of 6, 2 and  digits and colour code formatted
    :param item: model instance
    :return: html
    """
    commodity_code_html = ''
    if type(item) is not Section:
        commodity_code_html = '<span class="app-commodity-code app-hierarchy-tree__commodity-code">'

        if type(item) is Commodity:
            item.harmonized_code = item.commodity_code

        code_regex = code_regex.search(item.harmonized_code)
        code_split = [
            code_regex.group(1),
            code_regex.group(2),
            code_regex.group(3)
        ]

        for index, code_segment in enumerate(code_split):
            counter = str(int(index) + 1)
            commodity_code_html = commodity_code_html + \
                '<span class="app-commodity-code__highlight app-commodity-code__highlight--' + counter + '">' + code_segment + '</span>'

        commodity_code_html = commodity_code_html + '</span>'

    return commodity_code_html


def measure_condition_detail(request, heading_code, country_code, measure_id):
    """
    View for an individual measure condition detail page template which takes three arguments, the commodity code that
    the measure belongs to, the measure id of the individual measure being presented and the country code to
    provide the exporter geographical context
    :param heading_code:
    :param request: django http request object
    :param country_code: string
    :param measure_id: int
    :return:
    """

    country = Country.objects.filter(
        country_code=country_code.upper()
    ).first()

    if not country:
        messages.error(request, 'Invalid originCountry')
        return redirect(reverse('choose-country'))

    heading = Heading.objects.get(heading_code=heading_code)
    import_measure = heading.tts_obj.get_import_measure_by_id(int(measure_id), country_code=country_code)
    conditions = import_measure.get_measure_conditions_by_measure_id(int(measure_id))

    context = {
        'selected_origin_country': country.country_code,
        'heading': heading,
        'selected_origin_country_name': country.name,
        'import_measure': import_measure,
        'conditions': conditions
    }

    return render(request, 'hierarchy/measure_condition_detail.html', context)
