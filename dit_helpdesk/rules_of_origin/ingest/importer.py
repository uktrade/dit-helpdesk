import logging

from django.db.models import Q

from rules_of_origin.models import (
    RulesDocument, RulesDocumentFootnote,
    Rule, SubRule,
)
from hierarchy.models import Chapter, Heading
from countries.models import Country

from .parser import parse_file


logger = logging.getLogger(__name__)


class InvalidDocumentException(Exception):
    pass


class MultipleStartDatesException(InvalidDocumentException):
    pass


def _create_document(name, countries_with_dates):
    start_dates = [d['validFrom'] for d in countries_with_dates]
    country_codes = [d['code'] for d in countries_with_dates]

    if len(set(start_dates)) != 1:
        raise MultipleStartDatesException

    start_date = start_dates[0]

    countries = Country.objects.filter(
        country_code__in=country_codes
    )
    if countries.count() != len(country_codes):
        found_codes = countries.values_list('country_code', flat=True)
        missing_codes = set(country_codes) - set(found_codes)
        raise InvalidDocumentException(
            f"Couldn't find countries with country codes: {missing_codes}")

    logger.info("Creating document %s..", name)
    rules_document = RulesDocument.objects.create(
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


def _int_to_code(code: int, original_length):
    return str(code).rjust(original_length).ljust(10, '0')


def _normalise_code(code: str):
    if code:
        return code.replace(".", "")


def _get_objects_for_range(hs_type, hs_from, hs_to):
    hs_from, hs_to = _normalise_code(hs_from), _normalise_code(hs_to)
    if hs_to and len(hs_from) != len(hs_to):
        raise InvalidDocumentException(
            f"hsFrom ({hs_from}) and hsTo ({hs_to}) have to apply to the same level HS codes")

    hs_range = [hs_from]

    initial_hs_int = _commodity_code_to_int(hs_from)

    if hs_to:
        hs_delta = _commodity_code_to_int(hs_to) - initial_hs_int
        hs_range = [
            _int_to_code(initial_hs_int + increment, original_length=len(hs_from))
            for increment in range(hs_delta + 1)
        ]

    arg_name_map = {
        'PO': 'heading_code__in',
        'CH': 'chapter_code__in',
    }
    arg_name = arg_name_map[hs_type]
    query = Q(**{arg_name: hs_range})

    model_map = {
        'PO': Heading,
        'CH': Chapter,
    }
    model = model_map[hs_type]

    objects = model.objects.filter(query)

    return objects


def _process_inclusions(rule, inclusions):

    rule.is_exclusion = inclusions.get('ex') == 'true'

    hs_type = inclusions['hsFromType']
    hs_to_type = inclusions.get('hsToType')
    if hs_to_type and hs_type != hs_to_type:
        raise InvalidDocumentException(
            f"RoO HS range has to be defined in consistent units: {inclusions}"
        )

    objects_to_bind = _get_objects_for_range(
        hs_type=hs_type,
        hs_from=inclusions['hsFrom'],
        hs_to=inclusions.get('hsTo')
    )

    if hs_type == 'CH':
        rule.chapters.set(objects_to_bind)
    elif hs_type == 'PO':
        rule.headings.set(objects_to_bind)

    rule.save()

    return objects_to_bind


def _create_rules(rules_document, positions):

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

        _process_inclusions(rule, position['inclusions'])

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


def import_roo(f):
    logger.info("Imprting file %s..", f)

    roo_data = parse_file(f)

    rules_document = _create_document(
        name=roo_data['name'],
        countries_with_dates=roo_data['countries_with_dates']
    )

    _create_rules(rules_document, roo_data['positions'])

    _create_notes(rules_document, roo_data['notes'])


if __name__ == '__main__':
    import_roo('PSRO_UK_EN-UK-CL-FTA.xml')
    import ipdb; ipdb.set_trace()
