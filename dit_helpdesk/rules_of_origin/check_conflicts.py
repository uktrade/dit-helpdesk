from django.db.models import BigIntegerField, CharField, Q, Value
from django.db.models.functions import Cast, Length, Replace, RPad

from core.helpers import chunks, unique

from countries.models import Country

from rules_of_origin.models import Rule, RulesDocument

from datetime import date


CharField.register_lookup(Length)


def get_sub_heading_rules():
    sub_heading_rules = Rule.objects.filter(
        Q(hs_to__length__gte=6) | Q(hs_from__length__gte=6)
    )

    return sub_heading_rules


def _normalise_commodity_code_field(field_name):
    return Cast(
        RPad(
            Replace(field_name, Value(".")),
            12,
            Value("0"),
        ),
        output_field=BigIntegerField(),
    )


def _normalised_code(commodity_code):
    return commodity_code.ljust(12, "0")


def _get_hierarchy_codes(commodity_code):
    current_code = ""
    for chunk in chunks(commodity_code, 2):
        current_code += chunk
        yield _normalised_code(current_code)


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

    rules = {}

    # Loop through multiple rule documents to catch countries with GSP rules
    for rule_doc in rule_docs_to_apply:
        potential_rules = rule_doc.rule_set.annotate(
            normalised_hs_from=_normalise_commodity_code_field("hs_from"),
            normalised_hs_to=_normalise_commodity_code_field("hs_to"),
        )
        applied_rules = rule_doc.rule_set.none()

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

        rules[rule_doc] = applied_rules

    return rules


def check_rules(original_rule, possible_rules):
    for doc, rules in possible_rules.items():
        for rule in rules:
            if original_rule == rule:
                continue
            if rule.hs_type == "PO":
                if rule.hs_from:
                    hs_from = rule.hs_from.replace(".", "")
                    if len(hs_from) < 6:
                        return rule
                if rule.hs_to:
                    hs_to = rule.hs_to.replace(".", "")
                    if len(hs_to) < 6:
                        return rule

    return None


def find_hypothetical_rules():
    non_extract_subheading_rules = get_sub_heading_rules().filter(is_extract=False)

    conflicting_rules = []

    for rule in non_extract_subheading_rules:
        if rule.hs_from:
            hs_from = rule.hs_from.replace(".", "")
            possible_rules = get_rules_of_origin(
                hs_from, rule.rules_document.countries.first().country_code
            )
            conflicting_rule = check_rules(rule, possible_rules)
            if conflicting_rule:
                conflicting_rules.append((rule, conflicting_rule))

        if rule.hs_to:
            hs_to = rule.hs_to.replace(".", "")
            possible_rules = get_rules_of_origin(
                hs_to, rule.rules_document.countries.first().country_code
            )
            conflicting_rule = check_rules(rule, possible_rules)
            if conflicting_rule:
                conflicting_rules.append((rule, conflicting_rule))

    return conflicting_rules
