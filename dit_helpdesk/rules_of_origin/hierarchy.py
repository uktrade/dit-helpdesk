import logging

from django.db.models import BigIntegerField, Case, IntegerField, Value, When
from django.db.models.functions import Cast, Replace, RPad

from rules_of_origin.footnote_processor import FootnoteReferenceProcessor

from core.helpers import chunks, unique

from .models import RulesDocumentFootnote


logger = logging.getLogger(__name__)


def _normalised_code(commodity_code):
    return commodity_code.replace(".", "").ljust(12, "0")


def _get_hierarchy_codes(commodity_code):
    current_code = ""
    for chunk in chunks(commodity_code, 2):
        current_code += chunk
        yield _normalised_code(current_code)


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

    found_note_ids = list(unique(footnote_processor.found_note_ids))
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


def get_rules_of_origin(rules_document, commodity_code):
    potential_rules = rules_document.rule_set.annotate(
        normalised_hs_from=_normalise_commodity_code_field("hs_from"),
        normalised_hs_to=_normalise_commodity_code_field("hs_to"),
    )
    applied_rules = rules_document.rule_set.none()

    for hierarchy_code in unique(_get_hierarchy_codes(commodity_code)):
        hierarchy_rules = potential_rules.filter(
            hs_to__isnull=True,
            normalised_hs_from=int(hierarchy_code),
        )
        applied_rules = applied_rules.union(hierarchy_rules)

    applied_rules = applied_rules.union(
        potential_rules.filter(
            hs_to__isnull=False,
            normalised_hs_from__lte=int(_normalised_code(commodity_code)),
            normalised_hs_to__gte=int(_normalised_code(commodity_code)),
        )
    )

    for hierarchy_code in unique(_get_hierarchy_codes(commodity_code)):
        hierarchy_rules = potential_rules.filter(
            hs_to__isnull=False,
            normalised_hs_to=int(hierarchy_code),
        )
        applied_rules = applied_rules.union(hierarchy_rules)

    applied_rules = rules_document.rule_set.filter(
        pk__in=applied_rules.values_list("pk")
    ).annotate(
        normalised_hs_from=_normalise_commodity_code_field("hs_from"),
        normalised_hs_to=_normalise_commodity_code_field("hs_to"),
        is_leading_rule=Case(
            When(rule_text__isnull=True, then=Value(1, output_field=IntegerField())),
            default=Value(0, output_field=IntegerField()),
        ),
    )
    most_specific_non_extract_rule = (
        applied_rules.filter(is_extract=False)
        .order_by("-is_leading_rule", "-normalised_hs_from")
        .first()
    )
    if most_specific_non_extract_rule:
        applied_rules = applied_rules.filter(
            normalised_hs_from__gte=int(
                _normalised_code(most_specific_non_extract_rule.hs_from)
            )
        )

    applied_rules = applied_rules.order_by("hs_from")

    return applied_rules


def get_rules_footnotes(rules_document, rules):
    footnotes = RulesDocumentFootnote.objects.filter(
        rules_document=rules_document
    ).order_by("id")

    relevant_footnotes = _process_footnotes(list(rules), footnotes)

    return footnotes, relevant_footnotes


def get_rules_introductory_notes(rules_document, footnotes):
    # get introductory notes
    try:
        introductory_notes = footnotes.get(
            identifier="COMM",
        )
    except RulesDocumentFootnote.DoesNotExist:
        introductory_notes = None
        logger.error("Could not find introductory notes for %s", rules_document)

    return introductory_notes
