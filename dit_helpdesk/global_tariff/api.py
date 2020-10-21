import requests

from typing import Dict, List, Tuple

from hierarchy.helpers import permute_code_hierarchy

ROOT_URL = "https://www.check-future-uk-trade-tariffs.service.gov.uk/api/global-uk-tariff"

CommodityCodeType = str
GlobalTariffCommodityResponseType = Dict[str, any]


def get_commodity_code_data(code: CommodityCodeType) -> List[GlobalTariffCommodityResponseType]:
    """Gets results from the Global Tariff API for a commodity code.
    """
    return requests.get(f"{ROOT_URL}?q={code}").json()


class NoResultError(Exception):
    """Raised when there are no results for a commodity from the Global Tariff API.
    """
    pass


class MultipleResultsError(Exception):
    """Raised when there are multiple results for a commodity from the Global Tariff API.
    """
    pass


def get_commodity_data(code: CommodityCodeType) -> Tuple[CommodityCodeType, GlobalTariffCommodityResponseType]:
    """Gets results for the commodity code either of the commodity directly or by
    searching up through the commodity code hierarchy until it finds a result.

    :raises NoResultError: When there are no results after traversing up the commodity code hierarchy.
    :raises MultipleResultsError: When it finds more than one result for a commodity code.
    """
    for code in permute_code_hierarchy(code):
        response = get_commodity_code_data(code)

        num_results = len(response)
        if num_results > 1:
            raise MultipleResultsError(f"Found {num_results} expected 1.")

        if response:
            return code, response[0]

    raise NoResultError()
