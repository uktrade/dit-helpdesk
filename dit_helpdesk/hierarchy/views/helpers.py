import re

from django.shortcuts import reverse

from commodities.models import Commodity

from ..models import Chapter, Heading, SubHeading


def hierarchy_section_header(reversed_heading_tree):
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


def get_hierarchy_item_by_code(code):

    try:
        return Chapter.objects.get(chapter_code=code)
    except Chapter.DoesNotExist:
        pass

    try:
        return Heading.objects.get(heading_code=code)
    except Heading.DoesNotExist:
        pass

    try:
        subheading = SubHeading.objects.filter(commodity_code=code)
        if type(subheading) == SubHeading:
            return subheading
        elif len(subheading) > 0:
            return subheading.first()
        else:
            raise SubHeading.DoesNotExist
    except SubHeading.DoesNotExist:
        pass

    try:
        return Commodity.objects.get(commodity_code=code)
    except Commodity.DoesNotExist:
        pass


def _commodity_code_html(item, ignore_duplicate=True):
    """
    View helper function that genrates an html representation of the ten digit commodity code broken into three groups
    of 6, 2 and  digits and colour code formatted
    :param item: model instance
    :return: html
    """

    if ignore_duplicate:
        if isinstance(item, SubHeading) and item.is_duplicate_heading():
            return '<span class="app-commodity-code app-hierarchy-tree__commodity-code">&nbsp;</span>'

        if isinstance(item, Heading) and item.is_duplicate_heading():
            return '<span class="app-commodity-code app-hierarchy-tree__commodity-code">&nbsp;</span>'

    leaf = False

    if isinstance(item, str):
        code = item
    elif isinstance(item, Chapter):
        code = item.chapter_code
    elif isinstance(item, Heading):
        code = item.heading_code
    else:
        code = item.commodity_code

    if (
        type(item) == Commodity
        or hasattr(item, "get_hierarchy_children_count")
        and item.get_hierarchy_children_count() == 0
    ):
        leaf = True

    commodity_code_html = (
        '<span class="app-commodity-code app-hierarchy-tree__commodity-code" '
        'aria-label="Commodity code">'
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

        blank_span_html = ['<span class="app-commodity-code__is-blank">', "</span>"]

        for index, code_segment in enumerate(code_split):
            counter = str(int(index) + 1)
            if code[2:] == "00000000" and int(counter) > 1:
                blank_span = blank_span_html if not leaf else ["", ""]
            elif code[4:] == "000000" and int(counter) > 2:
                blank_span = blank_span_html if not leaf else ["", ""]
            elif code[6:] == "0000" and int(counter) > 3:
                blank_span = blank_span_html if not leaf else ["", ""]
            elif code[8:] == "00" and int(counter) > 4:
                blank_span = blank_span_html if not leaf else ["", ""]
            else:
                blank_span = ["", ""]

            commodity_code_html += '<span class="app-commodity-code__highlight app-commodity-code__highlight--{0}">{1}{2}{3}</span>'.format(
                counter, blank_span[0], code_segment, blank_span[1]
            )

    else:
        commodity_code_html + code

    commodity_code_html = commodity_code_html + "</span>"

    return commodity_code_html


def get_hierarchy_context(commodity_path, country_code, commodity_code, current_item):
    """
    View helper function that returns an html representation of the context of the commodity within the
    hierarchy takes three arguments: the path to the commodity, the country code of the exporting country and the
    commodity code
    :param commodity_path: string
    :param country_code: string
    :param commodity_code: string
    :return: html
    """

    listSize = len(commodity_path)
    html = ""
    reversedList = reversed(commodity_path)

    for index, lista in enumerate(reversedList):
        if index == 0:
            # We dont want to retrieve section as it is explicity renders by commodity_hierarchy_section_header
            html += "<nav>"
        else:
            html += f"<ul>"
            for i, item in enumerate(lista):
                if item.commodity_code == commodity_code and item == current_item:
                    html += f"""<li><div class="govuk-body govuk-!-font-weight-bold app-hierarchy-tree__link govuk-!-font-size-16">{item.description.capitalize()}</div><div class="govuk-visually-hidden"> &ndash; </div><strong>{_commodity_code_html(item)}</strong></li>"""
                else:
                    nomenclature_link = item.get_detail_url(country_code)

                    html += f"""<li><a href="{nomenclature_link}" class="app-hierarchy-tree__link app-hierarchy-tree__link--parent">{item.description.capitalize()}</a>{_commodity_code_html(item)}"""

                if index is listSize:
                    html += "</li>"

            if index is listSize:
                for i in range(0, listSize):
                    # close
                    html += "</ul></nav>"

    return html
