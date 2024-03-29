import logging
import requests

from requests.auth import HTTPBasicAuth

from enum import Enum

from django.conf import settings


logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


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


def get_params(config):
    return config.get("PARAMS", {})


class JSONObjClient:
    class CommodityType(Enum):
        CHAPTER = "CHAPTER"
        HEADING = "HEADING"
        COMMODITY = "COMMODITY"

    class NotFound(Exception):
        pass

    class ServerError(Exception):
        pass

    class UnknownError(Exception):
        pass

    TIMEOUT = 10

    def __init__(self, base_url, auth=None, params=None):
        self.base_url = base_url
        self.auth = auth
        self.params = params

    def __repr__(self):
        return f"<JSONObjClient {self.base_url}>"

    def get_content(self, commodity_type, commodity_code):
        path = {
            self.CommodityType.CHAPTER: "chapters",
            self.CommodityType.HEADING: "headings",
            self.CommodityType.COMMODITY: "commodities",
        }[commodity_type]
        url = f"{self.base_url}{path}/{commodity_code}"

        logger.debug(url)
        response = requests.get(
            url,
            auth=self.auth,
            timeout=self.TIMEOUT,
            params=self.params,
        )
        status_code = response.status_code
        if status_code != 200:
            if 500 > status_code >= 400:
                raise self.NotFound(f"Not found {url} ({status_code})")

            if status_code >= 500:
                raise self.ServerError(f"Server error {url} ({status_code})")

            raise self.UnknownError(f"Unknown {url} ({status_code})")

        return response.content.decode()


def get_settings_config():
    config = settings.TRADE_TARIFF_CONFIG
    if callable(config):
        config = config()

    return config


def get_json_obj_client(region):
    settings_config = get_settings_config()
    config = settings_config[region]["JSON_OBJ"]

    base_url = config["BASE_URL"]
    auth = get_auth(config)
    params = get_params(config)

    return JSONObjClient(base_url, auth=auth, params=params)


class HierarchyClient:
    class CommodityType(Enum):
        SECTION = "SECTION"
        CHAPTER = "CHAPTER"
        HEADING = "HEADING"
        COMMODITY = "COMMODITY"

    class NotFound(Exception):
        pass

    class ServerError(Exception):
        pass

    class UnknownError(Exception):
        pass

    def __init__(self, base_url, auth=None, params=None):
        self.base_url = base_url
        self.auth = auth
        self.params = params

    def __repr__(self):
        return f"<HierarchyClient {self.base_url}>"

    def _get_type_data_url(self, commodity_type):
        url_mapping = {
            self.CommodityType.SECTION: "sections",
            self.CommodityType.CHAPTER: "chapters",
        }
        url = f"{self.base_url}{url_mapping[commodity_type]}"

        return url

    def _make_request(self, url):
        logger.debug(url)
        response = requests.get(
            url,
            auth=self.auth,
            params=self.params,
        )
        status_code = response.status_code
        if status_code != 200:
            if 500 > status_code >= 400:
                raise self.NotFound(f"Not found {url} ({status_code})")

            if status_code >= 500:
                raise self.ServerError(f"Server error {url} ({status_code})")

            raise self.UnknownError(f"Unknown {url} ({status_code})")

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
    settings_config = get_settings_config()
    config = settings_config[region]["TREE"]

    base_url = config["BASE_URL"]
    auth = get_auth(config)
    params = get_params(config)

    return HierarchyClient(base_url, auth=auth, params=params)
