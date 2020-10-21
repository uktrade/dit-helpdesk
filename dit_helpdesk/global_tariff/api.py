import re
import requests

from typing import Dict, List, Iterable, Tuple

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


def get_commodity_data(codes: Iterable[CommodityCodeType]) -> Tuple[CommodityCodeType, GlobalTariffCommodityResponseType]:
    """Gets results for the first commodity code in the sequence of commodity codes that has a single result.

    :raises NoResultError: When there are no results after traversing through the codes.
    :raises MultipleResultsError: When it finds more than one result for a code.
    """
    for code in codes:
        normalised_code = re.sub(r"(0{2})*$", "", code)
        normalised_code = normalised_code.ljust(8, "0")
        response = get_commodity_code_data(normalised_code)

        num_results = len(response)
        if num_results > 1:
            raise MultipleResultsError(f"Found {num_results} for {normalised_code} expected 1.")

        if response:
            return response[0]

    raise NoResultError()
