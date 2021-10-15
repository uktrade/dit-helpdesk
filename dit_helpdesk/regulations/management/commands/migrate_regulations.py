from django.core.management.base import BaseCommand

from django.conf import settings

from hierarchy.models import NomenclatureTree, Section, Chapter, Heading, SubHeading
from commodities.models import Commodity
from regulations.models import RegulationGroup, Regulation
from hierarchy.helpers import process_swapped_tree


def _get_codes(m2m, prev_tree, attr_name="goods_nomenclature_sid"):
    return (
        m2m(manager="all_objects")
        .filter(nomenclature_tree=prev_tree)
        .values_list(attr_name, flat=True)
    )


class Command(BaseCommand):
    help = """Command to migrate regulations from a previous NomenclatureTree to the current one"""

    def handle(self, *args, **options):
        self.stdout.write("Migrating regulations..")

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
                self.stdout.write(f"Migrating regulation group {regulation_group}..")

                # assign commodities
                com_codes = _get_codes(regulation_group.commodities, prev_tree)
                new_commodities = Commodity.objects.filter(
                    goods_nomenclature_sid__in=com_codes
                )

                # special case - if there had been a contraction and commodity became a subheading
                new_subheadings = SubHeading.objects.filter(
                    goods_nomenclature_sid__in=com_codes
                )

                regulation_group.commodities.add(*new_commodities)
                regulation_group.subheadings.add(*new_subheadings)

                # assign subheadings
                subheading_codes = _get_codes(regulation_group.subheadings, prev_tree)
                new_subheadings = SubHeading.objects.filter(
                    goods_nomenclature_sid__in=subheading_codes
                )

                # special case - expansion, subheading became a commodity
                new_commodities = Commodity.objects.filter(
                    goods_nomenclature_sid__in=subheading_codes
                )

                # special case - contraction - not sure if it ever happens though
                new_chapters = Chapter.objects.filter(
                    goods_nomenclature_sid__in=subheading_codes
                )

                regulation_group.subheadings.add(*new_subheadings)
                regulation_group.commodities.add(*new_commodities)
                regulation_group.chapters.add(*new_chapters)

                # assign headings
                heading_codes = _get_codes(regulation_group.headings, prev_tree)
                new_headings = Heading.objects.filter(
                    goods_nomenclature_sid__in=heading_codes
                )
                new_subheadings = SubHeading.objects.filter(
                    goods_nomenclature_sid__in=heading_codes
                )
                regulation_group.headings.add(*new_headings)
                regulation_group.subheadings.add(*new_subheadings)

                # assign chapters
                chapter_codes = _get_codes(regulation_group.chapters, prev_tree)
                new_chapters = Chapter.objects.filter(
                    goods_nomenclature_sid__in=chapter_codes
                )
                new_subheadings = SubHeading.objects.filter(
                    goods_nomenclature_sid__in=chapter_codes
                )

                regulation_group.chapters.add(*new_chapters)
                regulation_group.subheadings.add(*new_subheadings)

                # assign sections
                section_codes = _get_codes(
                    regulation_group.sections, prev_tree, "roman_numeral"
                )
                new_sections = Section.objects.filter(roman_numeral__in=section_codes)
                regulation_group.sections.add(*new_sections)

                regulation_group.save()

        self.stdout.write("Done!")
