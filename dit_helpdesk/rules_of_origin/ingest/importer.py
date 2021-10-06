from typing import Union, Iterable
from itertools import chain
from collections import defaultdict
import datetime as dt
import logging

from django.db.models import Q
from django.conf import settings

from rules_of_origin.models import RulesDocument, RulesDocumentFootnote, Rule, SubRule
from hierarchy.models import NomenclatureTree, Chapter, Heading, SubHeading
from commodities.models import Commodity
from countries.models import Country

from .parser import parse_file


logger = logging.getLogger(__name__)


class InvalidDocumentException(Exception):
    pass


class MultipleStartDatesException(InvalidDocumentException):
    pass


class RulesDocumentAlreadyExistsException(InvalidDocumentException):
    def __init__(self, message, country):
        super().__init__(message)
        self.country = country


def _create_document(name, countries_with_dates, gb_start_date, region):
    country_codes = [d["code"] for d in countries_with_dates]

    start_date = dt.datetime.strptime(gb_start_date, "%Y-%m-%d")

    countries = Country.objects.filter(
        Q(country_code__in=country_codes)
        | Q(alternative_non_trade_country_code__in=country_codes)
    )
    if countries.count() != len(country_codes):
        found_codes = countries.values_list("country_code", flat=True)
        missing_codes = set(country_codes) - set(found_codes)
        raise InvalidDocumentException(
            f"Couldn't find countries with country codes: {missing_codes}"
        )

    nomenclature_tree = NomenclatureTree.get_active_tree(region)

    for country in countries:
        existing_rules_document = RulesDocument.objects.filter(
            countries=country, nomenclature_tree=nomenclature_tree
        )
        if existing_rules_document:
            raise RulesDocumentAlreadyExistsException(
                "RulesDocument has already been created for country_code"
                f" {country.country_code} \nduring this operation, check your source"
                " folder for duplicate XMLs or errors.",
                country=country,
            )

    logger.info("Creating document %s..", name)

    rules_document = RulesDocument.objects.create(
        nomenclature_tree=nomenclature_tree, description=name, start_date=start_date
    )
    rules_document.countries.set(countries)
    rules_document.save()

    return rules_document


def _create_subrules(rule, subpositions):
    subrules = []

    for idx, subposition in enumerate(subpositions, start=1):
        subrule = SubRule.objects.create(
            rule=rule,
            order=idx,
            description=subposition["description"],
            rule_text=subposition["rule1"],
            alt_rule_text=subposition["rule2"],
        )
        subrules.append(subrule)

    return subrules


def _commodity_code_to_int(heading_code):
    return int(heading_code.lstrip("0"))


def _fill_zeros(code: Union[int, str]) -> str:
    code = str(code)

    return code.ljust(10, "0")


def _left_fill_zeros(code: Union[int, str], length) -> str:
    code = str(code)

    return code.rjust(length, "0")


def _int_to_code(code: int, left_pad=0):
    return _fill_zeros(_left_fill_zeros(str(code), left_pad))


def _normalise_code(code: str):
    if code:
        return code.replace(".", "")


def _determine_range_models(hs_type, hs_from):
    if hs_type == "CH":
        return [Chapter]
    elif hs_type == "PO":
        if len(hs_from) == 4:
            return [Heading, SubHeading]
        elif len(hs_from) == 6:
            return [SubHeading, Commodity]


def _group_by_class(iterable: Iterable) -> dict:
    grouped = defaultdict(list)

    for obj in iterable:
        grouped[obj.__class__].append(obj)

    return grouped


def _get_same_level_objects_for_range(hs_type, hs_from, hs_to, region):
    """Treat subheading/commodity as the same level, as it's not possible to differentiate them
    from Mendel data only.

    """
    hs_from, hs_to = _normalise_code(hs_from), _normalise_code(hs_to)
    if hs_to and len(hs_from) != len(hs_to):
        raise InvalidDocumentException(
            f"hsFrom ({hs_from}) and hsTo ({hs_to}) have to apply to the same level HS"
            " codes"
        )

    range_models = _determine_range_models(hs_type, hs_from)
    if not range_models:
        raise InvalidDocumentException(
            f"Unsupported HS range for hs_type {hs_type} and length {len(hs_from)}"
        )

    hs_range = [_fill_zeros(hs_from)]

    initial_hs_int = _commodity_code_to_int(hs_from)

    if hs_to and hs_to != hs_from:
        hs_delta = _commodity_code_to_int(hs_to) - initial_hs_int
        hs_range = [
            _int_to_code(initial_hs_int + increment, left_pad=len(hs_from))
            for increment in range(hs_delta + 1)
        ]

    arg_name_map = {
        Commodity: "commodity_code__in",
        SubHeading: "commodity_code__in",
        Heading: "heading_code__in",
        Chapter: "chapter_code__in",
    }

    objects = []
    for range_model in range_models:
        arg_name = arg_name_map[range_model]
        query = Q(**{arg_name: hs_range})

        objects = chain(objects, range_model.objects.for_region(region).filter(query))

    return objects


def _higher_level_prefix(hs_code):
    return hs_code[:-2]


