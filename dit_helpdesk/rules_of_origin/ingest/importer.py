from typing import Union
import datetime as dt
import logging

from django.db.models import Q
from django.conf import settings

from rules_of_origin.models import (
    RulesDocument, RulesDocumentFootnote,
    Rule, SubRule,
)
from hierarchy.models import NomenclatureTree, Chapter, Heading, SubHeading
from countries.models import Country

from .parser import parse_file


logger = logging.getLogger(__name__)


class InvalidDocumentException(Exception):
    pass


class MultipleStartDatesException(InvalidDocumentException):
    pass


def _create_document(name, countries_with_dates, region):
    start_dates = [d['validFrom'] for d in countries_with_dates]
    country_codes = [d['code'] for d in countries_with_dates]

    if len(set(start_dates)) != 1:
        raise MultipleStartDatesException

    start_date = dt.datetime.strptime(start_dates[0], '%Y-%m-%d')

    countries = Country.objects.filter(
        country_code__in=country_codes
    )
    if countries.count() != len(country_codes):
        found_codes = countries.values_list('country_code', flat=True)
        missing_codes = set(country_codes) - set(found_codes)
        raise InvalidDocumentException(
            f"Couldn't find countries with country codes: {missing_codes}")

    logger.info("Creating document %s..", name)
    nomenclature_tree = NomenclatureTree.get_active_tree(region)

    rules_document = RulesDocument.objects.create(
        nomenclature_tree=nomenclature_tree,
        description=name,
        start_date=start_date,
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
            description=subposition['description'],
            rule_text=subposition['rule1'],
            alt_rule_text=subposition['rule2'],
        )
        subrules.append(subrule)

    return subrules


def _commodity_code_to_int(heading_code):
    return int(heading_code.lstrip('0'))


def _fill_zeros(code: Union[int, str]) -> str:
    code = str(code)

    return code.ljust(10, '0')


def _int_to_code(code: int, original_length):
    return _fill_zeros(str(code).rjust(original_length))


def _normalise_code(code: str):
    if code:
        return code.replace(".", "")


def _determine_range_model(hs_type, hs_from):
    if hs_type == 'CH':
        return Chapter
    elif hs_type == 'PO':
        if len(hs_from) == 4:
            return Heading
        elif len(hs_from) == 6:
            return SubHeading


def _get_objects_for_range(hs_type, hs_from, hs_to, region):
    hs_from, hs_to = _normalise_code(hs_from), _normalise_code(hs_to)
    if hs_to and len(hs_from) != len(hs_to):
        raise InvalidDocumentException(
            f"hsFrom ({hs_from}) and hsTo ({hs_to}) have to apply to the same level HS codes")

    range_model = _determine_range_model(hs_type, hs_from)
    if not range_model:
        raise InvalidDocumentException(
            f"Unsupported HS range for hs_type {hs_type} and length {len(hs_from)}")

    hs_range = [_fill_zeros(hs_from)]

    initial_hs_int = _commodity_code_to_int(hs_from)

    if hs_to:
        hs_delta = _commodity_code_to_int(hs_to) - initial_hs_int
        hs_range = [
            _int_to_code(initial_hs_int + increment, original_length=len(hs_from))
            for increment in range(hs_delta + 1)
        ]

    arg_name_map = {
        SubHeading: 'commodity_code__in',
        Heading: 'heading_code__in',
        Chapter: 'chapter_code__in',
    }
    arg_name = arg_name_map[range_model]
    query = Q(**{arg_name: hs_range})

    objects = range_model.objects.for_region(region).filter(query)

    return range_model, objects


def _process_inclusion(rule, inclusion, region):

    rule.is_exclusion = inclusion.get('ex') == 'true'

    hs_type = inclusion['hsFromType']
    hs_to_type = inclusion.get('hsToType')
    if hs_to_type and hs_type != hs_to_type:
        raise InvalidDocumentException(
            f"RoO HS range has to be defined in consistent units: {inclusion}"
        )

    range_model, objects_to_bind = _get_objects_for_range(
        hs_type=hs_type,
        hs_from=inclusion['hsFrom'],
        hs_to=inclusion.get('hsTo'),
        region=region,
    )

    rule_m2m_mapping = {
        Chapter: rule.chapters,
        Heading: rule.headings,
        SubHeading: rule.subheadings,
    }

    m2m_set = rule_m2m_mapping[range_model]
    m2m_set.set(objects_to_bind)

    rule.save()

    return objects_to_bind


def _create_rules(rules_document, positions, region):

    for position in positions:

        description = position['description']
        logger.info("Creating rule %s..", description[:25])

        rule = Rule.objects.create(
            rules_document=rules_document,
            code=position['code'],
            description=description,
            rule_text=position['rule1'],
            alt_rule_text=position['rule2'],
        )

        _process_inclusion(rule, position['inclusion'], region)

        _create_subrules(rule, position['subpositions'])


def _create_notes(rules_document, notes):
    note_objects = []

    for idx, note in enumerate(notes, start=1):
        content = note['content']
        logger.info("Creating note %s..", content[:25])

        note_obj = RulesDocumentFootnote.objects.create(
            rules_document=rules_document,
            number=idx,
            identifier=note['identifier'],
            note=content,
        )
        note_objects.append(note_obj)

    return note_objects


def import_roo(f, region=settings.PRIMARY_REGION):
    logger.info("Importing file %s..", f)

    roo_data = parse_file(f)

    rules_document = _create_document(
        name=roo_data['name'],
        countries_with_dates=roo_data['countries_with_dates'],
        region=region,
    )

    _create_rules(rules_document, roo_data['positions'], region=region)

    _create_notes(rules_document, roo_data['notes'])


if __name__ == '__main__':
    import_roo('PSRO_UK_EN-UK-CL-FTA.xml')
    import ipdb; ipdb.set_trace()
