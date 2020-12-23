import requests

from requests.auth import HTTPBasicAuth

from enum import Enum

from django.conf import settings


def get_auth(config):
    try:
        config = config["AUTH"]
    except KeyError:
        return None

    auth_type = config["type"]
    if auth_type == "basic":
        return HTTPBasicAuth(
            config["username"],
            config["password"],
        )

    raise ValueError(f"Unknown auth type {auth_type}")


class JSONObjClient:
    class CommodityType(Enum):
        CHAPTER = "CHAPTER"
        HEADING = "HEADING"
        COMMODITY = "COMMODITY"

    class NotFound(Exception):
        pass

    TIMEOUT = 10

    def __init__(self, base_url, auth=None):
        self.base_url = base_url
        self.auth = auth

    def get_content(self, commodity_type, commodity_code):
        path = {
            self.CommodityType.CHAPTER: "chapters",
            self.CommodityType.HEADING: "headings",
            self.CommodityType.COMMODITY: "commodities",
        }[commodity_type]
        url = f"{self.base_url}{path}/{commodity_code}"

        response = requests.get(url, auth=self.auth, timeout=self.TIMEOUT)

        if response.status_code != 200:
            raise self.NotFound()

        return response.content.decode()


def get_json_obj_client(region):
    config = settings.TRADE_TARIFF_CONFIG[region]["JSON_OBJ"]

    base_url = config["BASE_URL"]
    auth = get_auth(config)

    return JSONObjClient(base_url, auth=auth)


class HierarchyClient:
    class CommodityType(Enum):
        SECTION = "SECTION"
        CHAPTER = "CHAPTER"
        HEADING = "HEADING"
        COMMODITY = "COMMODITY"

    class NotFound(Exception):
        pass

    def __init__(self, base_url, auth=None):
        self.base_url = base_url
        self.auth = auth

    def _get_type_data_url(self, commodity_type):
        url_mapping = {
            self.CommodityType.SECTION: "sections",
            self.CommodityType.CHAPTER: "chapters",
        }
        url = f"{self.base_url}{url_mapping[commodity_type]}"

        return url

    def _make_request(self, url):
        response = requests.get(url, auth=self.auth)
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
    auth = get_auth(config)

    return HierarchyClient(base_url, auth=auth)
