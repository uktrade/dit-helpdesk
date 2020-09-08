import csv

from django.core.management.base import BaseCommand, CommandError

from ...models import Country


class Command(BaseCommand):
    help = 'Compares the country data with gov register data file'

    def add_arguments(self, parser):
        parser.add_argument(
            'register_country_file',
            type=str,
            help='Path for register country file',
        )

    def handle(self, *args, **options):
        current_countries = dict(
            Country.objects.values_list('country_code', 'name'),
        )

        register_countries = {}
        with open(options['register_country_file']) as register_country_file:
            reader = csv.DictReader(register_country_file)

            for row in reader:
                register_countries[row['key']] = row['name']

        added = set(register_countries.keys()) - set(current_countries.keys())
        removed = set(current_countries.keys()) - set(register_countries.keys())
        potentially_updated = set(register_countries.keys()) & set(current_countries.keys())

        updated = []
        for country_code in potentially_updated:
            if current_countries[country_code] != register_countries[country_code]:
                updated.append(country_code)

        indent = " " * 4

        self.stdout.write(f"Added: {len(added)}")
        for a in sorted(added):
            self.stdout.write(f"{indent}{a} {register_countries[a]}")

        self.stdout.write(f"Removed: {len(removed)}")
        for r in sorted(removed):
            self.stdout.write(f"{indent}{r} {current_countries[r]}")

        self.stdout.write(f"Updated: {len(updated)}")
        for u in sorted(updated):
            self.stdout.write(f"{indent}{u} {current_countries[u]} -> {register_countries[u]}")