def _get_objects_for_range(hs_type, hs_from, hs_to, region):
    """The tricky case is when hsTo and hsFrom are defined on different levels of hierarchy.
    If that's the case, split the range into two consistent ranges.
    E.g. 3205.50 to 3207 => (3205.50 to 3205.99) + (3206 to 3207)

    Or 3510 to 3512.50 => (3510 to 3511) + (3512.00 to 3512.50)

    """

    hs_from = _normalise_code(hs_from)
    hs_to = _normalise_code(hs_to)

    if not hs_to or len(hs_from) == len(hs_to):
        return _group_by_class(
            _get_same_level_objects_for_range(hs_type, hs_from, hs_to, region)
        )

    if len(hs_from) > len(hs_to):
        subheadings_to = _higher_level_prefix(hs_from) + "99"
        headings_from = _left_fill_zeros(
            int(_higher_level_prefix(hs_from)) + 1, length=4
        )

        subheadings_range = _get_same_level_objects_for_range(
            hs_type, hs_from, subheadings_to, region
        )
        headings_range = _get_same_level_objects_for_range(
            hs_type, headings_from, hs_to, region
        )

    elif len(hs_to) > len(hs_from):
        headings_to = _left_fill_zeros(int(_higher_level_prefix(hs_to)) - 1, length=4)
        subheadings_from = (
            _higher_level_prefix(hs_to) + "00"
        )  # beginning of subheading range

        subheadings_range = _get_same_level_objects_for_range(
            hs_type, subheadings_from, hs_to, region
        )
        headings_range = _get_same_level_objects_for_range(
            hs_type, hs_from, headings_to, region
        )

    return _group_by_class(chain(subheadings_range, headings_range))


def _process_inclusion(rule, inclusion, region):

    rule.is_exclusion = inclusion.get("ex") == "true"

    hs_type = inclusion["hsFromType"]
    hs_to_type = inclusion.get("hsToType")
    if hs_to_type and hs_type != hs_to_type:
        raise InvalidDocumentException(
            f"RoO HS range has to be defined in consistent units: {inclusion}"
        )

    ranges_objects = _get_objects_for_range(
        hs_type=hs_type,
        hs_from=inclusion["hsFrom"],
        hs_to=inclusion.get("hsTo"),
        region=region,
    )

    rule_m2m_mapping = {
        Chapter: rule.chapters,
        Heading: rule.headings,
        SubHeading: rule.subheadings,
        Commodity: rule.commodities,
    }

    for range_model, objects_to_bind in ranges_objects.items():
        m2m_set = rule_m2m_mapping[range_model]
        m2m_set.set(objects_to_bind)

    rule.save()

    return ranges_objects


def _create_rules(rules_document, positions, region):

    for position in positions:

        description = position["description"]
        logger.info(
            "Creating rule %s..",
            description[:25] if description else "(empty description)",
        )

        rule = Rule.objects.create(
            rules_document=rules_document,
            code=position["code"],
            description=description,
            rule_text=position["rule1"],
            alt_rule_text=position["rule2"],
        )

        _process_inclusion(rule, position["inclusion"], region)

        _create_subrules(rule, position["subpositions"])


def _create_notes(rules_document, notes):
    note_objects = []

    for idx, note in enumerate(notes, start=1):
        content = note["content"]
        logger.info("Creating note %s..", content[:25])

        note_obj = RulesDocumentFootnote.objects.create(
            rules_document=rules_document,
            number=idx,
            identifier=note["identifier"],
            note=content,
        )
        note_objects.append(note_obj)

    return note_objects


def import_roo(f, region=settings.PRIMARY_REGION):
    logger.info("Importing file %s..", f)

    roo_data = parse_file(f)

    rules_document = _create_document(
        name=roo_data["name"],
        countries_with_dates=roo_data["countries_with_dates"],
        gb_start_date=roo_data["gb_start_date"],
        region=region,
    )

    _create_rules(rules_document, roo_data["positions"], region=region)

    _create_notes(rules_document, roo_data["notes"])

    return rules_document


def check_countries_consistency():
    nomenclature_tree = NomenclatureTree.get_active_tree(settings.PRIMARY_REGION)

    # Get the list of countries we know have trade agreements
    countries = Country.objects.filter(Q(has_uk_trade_agreement=True))

    missing_countries_list = []

    for country in countries:
        # Check a rules document has been created for each of these countries
        rules_document = RulesDocument.objects.filter(
            countries=country, nomenclature_tree=nomenclature_tree
        )
        if not rules_document and country.country_code != "EU":
            # If there is no rules document, we need to raise the warning that we were expecting one
            missing_countries_list.append(country.country_code + " - " + country.name)

    if len(missing_countries_list) > 0:
        logger.error(
            "Completed consistency check, the following countries have trade agreements"
            " but are missing in the RoO documents: %s Please check the data files,"
            " they may be out of date",
            missing_countries_list,
        )


if __name__ == "__main__":
    import_roo("PSRO_UK_EN-UK-CL-FTA.xml")
    import ipdb

    ipdb.set_trace()
