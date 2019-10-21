import os
import json
import re
from datetime import datetime, timedelta, timezone
from django.contrib import messages
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404, redirect, reverse

from commodities.models import Commodity
from commodities.views import TABLE_COLUMN_TITLES
from countries.models import Country
from hierarchy.models import Section, Chapter, Heading, SubHeading

code_regex = re.compile("([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})")
HIERARCHY_JSON_PATH = os.path.join(os.path.dirname(__file__), "hierarchy_cached.json")
with open(HIERARCHY_JSON_PATH) as f:
    HIERARCHY_CACHED = json.loads(f.read())


def _get_expanded_context(selected_node_id):
    """
    Given a selected_node_id (a location in the hierarchy), return
    a list of hierarchy ids that make up the path to the currently expanded context.
    """
    if selected_node_id == "root":
        return []

    expanded = []
    node_type, node_pk = selected_node_id.split("-")

    if node_type == "section":
        expanded.append(selected_node_id)

    elif node_type == "chapter":
        chapter_obj = Chapter.objects.get(goods_nomenclature_sid=node_pk)
        expanded.append("section-{0}".format(chapter_obj.section.section_id))
        expanded.append("chapter-{0}".format(node_pk))

    elif node_type == "heading":
        heading_obj = Heading.objects.get(goods_nomenclature_sid=node_pk)

        expanded.append("section-{0}".format(heading_obj.chapter.section.section_id))
        expanded.append(
            "chapter-{0}".format(heading_obj.chapter.goods_nomenclature_sid)
        )
        expanded.append("heading-{0}".format(heading_obj.goods_nomenclature_sid))

    elif node_type == "sub_heading":

        current = SubHeading.objects.get(goods_nomenclature_sid=node_pk)
        while True:
            expanded.append("sub_heading-{0}".format(current.goods_nomenclature_sid))
            current = current.get_parent()
            if type(current) is Heading:
                break
        heading_obj = current

        expanded.append("section-{0}".format(heading_obj.chapter.section.section_id))
        expanded.append(
            "chapter-{0}".format(heading_obj.chapter.goods_nomenclature_sid)
        )
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
    if node == "root":  # if root it list only sections
        children = Section.objects.all().order_by("section_id").prefetch_related('chapter_set')
        html = '<ul class="app-hierarchy-tree">'
        end = "\n</ul>"
    else:
        children = node.get_hierarchy_children()
        html = '\n<ul class="app-hierarchy-tree--child">'
        end = "\n</ul>\n</li>"

    for child in children:
        if child.hierarchy_key in expanded:
            openclass = "open"
        else:
            openclass = "closed"

        commodity_code_html = ""
        if type(child) is not Section:
            commodity_code_html = (
                '<span class="app-commodity-code app-hierarchy-tree__commodity-code">'
            )

            if type(child) is Commodity:
                child.harmonized_code = child.commodity_code

            matches = code_regex.search(child.harmonized_code)
            code_split = [
                matches.group(1),
                matches.group(2),
                matches.group(3),
                matches.group(4),
                matches.group(5),
            ]
            for index, code_segment in enumerate(code_split):
                counter = str(int(index) + 1)

                if child.harmonized_code[2:] == "00000000" and int(counter) > 1:
                    blank_span = [
                        '<span class="app-commodity-code__is-blank">',
                        "</span>",
                    ]
                elif child.harmonized_code[4:] == "000000" and int(counter) > 2:
                    blank_span = [
                        '<span class="app-commodity-code__is-blank">',
                        "</span>",
                    ]
                else:
                    blank_span = ["", ""]

                commodity_code_html += '<span class="app-commodity-code__highlight app-commodity-code__highlight--{0}">{1}{2}{3}</span>'.format(
                    counter, blank_span[0], code_segment, blank_span[1]
                )

            commodity_code_html = commodity_code_html + "</span>"

        if type(child) is Section:
            li = f'<li id="{child.hierarchy_key}" class="app-hierarchy-tree__part app-hierarchy-tree__section app-hierarchy-tree__parent--{openclass}"><a href="{child.get_hierarchy_url(origin_country)}#{child.hierarchy_key}" class="app-hierarchy-tree__link app-hierarchy-tree__link--parent">{child.title.capitalize()}</a> <span class="app-hierarchy-tree__section-numbers">Section {child.roman_numeral}</span> <span class="app-hierarchy-tree__chapter-range">{child.chapter_range_str}</span>'
        elif (
            type(child) in [Commodity, Heading, SubHeading]
            and (type(child) is Commodity or child.get_hierarchy_children_count() == 0)
        ):
            li = f'<li id="{child.hierarchy_key}" class="app-hierarchy-tree__part app-hierarchy-tree__commodity"><div class="app-hierarchy-tree__link"><a href="{child.get_absolute_url(origin_country)}" class="app-hierarchy-tree__link--child">{child.description}<span class="govuk-visually-hidden"> &ndash; </span></a></div>{commodity_code_html}</li>'
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

    if node == "root":  # if root it list only sections
        children = Section.objects.all().order_by("section_id").prefetch_related('chapter_set')
    else:
        children = node.get_hierarchy_children()

    for child in children:
        element = {"key": child.hierarchy_key}
        if type(child) is Section:
            element.update(
                {
                    "type": "branch",
                    "roman_numeral": child.roman_numeral,
                    "chapter_range_str": child.chapter_range_str,
                    "label": child.title,
                }
            )
        else:
            if type(child) is Commodity or child.get_hierarchy_children_count() == 0:
                element["type"] = "leaf"
            else:
                element["type"] = "parent"
            code = (
                child.commodity_code
                if isinstance(child, Commodity)
                else child.harmonized_code
            )
            element["commodity_code"] = code_regex.search(code).groups()
            element["label"] = child.description

        if child.hierarchy_key in expanded:
            element["children"] = _get_hierarchy_level_json(
                node=child, expanded=expanded, origin_country=origin_country
            )

        serialized.append(element)
    return serialized


