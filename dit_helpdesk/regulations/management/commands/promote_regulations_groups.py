from django.core.management.base import BaseCommand

from hierarchy.models import Section
from regulations.hierarchy import promote_regulation_groups


class Command(BaseCommand):
    help = (
        """Command to promote and dedupe regulations"""
    )

    def handle(self, *args, **options):
        self.stdout.write("Promoting and de-duping regulations")
        for section in Section.objects.all():
            self.stdout.write(f"Promoting and de-duping for {section}")
            promote_regulation_groups(section)
