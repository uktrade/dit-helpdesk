import requests

from enum import Enum

from django.conf import settings


class HierarchyClient:
    class CommodityType(Enum):
        SECTION = "SECTION"
        CHAPTER = "CHAPTER"
        HEADING = "HEADING"
        COMMODITY = "COMMODITY"

    class NotFound(Exception):
        pass

    def __init__(self, base_url):
        self.base_url = base_url

    def _get_type_data_url(self, commodity_type):
        url_mapping = {
            self.CommodityType.SECTION: "sections",
            self.CommodityType.CHAPTER: "chapters",
        }
        url = f"{self.base_url}{url_mapping[commodity_type]}"

        return url

    def _make_request(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            raise self.NotFound(url)

        return response

    def get_type_data(self, commodity_type):
        url = self._get_type_data_url(commodity_type)
        response = self._make_request(url)

        return response.json()

    def _get_item_data_url(self, commodity_type, item_id):
        url_mapping = {
            self.CommodityType.SECTION: "sections",
            self.CommodityType.CHAPTER: "chapters",
            self.CommodityType.HEADING: "headings",
        }
        item_path = f"{url_mapping[commodity_type]}/{item_id}"
        url = f"{self.base_url}{item_path}"

        return url

    def get_item_data(self, commodity_type, item_id):
        url = self._get_item_data_url(commodity_type, item_id)
        response = self._make_request(url)

        return response.json()


def get_hierarchy_client(region):
    config = settings.TRADE_TARIFF_CONFIG[region]["TREE"]
    base_url = config["BASE_URL"]

    return HierarchyClient(base_url)
