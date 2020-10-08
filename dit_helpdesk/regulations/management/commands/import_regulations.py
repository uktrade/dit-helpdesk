from django.conf import settings
from django.db import transaction
from django.core.management.base import BaseCommand

from hierarchy.models import Section
from hierarchy.helpers import process_swapped_tree

from regulations.hierarchy import promote_regulation_groups
from regulations.importer import RegulationsImporter


class Command(BaseCommand):
    help = (
        """Command to import links to documents and regulations related to commodties"""
    )

    def import_regulations(self, region, data_path):
        self.stdout.write("Importing regulations")
        importer = RegulationsImporter(region=region)
        importer.load(data_path)
        importer.process()

        self.stdout.write("Promoting and de-duping regulations")
        for section in Section.objects.all():
            self.stdout.write(f"Promoting and de-duping for {section}")
            promote_regulation_groups(section)

    def handle(self, *args, **options):
        data_path = settings.REGULATIONS_DATA_PATH

        with transaction.atomic():
            with process_swapped_tree():
                # using `process_swapped_tree` on the default region, as that tree is updated
                # in the background - this tree should remain inactive until it's fully populated
                self.import_regulations('EU', data_path)

            # we don't care about this tree being partially updated for a few minutes for now
            self.import_regulations('UK', data_path)
