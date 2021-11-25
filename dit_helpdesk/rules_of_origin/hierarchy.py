import logging

from django.db.models import BigIntegerField, Value
from django.db.models.functions import Cast, Replace, RPad

from rules_of_origin.footnote_processor import FootnoteReferenceProcessor

from core.helpers import unique_maintain_order

from countries.models import Country

from .models import RulesDocument, RulesDocumentFootnote

from datetime import date

logger = logging.getLogger(__name__)


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]  # noqa: E203


def _get_hierarchy_codes(commodity_code):
    current_code = ""
    for chunk in chunks(commodity_code, 2):
        current_code += chunk
        yield current_code


def _normalised_code(commodity_code):
    return commodity_code.ljust(12, "0")


def _normalise_commodity_code_field(field_name):
    return Cast(
        RPad(
            Replace(field_name, Value(".")),
            12,
            Value("0"),
        ),
        output_field=BigIntegerField(),
    )


def _process_rule_references(rule, footnote_processor):

    """Rule text may contain references to footnotes. Extract them from rule text.
    The Rule object is not saved - the changes are only persisted in memory because the same
    rule may be reused for different commodity objects and the order of notes (and their
    numbering) may change for these objects. So it's necessary to recalculate on the fly and
    not persist the result - the in-memory version is used for rendering from current view
    though.
    """

    rule.rule_text_processed = footnote_processor.replace_all_notes_references(
        rule.rule_text_processed
    )

    rule.alt_rule_text_processed = footnote_processor.replace_all_notes_references(
        rule.alt_rule_text_processed
    )

    for subrule in rule.subrules.all():
        subrule.rule_text_processed = footnote_processor.replace_all_notes_references(
            subrule.rule_text_processed
        )

        subrule.alt_rule_text_processed = (
            footnote_processor.replace_all_notes_references(
                subrule.alt_rule_text_processed
            )
        )


def _process_footnotes(rules, notes):
    footnote_processor = FootnoteReferenceProcessor()

    for rule in rules:
        _process_rule_references(rule, footnote_processor)

    found_note_ids = unique_maintain_order(footnote_processor.found_note_ids)
    notes_by_id = {}

    # Check that we are not missing footnotes that we expect to exist
    if not notes and len(found_note_ids) > 0:
        raise RulesDocumentFootnote.DoesNotExist(
            "Missing expected footnotes for this commodity code"
        )

    for alpha_ord, note in enumerate(notes, ord("a")):
        notes_by_id[note.identifier] = note
        alpha_identifier = chr(alpha_ord)
        notes_by_id[alpha_identifier] = note

    filtered_notes = [(note_id, notes_by_id[note_id]) for note_id in found_note_ids]

    for note_id, note in filtered_notes:
        note.number = footnote_processor.note_number_by_id[note_id]
        note.note = footnote_processor.replace_all_introductory_notes_references(
            note.note
        )
    return [note for _, note in filtered_notes]


def get_rules_of_origin(commodity_code, country_code):

    if country_code == "EU":
        country_code = (
            "FR"  # pick one of the EU countries, the RoO are the same for all
        )

    country = Country.objects.get(country_code=country_code)

    rule_docs_to_apply = RulesDocument.objects.filter(
        countries=country,
        start_date__lte=date.today(),
    )

    # Loop through multiple rule documents to catch countries with GSP rules
    rule_doc_dict = {}
    for rule_doc in rule_docs_to_apply:
        potential_rules = rule_doc.rule_set.annotate(
            normalised_hs_from=_normalise_commodity_code_field("hs_from"),
            normalised_hs_to=_normalise_commodity_code_field("hs_to"),
        )
        applied_rules = rule_doc.rule_set.none()

        for hierarchy_code in _get_hierarchy_codes(commodity_code):
            hierarchy_rules = potential_rules.filter(
                hs_to__isnull=True,
                normalised_hs_from=int(_normalised_code(hierarchy_code)),
            )
            applied_rules = applied_rules.union(hierarchy_rules)

        applied_rules = applied_rules.union(
            potential_rules.filter(
                hs_to__isnull=False,
                normalised_hs_from__lte=int(_normalised_code(commodity_code)),
                normalised_hs_to__gte=int(_normalised_code(commodity_code)),
            )
        )

        for hierarchy_code in _get_hierarchy_codes(commodity_code):
            hierarchy_rules = potential_rules.filter(
                hs_to__isnull=False,
                normalised_hs_to=int(_normalised_code(hierarchy_code)),
            )
            applied_rules = applied_rules.union(hierarchy_rules)

        ch_level_ex_rule_exists = False
        po_level_ex_rule_exists = False
        for rule in applied_rules:
            if rule.hs_type == "CH" and rule.is_extract:
                ch_level_ex_rule_exists = True
            if rule.hs_type == "PO" and rule.is_extract:
                po_level_ex_rule_exists = True

        # If we have an ex chapter rule, but no lower level rules, we need to skip this filter to display the rule
        # If we have lower level ex rules and an ex chapter rule, we need to skip the filter so it is displayed
        # If we have lower level non-ex rules and an ex chapter rule, we need to add the filter to not display the rule
        if (
            len(applied_rules) > 1
            and ch_level_ex_rule_exists
            and not po_level_ex_rule_exists
        ):
            exclusion_rules = potential_rules.filter(
                hs_from=hierarchy_code[:2],
                is_extract=True,
            )

            applied_rules = applied_rules.difference(exclusion_rules)

        # Order rules by their code - this will also arrange them in level order
        applied_rules = applied_rules.all().order_by("hs_from")

        # get footnotes
        footnotes = RulesDocumentFootnote.objects.filter(
            rules_document_id=rule_doc.id
        ).order_by("id")

        relevant_footnotes = _process_footnotes(list(applied_rules), footnotes)

        # get introductory notes
        try:
            introductory_notes = footnotes.get(
                identifier="COMM",
            )
        except RulesDocumentFootnote.DoesNotExist:
            introductory_notes = None

            roo_exist = RulesDocument.objects.filter(countries=country).exists()

            if roo_exist:
                logger.error("Could not find introductory notes for %s", country)

        rules_of_origin = {
            "rules": list(applied_rules),
            "footnotes": relevant_footnotes,
            "introductory_notes": introductory_notes,
            "rule_doc_name": str(rule_doc),
        }

        rule_doc_dict[str(rule_doc)] = rules_of_origin

    return rule_doc_dict
