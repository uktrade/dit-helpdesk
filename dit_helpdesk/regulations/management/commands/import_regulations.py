from django.conf import settings
from django.core.management.base import BaseCommand

from hierarchy.models import Section
from hierarchy.helpers import process_swapped_tree

from regulations.hierarchy import promote_regulations
from regulations.importer import RegulationsImporter


class Command(BaseCommand):
    help = (
        """Command to import links to documents and regulations related to commodties"""
    )

    def handle(self, *args, **options):
        data_path = settings.REGULATIONS_DATA_PATH

        with process_swapped_tree():
            self.stdout.write("Importing regulations")
            importer = RegulationsImporter()
            importer.load(data_path)
            importer.process()

            self.stdout.write("Promoting and de-duping regulations")
            for section in Section.objects.all():
                self.stdout.write(f"Promoting and de-duping for {section}")
                promote_regulations(section)
