from django.core.management.base import BaseCommand

from django.conf import settings
from django.db import transaction

from hierarchy.models import NomenclatureTree, Section, Chapter, Heading, SubHeading
from commodities.models import Commodity
from regulations.models import RegulationGroup, Regulation
from regulations.hierarchy import promote_regulation_groups, replicate_regulation_groups
from hierarchy.helpers import process_swapped_tree


def _get_codes(m2m, prev_tree, attr_name="goods_nomenclature_sid"):
    return (
        m2m(manager="all_objects")
        .filter(nomenclature_tree=prev_tree)
        .values_list(attr_name, flat=True)
    )


MODEL_CLASSES = [
    (Chapter, "chapters"),
    (Heading, "headings"),
    (SubHeading, "subheadings"),
    (Commodity, "commodities"),
]


def _get_sids(regulation_group, prev_tree):
    sids = None

    for _, m2m_attr in MODEL_CLASSES:
        m2m = getattr(regulation_group, m2m_attr)

        new_sids = _get_codes(m2m, prev_tree)
        if sids is None:
            sids = new_sids
        else:
            sids = sids.union(new_sids)

    return sids


class Command(BaseCommand):
    help = """Command to migrate regulations from a previous NomenclatureTree to the current one"""

    def handle(self, *args, **options):
        self.stdout.write("Migrating regulations..")

        with transaction.atomic():
            # Promote the regulations for the currently active tree.
            for section in Section.objects.all():
                # We replicate the regulation groups so that when we copy between trees and a move has been made all of
                # the regulations pertaining to the moved commodity object (including those inherited) will also be
                # copied.
                replicate_regulation_groups(section)

            with process_swapped_tree():
                new_tree = NomenclatureTree.get_active_tree()
                prev_tree = NomenclatureTree.objects.filter(
                    region=settings.PRIMARY_REGION, start_date__lt=new_tree.start_date
                ).latest("start_date")

                self.stdout.write(f"New tree: {new_tree}")
                self.stdout.write(f"Previous tree: {prev_tree}")

                prev_tree_groups = prev_tree.regulationgroup_set.all()
                # if for some reason previous tree doesn't have RegulationGroups assigned (e.g.
                # running this for the first time without running import_initial_regulations),
                # take all of them
                regulation_groups = (
                    prev_tree_groups
                    if prev_tree_groups.exists()
                    else RegulationGroup.objects.all()
                )
                new_tree.regulationgroup_set.set(regulation_groups)

                prev_tree_regulations = prev_tree.regulation_set.all()
                # same here
                regulations = (
                    prev_tree_regulations
                    if prev_tree_groups.exists()
                    else Regulation.objects.all()
                )
                new_tree.regulation_set.set(regulations)
                new_tree.save()

                for regulation_group in regulation_groups:
                    self.stdout.write(
                        f"Migrating regulation group {regulation_group}.."
                    )

                    goods_nomenclature_sids = _get_sids(regulation_group, prev_tree)
                    for model_class, m2m_attr in MODEL_CLASSES:
                        objects = model_class.objects.filter(
                            goods_nomenclature_sid__in=goods_nomenclature_sids
                        )
                        m2m = getattr(regulation_group, m2m_attr)
                        m2m.add(*objects)

                    # assign sections
                    section_codes = _get_codes(
                        regulation_group.sections, prev_tree, "roman_numeral"
                    )
                    new_sections = Section.objects.filter(
                        roman_numeral__in=section_codes
                    )
                    regulation_group.sections.add(*new_sections)

                    regulation_group.save()

                # Promote the regulations for the new tree
                for section in Section.objects.all():
                    promote_regulation_groups(section)

            # Promote the regulations for the previous tree.
            # This undoes our replication at the beginning of this command.
            for section in Section.objects.all():
                promote_regulation_groups(section)

        self.stdout.write("Done!")
