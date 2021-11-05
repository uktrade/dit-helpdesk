from django.db.models import BigIntegerField, Value
from django.db.models.functions import Cast, Replace, RPad

from countries.models import Country

from .models import RulesDocument


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


def get_rules_of_origin(commodity_code, country_code):
    from hierarchy.models import NomenclatureTree

    if country_code == "EU":
        country_code = (
            "FR"  # pick one of the EU countries, the RoO are the same for all
        )

    tree = NomenclatureTree.get_active_tree()
    country = Country.objects.get(country_code=country_code)

    rule_doc_to_apply = RulesDocument.objects.get(
        countries=country,
        nomenclature_tree=tree,
    )

    potential_rules = rule_doc_to_apply.rule_set.annotate(
        normalised_hs_from=_normalise_commodity_code_field("hs_from"),
        normalised_hs_to=_normalise_commodity_code_field("hs_to"),
    )
    applied_rules = rule_doc_to_apply.rule_set.none()

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

    return applied_rules
