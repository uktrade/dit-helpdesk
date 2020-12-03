from django.conf import settings

from .helpers import _is_importer_journey


def ga_gtm_processor(request):
    return {"HELPDESK_GA_GTM": settings.HELPDESK_GA_GTM}


def feature_flag_processor(request):

    return {
        "ukgt_enabled": settings.UKGT_ENABLED,
        "japan_fta_enabled": settings.JAPAN_FTA_ENABLED,
        "ni_journey_enabled": settings.NI_JOURNEY_ENABLED,
        "grouped_search_enabled": settings.GROUPED_SEARCH_ENABLED,
        "importer_journey_enabled": _is_importer_journey(request),
    }
