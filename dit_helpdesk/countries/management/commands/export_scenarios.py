import csv

from contextlib import contextmanager

from django.core.management.base import BaseCommand

from countries.models import Country


class Command(BaseCommand):
    help = "Outputs a CSV of countries and scenarios"

    def add_arguments(self, parser):
        parser.add_argument(
            '-o', '--output',
            help='Specifies file to which the output is written.'
        )

    def get_fieldnames(self):
        return [
            "Country code",
            "Country name",
            "Scenario",
        ]

    @contextmanager
    def get_writer(self, output):
        fieldnames = self.get_fieldnames()

        def _writer(out):
            return csv.DictWriter(out, fieldnames=fieldnames)

        if output:
            with open(output, 'w') as csv_file:
                yield _writer(csv_file)
        else:
            yield _writer(self.stdout)

    def handle(self, *args, **options):
        with self.get_writer(options["output"]) as writer:
            writer.writeheader()

            for country in Country.objects.order_by("country_code"):
                writer.writerow({
                    "Country code": country.country_code,
                    "Country name": country.name,
                    "Scenario": country.scenario,
                })
