import csv

from contextlib import contextmanager

from django.core.management.base import BaseCommand

from countries.models import Country


class Command(BaseCommand):
    help = "Outputs a CSV of countries and scenarios"

    def add_arguments(self, parser):
        parser.add_argument(
            "-o", "--output", help="Specifies file to which the output is written."
        )

    def get_fieldnames(self):
        return [
            "country_code",
            "country_name",
            "uk_agreement_status",
            "eu_agreement_status",
            "scenario",
            "govuk_fta_url",
            "trade_agreement_title",
            "trade_agreement_type",
        ]

    @contextmanager
    def get_writer(self, output):
        fieldnames = self.get_fieldnames()

        def _writer(out):
            return csv.DictWriter(out, fieldnames=fieldnames)

        if output:
            with open(output, "w") as csv_file:
                yield _writer(csv_file)
        else:
            yield _writer(self.stdout)

    def handle(self, *args, **options):
        with self.get_writer(options["output"]) as writer:
            writer.writeheader()

            for country in Country.objects.order_by("country_code"):
                writer.writerow(
                    {
                        "country_code": country.country_code,
                        "country_name": country.name,
                        "uk_agreement_status": country.has_uk_trade_agreement,
                        "eu_agreement_status": country.has_eu_trade_agreement,
                        "scenario": country.scenario,
                        "govuk_fta_url": country.content_url,
                        "trade_agreement_title": country.trade_agreement_title,
                        "trade_agreement_type": country.trade_agreement_type,
                    }
                )
