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


def track_event(category, action, label=None, value=None):
    data = {
        "v": API_VERSION,  # API Version.
        "tid": settings.HELPDESK_GA_UA,  # Tracking aID / Property ID.
        "cid": str(uuid.uuid4()),
        "t": "event",  # Event hit type.
        "ec": category,  # Event category.
        "ea": action,  # Event action.
    }

    if label:
        data["el"] = label

    if value:
        data["ev"] = value

    logger.info("Sending analytics event %s", data)

    return requests.post(
        GOOGLE_ANALYTICS_ENDPOINT,
        params=data,
        # if a custom user agent isn't set then we get no events coming through
        # on GA as it seems to filter out those sent by requests (requests sets
        # its own user agent if you don't specify one)
        headers={"User-Agent": "TWUK analytics"},
    )
