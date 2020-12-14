from enum import auto, Enum

from django.conf import settings

from global_tariff.api import (
    get_commodity_data as get_global_tariff_commodity_data,
    MultipleResultsError as GlobalTariffMultipleResultsError,
    NoResultError as GlobalTariffNoResultError,
)
from hierarchy.helpers import permute_code_hierarchy


class GlobalTariffResult(Enum):
    HAS_RESULTS = auto()
    NO_RESULT = auto()
    MULTIPLE_RESULTS = auto()


def get_global_tariff_context(commodity):
    context = {
        "result_types": GlobalTariffResult.__members__,
    }
    try:
        context_result = get_global_tariff_commodity_data(permute_code_hierarchy(commodity))
        context.update({
            "result_type": GlobalTariffResult.HAS_RESULTS,
            "result": context_result,
        })
    except GlobalTariffMultipleResultsError:
        context.update({
            "result_type": GlobalTariffResult.MULTIPLE_RESULTS,
        })
    except GlobalTariffNoResultError:
        context.update({
            "result_type": GlobalTariffResult.NO_RESULT,
        })

    return context


def has_trade_scenario(country):
    return country.scenario in settings.SUPPORTED_TRADE_SCENARIOS


def get_tariff_content_context(country, commodity):
    if has_trade_scenario(country):
        tariff_content_label = f"_content_{country.scenario.replace('-', '_')}"
    else:
        tariff_content_label = ''

    country_suffix = '' if country.name.endswith('s') else 's'

    context = {
        "tariff_content_label": tariff_content_label,
        "tariff_content_url": country.content_url,
        "country_name": country.name,
        "country_suffix": country_suffix,
        "global_tariff_data": get_global_tariff_context(commodity),
    }

    return context
