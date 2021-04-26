import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from commodities.models import Commodity
from hierarchy.models import NomenclatureTree, Section, Chapter, Heading, SubHeading

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    help = """
        Copies an existing active NomenclatureTree to a new NomenclatureTree, but with a specific,
        start date. It is expected that this will be changed to populate the database and Redis
        with different data

        Expected usage:
        python3 manage.py copy_section_hierarchy --source_tree_id 1 --region UK-FUTURE
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--source_tree_id", nargs=1, type=int, help="ID of tree to copy"
        )
        parser.add_argument(
            "--region", nargs=1, required=True, type=str, help="Region for cloned tree"
        )
        parser.add_argument(
            "--tts_source",
            nargs="?",
            type=str,
            const="original",
            choices=["original", "alt"],
            help="TTS source for cloned tree",
        )

    def handle(self, *args, **options):
        source_tree_id = options["source_tree_id"]
        if source_tree_id is not None:
            source_tree_id = options["source_tree_id"][0]
        region = options["region"][0]
        tts_source = options["tts_source"]

        with transaction.atomic():
            if source_tree_id:
                existing_tree = NomenclatureTree.objects.get(pk=source_tree_id)
            else:
                existing_tree = NomenclatureTree.get_active_tree()

            new_tree = NomenclatureTree.objects.create(
                region=region,
                start_date=existing_tree.start_date,
                end_date=None,
                source=tts_source,
            )

            # There is some recursion below to deal with the SubHeading tree structure. However,
            # it is not expected that the recursion level will get very high

            def copy_sections():
                for section in Section.objects.filter(nomenclature_tree=existing_tree):
                    logger.info("Copying %s", section)
                    from_section_id = section.pk
                    section.nomenclature_tree = new_tree
                    section.pk = None
                    section.save()
                    to_section_id = section.id
                    copy_chapters(from_section_id, to_section_id)

            def copy_chapters(from_section_id, to_section_id):
                for chapter in Chapter.objects.filter(section_id=from_section_id):
                    logger.info("Copying %s", chapter)
                    from_chapter_id = chapter.pk
                    chapter.nomenclature_tree = new_tree
                    chapter.section_id = to_section_id
                    chapter.pk = None
                    chapter.save()
                    to_chapter_id = chapter.id
                    copy_headings(from_chapter_id, to_chapter_id)

            def copy_headings(from_chapter_id, to_chapter_id):
                for heading in Heading.objects.filter(chapter_id=from_chapter_id):
                    logger.info("Copying %s", heading)
                    from_heading_id = heading.pk
                    heading.nomenclature_tree = new_tree
                    heading.chapter_id = to_chapter_id
                    heading.pk = None
                    heading.save()
                    to_heading_id = heading.pk
                    copy_subheadings_of_heading(from_heading_id, to_heading_id)
                    copy_commodities_of_heading(from_heading_id, to_heading_id)

            def copy_subheadings_of_heading(from_heading_id, to_heading_id):
                for subheading in SubHeading.objects.filter(heading_id=from_heading_id):
                    logger.debug("Copying %s", subheading)
                    if subheading.parent_subheading is not None:
                        raise Exception(
                            "Unexpected tree structure: subheading with heading should not have a parent_subheading"
                        )
                    from_subheading_id = subheading.pk
                    subheading.nomenclature_tree = new_tree
                    subheading.heading_id = to_heading_id
                    subheading.pk = None
                    subheading.save()
                    to_subheading_id = subheading.pk
                    copy_subheadings_of_subheading(from_subheading_id, to_subheading_id)
                    copy_commodities_of_subheading(from_subheading_id, to_subheading_id)

            def copy_subheadings_of_subheading(from_subheading_id, to_subheading_id):
                for subheading in SubHeading.objects.filter(
                    parent_subheading_id=from_subheading_id
                ):
                    logger.debug("Copying %s", subheading)
                    if subheading.heading is not None:
                        raise Exception(
                            "Unexpected tree structure: subheading with parent_subheading should not have a heading"
                        )
                    from_nested_subheading_id = subheading.pk
                    subheading.nomenclature_tree = new_tree
                    subheading.parent_subheading_id = to_subheading_id
                    subheading.pk = None
                    subheading.save()
                    to_nested_subheading_id = subheading.pk
                    copy_subheadings_of_subheading(
                        from_nested_subheading_id, to_nested_subheading_id
                    )
                    copy_commodities_of_subheading(
                        from_nested_subheading_id, to_nested_subheading_id
                    )

            def copy_commodities_of_heading(from_heading_id, to_heading_id):
                for commodity in Commodity.objects.filter(heading_id=from_heading_id):
                    logger.debug("Copying %s", commodity)
                    if commodity.parent_subheading is not None:
                        raise Exception(
                            "Unexpected tree structure: commodity with heading should not have a parent_subheading"
                        )
                    commodity.nomenclature_tree = new_tree
                    commodity.heading_id = to_heading_id
                    commodity.pk = None
                    commodity.save()

            def copy_commodities_of_subheading(from_subheading_id, to_subheading_id):
                for commodity in Commodity.objects.filter(
                    parent_subheading_id=from_subheading_id
                ):
                    logger.debug("Copying %s", commodity)
                    if commodity.heading is not None:
                        raise Exception(
                            "Unexpected tree structure: commodity with parent_subheading should not have a heading"
                        )
                    commodity.nomenclature_tree = new_tree
                    commodity.parent_subheading_id = to_subheading_id
                    commodity.pk = None
                    commodity.save()

            copy_sections()
