import json
import pprint

from django.core.management.base import BaseCommand, CommandError

from hierarchy.tts_api import BaseTTSClient

from ...tts_api import Client


COMMODITY_MAPPING = {
    "chapter": BaseTTSClient.CommodityType.CHAPTER,
    "heading": BaseTTSClient.CommodityType.HEADING,
    "commodity": BaseTTSClient.CommodityType.COMMODITY,
}

COMMODITY_TYPES = COMMODITY_MAPPING.keys()


class Command(BaseCommand):
    help = "Displays commodity details taken from the alt trade tariff service"

    def add_arguments(self, parser):
        parser.add_argument("commodity_type", type=str, choices=COMMODITY_TYPES)
        parser.add_argument("commodity_code", type=str)

    def _request_details(self, commodity_type, commodity_code):
        client = Client()

        try:
            response = client.get_content(commodity_type, commodity_code)
        except client.NotFound:
            raise CommandError("Invalid commodity - not found")

        return json.loads(response)

    def handle(self, *args, **options):
        commodity_type = COMMODITY_MAPPING[options["commodity_type"]]
        commodity_code = options["commodity_code"]

        details = self._request_details(commodity_type, commodity_code)

        pp = pprint.PrettyPrinter(indent=4)
        self.stdout.write(pp.pformat(details))
