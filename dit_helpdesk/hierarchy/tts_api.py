from enum import Enum


class NotFound(Exception):
    pass


class BaseTTSClient:
    class CommodityType(Enum):
        CHAPTER = "CHAPTER"
        HEADING = "HEADING"
        COMMODITY = "COMMODITY"

    NotFound = NotFound

    TIMEOUT = 10

    def get_content(self, commodity_type, commodity_code):
        raise NotImplementedError("Impement `get_content`")
