import pprint
import requests
from requests_aws4auth import AWS4Auth

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


COMMODITY_MAPPING = {
    "chapter": "chapters",
    "heading": "headings",
    "commodity": "commodities",
}


COMMODITY_TYPES = COMMODITY_MAPPING.keys()


class Command(BaseCommand):
    help = "Displays commodity details taken from the alt trade tariff service"

    def add_arguments(self, parser):
        parser.add_argument("commodity_type", type=str, choices=COMMODITY_TYPES)
        parser.add_argument("commodity_code", type=str)

    def _get_url(self, commodity_type, commodity_code):
        bucket_name = settings.AWS_ALT_TARIFF_BUCKET_NAME
        region = settings.AWS_REGION
        commodity_type = COMMODITY_MAPPING[commodity_type]

        return f"https://{bucket_name}.s3.{region}.amazonaws.com/uk/2021-01-01/{commodity_type}/{commodity_code}.json"

    def _get_auth(self):
        return AWS4Auth(
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY,
            settings.AWS_REGION,
            's3',
        )

    def _request_details(self, url):
        auth = self._get_auth()
        response = requests.get(url, auth=auth)

        if response.status_code != requests.codes.ok:
            raise CommandError("Invalid commodity - not found")

        return response.json()

    def handle(self, *args, **options):
        commodity_type = options["commodity_type"]
        commodity_code = options["commodity_code"]

        url = self._get_url(commodity_type, commodity_code)
        details = self._request_details(url)

        pp = pprint.PrettyPrinter(indent=4)
        self.stdout.write(pp.pformat(details))
