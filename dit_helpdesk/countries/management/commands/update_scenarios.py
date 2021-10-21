from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import Country
from ...scenarios import update_scenario


class Command(BaseCommand):
    help = "Updates the trade scenarios based on external data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            help="Outputs country changes without updating data",
            action="store_true",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        scenarios_map = []
        with transaction.atomic():
            for country in Country.objects.all():
                previous_scenario = country.scenario
                update_scenario(country)
                country.refresh_from_db()
                updated_scenario = country.scenario

                if previous_scenario != updated_scenario:
                    scenarios_map.append(
                        (country.country_code, previous_scenario, updated_scenario)
                    )

            if dry_run:
                transaction.set_rollback(True)

        if dry_run:
            self.stdout.write("Would update:")
        else:
            self.stdout.write("Updated:")

        for country_code, previous_scenario, updated_scenario in scenarios_map:
            self.stdout.write(
                f"{country_code}: {previous_scenario} -> {updated_scenario}"
            )
