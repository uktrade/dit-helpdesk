import logging
import re

from functools import partial

from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

from hierarchy.models import Chapter, Heading, SubHeading
from commodities.models import Commodity


logger = logging.getLogger(__name__)


register = template.Library()


SUBTEXT_REGEX = re.compile(
    r"\b(chapter|chapters|heading|headings|subheading|subheadings).*(\.\D|;|\s*$)",
    re.IGNORECASE,
)


CODES_REGEX = re.compile(
    r"\bchapter (\d)[^.\d][\b,)]?(?!\s?%)|"
    r"\b(?<!\[)(\d\d)(?!.\d)[\b,)]?(?!\s?%| per cent| percent)|"
    r"\b(?<!\[)(\d\d\d\d)(?!.\d)[\b,)]?(?!\s?%| per cent| percent)|"
    r"\b(?<!\[)(\d\d\.\d\d)(?!.\d)[\b,)]?(?!\s?%| per cent| percent)|"
    r"\b(?<!\[)(\d\d\d\d\.\d\d)(?!.\d)[\b,)]?(?!\s?%| per cent| percent)",
    re.IGNORECASE,
)


HS_LEN_MAPPING = {2: [Chapter], 4: [SubHeading, Heading], 6: [Commodity, SubHeading]}


class HierarchyModelNotFound(Exception):
    pass


def _find_hierarchy_model(code):
    models = HS_LEN_MAPPING[len(code)]

    code_norm = code.ljust(10, "0")

    for model_class in models:
        try:
            return model_class.objects.get_by_commodity_code(code_norm)
        except model_class.DoesNotExist:
            logger.warning(
                "Couldn't find %s object for HS code %s", model_class, code_norm
            )
            continue
        except model_class.MultipleObjectsReturned:
            # if multiple objects with the same HS code (usually differing by productline suffix)
            # choose the one lowest in hierarchy
            objs = model_class.objects.filter_by_commodity_code(code_norm).order_by(
                "-number_indents"
            )
            return objs.first()

    raise HierarchyModelNotFound()


def _replace_hs_code(country_code, code_match):
    full_code = code_match.group()
    code = next(code for code in code_match.groups() if code)
    code_stripped = code.replace(".", "").strip()

    if len(code) == 1:
        code_stripped = f"0{code_stripped}"

    try:
        obj = _find_hierarchy_model(code_stripped)
    except HierarchyModelNotFound:
        return full_code

    detail_url = obj.get_detail_url(country_code)
    hierarchy_context_url = reverse(
        "hierarchy-context-tree",
        kwargs={
            "commodity_type": obj.__class__.__name__.lower(),
            "commodity_code": obj.commodity_code,
            "nomenclature_sid": obj.goods_nomenclature_sid,
            "country_code": country_code.lower(),
        },
    )
    url_element = (
        f'<a class="govuk-link hierarchy-modal" data-toggle="modal" data-target="hierarchy-modal" '
        f'data-href="{hierarchy_context_url}" href="{detail_url}">{code}</a>'
    )

    return full_code.replace(code, url_element)


def _process_hs_codes_in_subtext(country_code, subtext_match):
    subtext = subtext_match.group()

    sub = partial(_replace_hs_code, country_code)
    subtext_replaced = CODES_REGEX.sub(sub, subtext)

    return subtext_replaced


@register.filter(name="linkify_hs_codes")
def linkify_hs_codes(value, country_code):
    if not isinstance(value, str):
        return ""

    sub = partial(_process_hs_codes_in_subtext, country_code)
    processed_text = SUBTEXT_REGEX.sub(sub, value)

    return mark_safe(processed_text)


ABBR_REGEX = re.compile(r"\b(CC|CTH|CTSH|MaxNOM)\b")

ABBR_DEFINITIONS = {
    "CC": "Change of Chapter",
    "CTH": "Change in tariff heading",
    "CTSH": "Change in tariff subheading",
    "MaxNOM": "Maximum value of non-originating materials",
}


def _replace_abbrs(abbr_match):
    abbr = abbr_match.group()
    abbr_definition = ABBR_DEFINITIONS[abbr]

    url_element = f'<abbr title="{abbr_definition}">{abbr}</abbr>'

    return url_element


@register.filter(name="annotate_abbreviations")
def annotate_abbreviations(value):
    processed_text = ABBR_REGEX.sub(_replace_abbrs, value)

    return mark_safe(processed_text)
