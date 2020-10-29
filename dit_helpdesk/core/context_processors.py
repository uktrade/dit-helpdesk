from django.conf import settings


def ga_gtm_processor(request):
    return {"HELPDESK_GA_GTM": settings.HELPDESK_GA_GTM}


def feature_flag_processor(request):
    return {
        "ukgt_enabled": settings.UKGT_ENABLED,
        "fta_info_sharing_enabled": settings.FTA_INFO_SHARING_ENABLED,
        "ni_journey_enabled": settings.NI_JOURNEY_ENABLED,
    }
