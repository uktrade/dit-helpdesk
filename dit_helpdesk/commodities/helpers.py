from django.conf import settings


def get_tariff_content_context(country):
    if country.scenario in settings.SUPPORTED_TRADE_SCENARIOS:
        tariff_content_label = f"_content_{country.scenario.replace('-', '_')}"
    else:
        tariff_content_label = ''

    country_suffix = '' if country.name.endswith('s') else 's'

    context = {
        "tariff_content_label": tariff_content_label,
        "tariff_content_url": country.content_url,
        "country_name": country.name,
        "country_suffix": country_suffix,
    }

    return context
