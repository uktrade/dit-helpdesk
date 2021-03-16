import logging
import requests
import uuid

from django.conf import settings


logger = logging.getLogger(__name__)


# For an overview of all of the available parameters available to be sent to GA:
# https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters


API_VERSION = "1"

# Use "http://www.google-analytics.com/debug/collect" for testing.
GOOGLE_ANALYTICS_ENDPOINT = "http://www.google-analytics.com/collect"


def track_event(request, category, action, label=None, value=None):
    data = {
        "v": API_VERSION,  # API Version.
        "tid": settings.HELPDESK_GA_UA,  # Tracking aID / Property ID.
        "uid": str(uuid.uuid4()),

        "uip": request.META.get("REMOTE_ADDR"),  # User ip override
        "aip": "1",  # Anonymise user ip
        "ua": request.META.get("HTTP_USER_AGENT"),  # User agent override
        "dr": request.META.get("HTTP_REFERER"),  # Document referrer
        "dl": request.build_absolute_uri(),  # Document location URL

        "t": "event",  # Event hit type.
        "ec": category,  # Event category.
        "ea": action,  # Event action.
    }

    if label:
        data["el"] = label

    if value:
        data["ev"] = value

    if not settings.TRACK_GA_EVENTS:
        return

    return requests.post(
        GOOGLE_ANALYTICS_ENDPOINT,
        data=data,
    )
