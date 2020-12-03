import requests

from requests_aws4auth import AWS4Auth

from django.conf import settings

from hierarchy.tts_api import BaseTTSClient


COMMODITY_MAPPING = {
    BaseTTSClient.CommodityType.CHAPTER: "chapters",
    BaseTTSClient.CommodityType.HEADING: "headings",
    BaseTTSClient.CommodityType.COMMODITY: "commodities",
}


class Client(BaseTTSClient):
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

    def get_content(self, commodity_type, commodity_code):
        url = self._get_url(commodity_type, commodity_code)

        response = requests.get(
            url,
            auth=self._get_auth(),
            timeout=self.TIMEOUT,
        )

        if response.status_code != 200:
            raise self.NotFound()

        return response.content.decode()