def hierarchy_data(country_code, node_id="root", content_type="html"):
    """
    View helper function
    :param country_code: string representing country code
    :param node_id: string representing hierarchy node id
    :return: html snippet that represents the expanded section of the hierarchy
    """
    node_id = node_id.rstrip("/")
    expanded = _get_expanded_context(node_id)
    serializers = {"html": _get_hierarchy_level_html, "json": _get_hierarchy_level_json}
    serializer = serializers[content_type]
    return serializer(node="root", expanded=expanded, origin_country=country_code)


def section_detail(request, section_id, country_code):
    """
    View for the heading detail page template which takes two arguments; the 10 digit code for the heading to
    display and the two character country code to provide the exporter geographical context which is
    used to display the appropriate related supporting content

    :param heading_code:
    :param request: django http request object
    :param country_code: string
    :return:
    """

    country = Country.objects.filter(country_code=country_code.upper()).first()

    if not country:
        messages.error(request, "Invalid originCountry")
        return redirect(reverse("choose-country"))

    section = get_object_or_404(Heading, heading_code=section_id)

    if (
        section.last_updated < datetime.now(timezone.utc) - timedelta(days=1)
        or section.tts_json is None
    ):
        section.update_content()

    import_measures = section.tts_obj.get_import_measures(country.country_code)
    table_data = [measure_json.get_table_row() for measure_json in import_measures]

    section_path = section.get_path()
    accordion_title = heading_hierarchy_section_header(section_path)
    rules_of_origin = section.get_rules_of_origin(country_code=country.country_code)

    modals_dict = {}
    for measure_json in import_measures:
        modals_dict.update(measure_json.measures_modals)

    context = {
        "selected_origin_country": country.country_code,
        "section": section,
        "selected_origin_country_name": country.name,
        "rules_of_origin": rules_of_origin,
        "roo_footnotes": rules_of_origin,
        "table_data": table_data,
        "column_titles": TABLE_COLUMN_TITLES,
        "regulations": section.get_regulations(),
        "accordion_title": accordion_title,
        "section_hierarchy_context": section_hierarchy_context(
            section_path, country.country_code, section_id
        ),
        "modals": modals_dict,
    }

    return render(request, "hierarchy/section_detail.html", context)


