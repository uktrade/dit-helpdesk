from django.conf import settings


def ga_gtm_processor(request):
    return {"HELPDESK_GA_GTM": settings.HELPDESK_GA_GTM}


def feature_flag_processor(request):
    return {
        "ugkt_enabled": settings.UKGT_ENABLED
    }
