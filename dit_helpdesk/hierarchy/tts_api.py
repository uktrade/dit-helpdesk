from enum import Enum


class BaseTTSClient:
    class CommodityType(Enum):
        CHAPTER = "CHAPTER"
        HEADING = "HEADING"
        COMMODITY = "COMMODITY"

    class NotFound(Exception):
        pass

    TIMEOUT = 10

    def get_content(self, commodity_type, commodity_code):
        raise NotImplementedError("Impement `get_content`")
