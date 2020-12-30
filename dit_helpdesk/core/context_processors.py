from django.conf import settings

from flags.state import flag_enabled

from .helpers import _is_importer_journey


def ga_gtm_processor(request):
    return {"HELPDESK_GA_GTM": settings.HELPDESK_GA_GTM}


def feature_flag_processor(request):

    pre21_enabled = flag_enabled("PRE21")

    return {
        "ukgt_enabled": pre21_enabled,
        "japan_fta_enabled": flag_enabled("JAPAN_FTA"),
        "ni_journey_enabled": flag_enabled("NI_JOURNEY"),
        "old_roo_enabled": pre21_enabled,
        "importer_journey_enabled": _is_importer_journey(request),
        "eu_fallback_enabled": flag_enabled("EU_FALLBACK"),
        "eu_tariff_enabled": not pre21_enabled,
    }
