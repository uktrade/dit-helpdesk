import datetime as dt
import logging

from django.db.models import Q
from django.conf import settings

from rules_of_origin.models import RulesDocument, RulesDocumentFootnote, Rule, SubRule
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


def _create_document(name, countries_with_dates, gb_start_date):
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

    for country in countries:
        # Certain country TA scenarios have multiple rule documents, must check others
        # to prevent duplicates in source data
        if country.scenario not in settings.MULTIPLE_ROO_SCENARIOS:
            existing_rules_document = RulesDocument.objects.filter(countries=country)
            if existing_rules_document:
                raise RulesDocumentAlreadyExistsException(
                    "RulesDocument has already been created for country_code"
                    f" {country.country_code} \nduring this operation, check your source"
                    " folder for duplicate XMLs or errors.",
                    country=country,
                )

    logger.info("Creating document %s..", name)

    # Note: The rules documents have been seperated from the Nomenclature tree.
    # there were previously multiple trees we attached rules to - one was for the ni/eu tree
    # however these rules were not displayed anywhere. Other trees seem to be for backup purposes

    rules_document = RulesDocument.objects.create(
        description=name, start_date=start_date
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


def _normalise_code(code: str):
    if code:
        return code.replace(".", "")


def _process_inclusion(rule, inclusion, region):
    rule.is_exclusion = inclusion.get("ex") == "true"
    rule.hs_from = _normalise_code(inclusion["hsFrom"])
    rule.hs_to = _normalise_code(inclusion.get("hsTo"))

    rule.hs_type = inclusion["hsFromType"]
    rule.hs_to_type = inclusion.get("hsToType")
    if rule.hs_to_type and rule.hs_type != rule.hs_to_type:
        raise InvalidDocumentException(
            f"RoO HS range has to be defined in consistent units: {inclusion}"
        )

    rule.save()


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
    )

    _create_rules(rules_document, roo_data["positions"], region=region)

    _create_notes(rules_document, roo_data["notes"])

    return rules_document


def check_countries_consistency():
    # Get the list of countries we know have trade agreements
    countries = [
        country for country in Country.objects.all() if country.has_uk_trade_agreement
    ]

    missing_countries_list = []

    for country in countries:
        # Check a rules document has been created for each of these countries
        rules_document = RulesDocument.objects.filter(countries=country)
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