def chapter_detail(request, chapter_code, country_code):
    """
    View for the heading detail page template which takes two arguments; the 10 digit code for the heading to
    display and the two character country code to provide the exporter geographical context which is
    used to display the appropriate related supporting content

    :param heading_code:
    :param request: django http request object
    :param country_code: string
    :return:
    """
    country = Country.objects.filter(country_code=country_code.upper()).first()

    if not country:
        messages.error(request, "Invalid originCountry")
        return redirect(reverse("choose-country"))

    chapter = get_object_or_404(Chapter, chapter_code=chapter_code)

    chapter_path = chapter.get_path()
    chapter_path.insert(0, [chapter])

    accordion_title = chapter_hierarchy_section_header(chapter_path)

    context = {
        "selected_origin_country": country.country_code,
        "chapter": chapter,
        "selected_origin_country_name": country.name,
        "accordion_title": accordion_title,
        "chapter_hierarchy_context": detail_hierarchy_context(
            chapter_path, country.country_code, chapter_code
        ),
    }

    return render(request, "hierarchy/chapter_detail.html", context)


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

    country = Country.objects.filter(country_code=country_code.upper()).first()

    if not country:
        messages.error(request, "Invalid originCountry")
        return redirect(reverse("choose-country"))

    # heading = Heading.objects.filter(heading_code=heading_code).first()

    heading = get_object_or_404(Heading, heading_code=heading_code)

    import_measures = []
    table_data = []
    modals_dict = {}

    try:

        if (
            heading.last_updated < datetime.now(timezone.utc) - timedelta(days=1)
            or heading.tts_json is None
        ):
            heading.update_content()

        import_measures = heading.tts_obj.get_import_measures(country.country_code)
        table_data = [measure_json.get_table_row() for measure_json in import_measures]
        for measure_json in import_measures:
            modals_dict.update(measure_json.measures_modals)
    except Exception as ex:
        print(ex.args)

    heading_path = heading.get_path()
    heading_path.insert(0, [heading])
    accordion_title = heading_hierarchy_section_header(heading_path)
    rules_of_origin = heading.get_rules_of_origin(country_code=country.country_code)

    context = {
        "selected_origin_country": country.country_code,
        "heading": heading,
        "selected_origin_country_name": country.name,
        "accordion_title": accordion_title,
        "heading_hierarchy_context": detail_hierarchy_context(
            heading_path, country.country_code, heading_code
        ),
    }

    if import_measures and table_data:
        context.update(
            {
                "table_data": table_data,
                "column_titles": TABLE_COLUMN_TITLES,
                "modals": modals_dict,
                "rules_of_origin": rules_of_origin,
                "roo_footnotes": rules_of_origin,
                "regulations": heading.get_regulations(),
            }
        )

    return render(request, "hierarchy/heading_detail.html", context)


def subheading_detail(request, commodity_code, country_code):
    """
    View for the heading detail page template which takes two arguments; the 10 digit code for the heading to
    display and the two character country code to provide the exporter geographical context which is
    used to display the appropriate related supporting content

    :param heading_code:
    :param request: django http request object
    :param country_code: string
    :return:
    """

    country = Country.objects.filter(country_code=country_code.upper()).first()

    if not country:
        messages.error(request, "Invalid originCountry")
        return redirect(reverse("choose-country"))

    # heading = Heading.objects.filter(heading_code=heading_code).first()

    subheading = get_object_or_404(SubHeading, commodity_code=commodity_code)

    import_measures = []
    table_data = []
    modals_dict = {}
    try:
        if (
            subheading.last_updated < datetime.now(timezone.utc) - timedelta(days=1)
            or subheading.tts_json is None
        ):
            subheading.update_content()

        import_measures = subheading.tts_obj.get_import_measures(country.country_code)
        table_data = [measure_json.get_table_row() for measure_json in import_measures]
        for measure_json in import_measures:
            modals_dict.update(measure_json.measures_modals)
    except Exception as ex:
        print(ex.args)

    subheading_path = subheading.get_path()
    subheading_path.insert(0, [subheading])
    accordion_title = heading_hierarchy_section_header(subheading_path)
    rules_of_origin = subheading.get_rules_of_origin(country_code=country.country_code)

    context = {
        "selected_origin_country": country.country_code,
        "subheading": subheading,
        "selected_origin_country_name": country.name,
        "accordion_title": accordion_title,
        "subheading_hierarchy_context": detail_hierarchy_context(
            subheading_path, country.country_code, commodity_code
        ),
    }

    if import_measures and table_data:
        context.update(
            {
                "table_data": table_data,
                "column_titles": TABLE_COLUMN_TITLES,
                "modals": modals_dict,
                "rules_of_origin": rules_of_origin,
                "roo_footnotes": rules_of_origin,
                "regulations": subheading.get_regulations(),
            }
        )

    return render(request, "hierarchy/subheading_detail.html", context)


