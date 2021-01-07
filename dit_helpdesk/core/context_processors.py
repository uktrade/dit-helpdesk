from django.conf import settings

from flags.state import flag_enabled


def ga_gtm_processor(request):
    return {"HELPDESK_GA_GTM": settings.HELPDESK_GA_GTM}


def feature_flag_processor(request):

    return {
        "eu_fallback_enabled": flag_enabled("EU_FALLBACK"),
    }
