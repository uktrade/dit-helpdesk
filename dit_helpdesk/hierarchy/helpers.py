import contextlib

from django.utils import timezone
from django.db import transaction

from .models import NomenclatureTree

from trade_tariff_service.tts_api import COMMODITY_DETAIL_TABLE_KEYS

TABLE_COLUMN_TITLES = [tup[1] for tup in COMMODITY_DETAIL_TABLE_KEYS]

IMPORT_MEASURE_GROUPS = {
    "Tariffs and charges": (
        ("National duties - VAT", ("305", "VTA", "VTE", "VTS", "VTZ")),
        (
            "National duties - excise",
            (
                "306",
                "DAA",
                "DAB",
                "DAC",
                "DAE",
                "DAI",
                "DBA",
                "DBB",
                "DBC",
                "DBE",
                "DBI",
                "DCA",
                "DCC",
                "DCE",
                "DCH",
                "DDA",
                "DDB",
                "DDC",
                "DDD",
                "DDE",
                "DDF",
                "DDG",
                "DDJ",
                "DEA",
                "DFA",
                "DFB",
                "DFC",
                "DGC",
                "DHA",
                "DHC",
                "DHE",
                "EAA",
                "EAE",
                "EBA",
                "EBB",
                "EBE",
                "EBJ",
                "EDA",
                "EDB",
                "EDE",
                "EDJ",
                "EEA",
                "EEF",
                "EFA",
                "EFJ",
                "EGA",
                "EGB",
                "EGJ",
                "EHI",
                "EIA",
                "EIB",
                "EIC",
                "EID",
                "EIE",
                "EIJ",
                "EXA",
                "EXB",
                "EXC",
                "EXD",
                "FAA",
                "FAE",
                "FAI",
                "FBC",
                "FBG",
                "LAA",
                "LAE",
                "LBA",
                "LBB",
                "LBE",
                "LBJ",
                "LDA",
                "LEA",
                "LEF",
                "LFA",
                "LGJ",
            ),
        ),
        (
            "International duty",
            ("103", "105", "106", "112", "115", "117", "119", "141", "142", "145"),
        ),
        ("Agricultural duty", ("488", "489", "490", "651", "652", "653", "654")),
        (
            "Trade remedy",
            ("551", "552", "553", "554", "555", "561", "564", "565", "566", "570"),
        ),
        ("Safeguards and retaliation", ("695", "696")),
        ("Supplementary unit", ("109", "110")),
    ),
    "Quotas": (("Quotas", ("122", "123", "146", "147")),),
    "Other measures": (
        (
            "Prohibitions and restrictions (or other)",
            (
                "277",
                "278",
                "410",
                "420",
                "465",
                "467",
                "473",
                "474",
                "475",
                "476",
                "478",
                "479",
                "705",
                "706",
                "707",
                "708",
                "709",
                "710",
                "711",
                "712",
                "713",
                "714",
                "715",
                "716",
                "717",
                "718",
                "719",
                "722",
                "724",
                "725",
                "728",
                "730",
                "735",
                "740",
                "745",
                "746",
                "747",
                "748",
                "749",
                "750",
                "751",
                "755",
                "760",
                "761",
                "774",
                "AHC",
                "AIL",
                "ATT",
                "CEX",
                "COE",
                "COI",
                "CVD",
                "EQC",
                "HOP",
                "HSE",
                "PHC",
                "PRE",
                "PRT",
                "QRC",
            ),
        ),
        ("Credibility checks", ("430", "431", "481", "482", "483")),
    ),
}


def get_nomenclature_group_measures(nomenclature_model, group_name, country_code):
    group_measure_type_ids = [
        item
        for collection in [group[1] for group in IMPORT_MEASURE_GROUPS[group_name]]
        for item in collection
    ]

    return [
        measure
        for measure in nomenclature_model.tts_obj.get_import_measures(country_code)
        if measure.type_id in group_measure_type_ids
        and country_code not in [id for id in measure.excluded_country_area_ids]
    ]


def create_nomenclature_tree(region='EU'):
    """Create new nomenclature tree and mark the previous most recent
    one as ended.

    Recommended to run inside transaction, especially if deleting the old tree,
    as when this function returns there are no nomenclature objects attached to the new tree.

    """
    new_start_date = timezone.now()

    prev_tree = NomenclatureTree.get_active_tree(region)
    if prev_tree:
        prev_tree.end_date = new_start_date
        prev_tree.save()

    tree = NomenclatureTree.objects.create(
        region=region,
        start_date=new_start_date,
        end_date=None
    )

    return tree


def delete_all_inactive_trees(region):
    inactive_trees = NomenclatureTree.objects.filter(
        region=region,
        end_date__isnull=False,
    ).all()

    inactive_trees.delete()


def fill_tree_in_json_data(json_data, tree):
    for data in json_data:
        data["nomenclature_tree_id"] = tree.pk

    return json_data


@contextlib.contextmanager
def process_swapped_tree(region='EU'):
    """This enables to populate data to a tree that is active only within transaction,
    and not visible from within the app. Thanks to this we can add data and make the tree
    visibly active only as a very last step.
    This is like making the tree write-active but not read-active which is what we want to ensure
    consistency.

    """
    with transaction.atomic():
        # get latest tree - not yet active because we want to activate it only immediately after
        # finishing reindexing (and swapping index aliases)
        new_tree = NomenclatureTree.objects.filter(region=region).latest('start_date')
        # get active (but not latest) tree
        prev_tree = NomenclatureTree.get_active_tree(region)
        if prev_tree:
            prev_tree.end_date = timezone.now()
            prev_tree.save()

        # activate the latest tree so that ES indexes objects from that tree (but it's not
        # yet visible in the app since the transaction didn't finish)
        new_tree.end_date = None
        new_tree.save()

        yield

        new_tree.end_date = timezone.now()
        new_tree.save()

        prev_tree.end_date = None
        prev_tree.save()