def chapter_hierarchy_section_header(reversed_heading_tree):
    """
    View helper function to extract the Section Numeral and title for the hierarchy context of the heading
    and returned as formatted html string
    :param reversed_heading_tree:
    :return: html
    """
    section_index = len(reversed_heading_tree) - 1
    section = reversed_heading_tree[section_index][0]
    html = f"Section {section.roman_numeral}: {section.title.capitalize()}"
    return html


def heading_hierarchy_section_header(reversed_heading_tree):
    """
    View helper function to extract the Section Numeral and title for the hierarchy context of the heading
    and returned as formatted html string
    :param reversed_heading_tree:
    :return: html
    """
    section_index = len(reversed_heading_tree) - 1
    section = reversed_heading_tree[section_index][0]
    html = f"Section {section.roman_numeral}: {section.title.capitalize()}"
    return html


def _commodity_code_html(code):
    """
    View helper function that genrates an html representation of the ten digit commodity code broken into three groups
    of 6, 2 and  digits and colour code formatted
    :param item: model instance
    :return: html
    """
    commodity_code_html = (
        '<span class="app-commodity-code app-hierarchy-tree__commodity-code">'
    )

    if len(code) > 2 and code.isdigit():

        code_regex = re.search(
            "([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})", code
        )
        code_split = [
            code_regex.group(1),
            code_regex.group(2),
            code_regex.group(3),
            code_regex.group(4),
            code_regex.group(5),
        ]

        for index, code_segment in enumerate(code_split):
            counter = str(int(index) + 1)
            if code[2:] == "00000000" and int(counter) > 1:
                blank_span = ['<span class="app-commodity-code__is-blank">', "</span>"]
            elif code[4:] == "000000" and int(counter) > 2:
                blank_span = ['<span class="app-commodity-code__is-blank">', "</span>"]
            else:
                blank_span = ["", ""]

            commodity_code_html += '<span class="app-commodity-code__highlight app-commodity-code__highlight--{0}">{1}{2}{3}</span>'.format(
                counter, blank_span[0], code_segment, blank_span[1]
            )
    else:
        commodity_code_html + code

    commodity_code_html = commodity_code_html + "</span>"

    return commodity_code_html


def _generate_commodity_code_html(item):
    """
    View helper function that genrates an html representation of the ten digit commodity code broken into three groups
    of 6, 2 and  digits and colour code formatted
    :param item: model instance
    :return: html
    """
    commodity_code_html = ""
    if type(item) is not Section:
        commodity_code_html = (
            '<span class="app-commodity-code app-hierarchy-tree__commodity-code">'
        )

        if type(item) is Commodity:
            item.harmonized_code = item.commodity_code

        code_result = code_regex.search(item.harmonized_code)
        code_split = [
            code_result.group(1),
            code_result.group(2),
            code_result.group(3),
            code_result.group(4),
            code_result.group(5),
        ]

        for index, code_segment in enumerate(code_split):
            counter = str(int(index) + 1)
            commodity_code_html = (
                commodity_code_html
                + '<span class="app-commodity-code__highlight app-commodity-code__highlight--'
                + counter
                + '">'
                + code_segment
                + "</span>"
            )

        commodity_code_html = commodity_code_html + "</span>"

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

    country = Country.objects.filter(country_code=country_code.upper()).first()

    if not country:
        messages.error(request, "Invalid originCountry")
        return redirect(reverse("choose-country"))

    heading = Heading.objects.get(heading_code=heading_code)
    import_measure = heading.tts_obj.get_import_measure_by_id(
        int(measure_id), country_code=country_code
    )
    conditions = import_measure.get_measure_conditions_by_measure_id(int(measure_id))

    context = {
        "selected_origin_country": country.country_code,
        "heading": heading,
        "commodity_code_split": heading.heading_code_split,
        "selected_origin_country_name": country.name,
        "import_measure": import_measure,
        "conditions": conditions,
    }

    return render(request, "hierarchy/measure_condition_detail.html", context)


