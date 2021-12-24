import re
import logging

from django.urls import reverse

from rules_of_origin.models import RulesDocument
from hierarchy.models import Chapter, Heading, SubHeading
from commodities.models import Commodity


logger = logging.getLogger(__name__)


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

ABBR_REGEX = re.compile(r"\b(CC|CTH|CTSH|MaxNOM%?)\b")


HS_LEN_MAPPING = {2: [Chapter], 4: [Heading, SubHeading], 6: [SubHeading, Commodity]}


def postprocess_rules_of_origin():

    active_documents = RulesDocument.objects.all()

    doc_count = active_documents.count()

    for idx, rules_doc in enumerate(active_documents.all(), start=1):
        logger.info(
            "\n\nProcessing rules document %d/%d: %s", idx, doc_count, rules_doc
        )

        inner_idx = 0
        for rule in rules_doc.rule_set.all():
            if inner_idx % 100 == 0:
                logger.info("Processing rule %s", rule)

            rule.description_processed = process_rule_text(rule.description)
            rule.rule_text_processed = process_rule_text(rule.rule_text)
            rule.alt_rule_text_processed = process_rule_text(rule.alt_rule_text)
            rule.save()

            for subrule in rule.subrules.all():
                subrule.description_processed = process_rule_text(subrule.description)
                subrule.rule_text_processed = process_rule_text(subrule.rule_text)
                subrule.alt_rule_text_processed = process_rule_text(
                    subrule.alt_rule_text
                )
                subrule.save()

            inner_idx += 1


def process_rule_text(text):
    if not text:
        return text

    text = process_hs_codes_in_text(text)
    text = process_abbreviations_in_text(text)

    return text


def _replace_hs_code(code_match):
    full_code = code_match.group()
    code = next(code for code in code_match.groups() if code)
    code_stripped = code.replace(".", "").strip()

    if len(code) == 1:
        code_stripped = f"0{code_stripped}"

    models = HS_LEN_MAPPING[len(code_stripped)]

    code_norm = code_stripped.ljust(10, "0")

    url = None

    for model in models:
        arg = {
            Chapter: "chapter_code",
            Heading: "heading_code",
            SubHeading: "commodity_code",
            Commodity: "commodity_code",
        }[model]

        try:
            obj = model.objects.get(**{arg: code_norm})
        except model.DoesNotExist:
            logger.warning("Couldn't find %s object for HS code %s", model, code_norm)
            continue
        except model.MultipleObjectsReturned:
            # if multiple objects with the same HS code (usually differing by productline suffix)
            # choose the one lowest in hierarchy
            objs = model.objects.filter(**{arg: code_norm}).order_by("-number_indents")
            obj = objs.first()

        url_name = "hierarchy-context-tree"

        url = reverse(
            viewname=url_name,
            kwargs={
                "commodity_type": model.__name__.lower(),
                "commodity_code": code_norm,
                "nomenclature_sid": obj.goods_nomenclature_sid,
                "country_code": "country_code",  # to be replaced/formatted at a later stage
            },
        )
        url = url.replace("country_code", "{country_code}")

    if url:
        url_element = (
            f'<a data-toggle="modal" data-target="hierarchy-modal" href="javascript:void(0)" '
            f'class="hierarchy-modal" data-href="{url}">{code}</a>'
        )
        return full_code.replace(code, url_element)
    else:
        return full_code


def _process_hs_codes_in_subtext(subtext_match):
    subtext = subtext_match.group()

    subtext_replaced = CODES_REGEX.sub(_replace_hs_code, subtext)

    return subtext_replaced


def process_hs_codes_in_text(text):
    processed_text = SUBTEXT_REGEX.sub(_process_hs_codes_in_subtext, text)

    return processed_text


def _replace_abbrs(abbr_match):
    abbr = abbr_match.group()
    abbr_cleaned = abbr.strip(" %").lower()

    url_element = (
        f'<a data-toggle="modal" data-target="roo-abbr-{abbr_cleaned}-modal" '
        f'href="javascript:void(0)">{abbr}</a>'
    )

    return url_element


def process_abbreviations_in_text(text):

    processed_text = ABBR_REGEX.sub(_replace_abbrs, text)

    return processed_text