def measure_quota_detail(request, heading_code, country_code, measure_id, order_number):
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

    country = Country.objects.filter(country_code=country_code.upper()).first()

    if not country:
        messages.error(request, "Invalid originCountry")
        return redirect(reverse("choose-country"))

    heading = Heading.objects.get(heading_code=heading_code)
    import_measure = heading.tts_obj.get_import_measure_by_id(
        int(measure_id), country_code=country_code
    )
    conditions = import_measure.get_measure_conditions_by_measure_id(int(measure_id))
    quota_def = import_measure.get_measure_quota_definition_by_order_number(
        order_number
    )
    geographical_area = import_measure.get_geographical_area()

    context = {
        "selected_origin_country": country.country_code,
        "commodity_description": heading.description,
        "commodity_code": heading.commodity_code,
        "selected_origin_country_name": country.name,
        "quota_def": quota_def,
        "geographical_area": geographical_area,
        "commodity_code_split": heading.heading_code_split,
        "measure_type": import_measure.type_description,
    }

    return render(request, "hierarchy/measure_quota_detail.html", context)


def detail_hierarchy_context(hierarchy_path, country_code, commodity_code):
    """
    View helper function that returns an html representation of the context of the heading within the
    hierarchy takes three arguments: the path to the heading, the country code of the exporting country and the
    heading code
    :param commodity_code:
    :param hierarchy_path:
    :param country_code: string
    :return: html
    """
    listSize = len(hierarchy_path)
    html = ""
    reversedList = reversed(hierarchy_path)

    for index, lista in enumerate(reversedList):
        if index is 0:
            # We dont want to retrieve section as it is explicity renders by commodity_hierarchy_section_header
            html += "<nav>"
        else:
            html += f"<ul>"

            for i, item in enumerate(lista):
                expand = "open"
                if index is listSize:
                    expand = "closed"

                if type(item) is Heading:
                    if item.heading_code == commodity_code:
                        html += f"""
                            <li>
                                <span class="govuk-!-font-weight-bold app-hierarchy-tree__link">{item.description.capitalize()}</span><span class="govuk-visually-hidden"> &ndash; </span>{_commodity_code_html(item.commodity_code)}
                            </li>
                            """
                    else:
                        html += f"""
                           <li>
                                <a href="{item.get_absolute_url(country_code)}" class="app-hierarchy-tree__link app-hierarchy-tree__link--child">
                                <span>{item.description.capitalize()}</span><span class="govuk-visually-hidden"> &ndash; </span></a>{_commodity_code_html(item.commodity_code)}
                            </li>
                            """
                elif type(item) in [Chapter, Heading, SubHeading]:
                    item_commodity_code = ""
                    if type(item) is Chapter:
                        item_commodity_code = item.chapter_code
                    elif type(item) is Heading:
                        item_commodity_code = item.heading_code
                    else:
                        item_commodity_code = item.commodity_code
                    html += f"""
                       <li>
                            <span class="govuk-!-font-weight-bold app-hierarchy-tree__link">{item.description.capitalize()}</span>{_commodity_code_html(item_commodity_code)}"""

                    if index is listSize:
                        html += "</li>"

            if index is listSize:
                for i in range(0, listSize):
                    # close
                    html += "</ul>"
    return html
