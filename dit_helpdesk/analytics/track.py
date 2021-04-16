import logging
import requests
import uuid

from django.conf import settings


logger = logging.getLogger(__name__)


# For an overview of all of the available parameters available to be sent to GA:
# https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters


API_VERSION = "1"

# Use "https://www.google-analytics.com/debug/collect" for testing.
GOOGLE_ANALYTICS_ENDPOINT = "https://www.google-analytics.com/collect"


def build_tracking_data(request, additional_data):
    data = {
        "v": API_VERSION,  # API Version.
        "tid": settings.HELPDESK_GA_UA,  # Tracking aID / Property ID.
        "cid": str(uuid.uuid4()),  # This needs to be cid not uid or your events won't register in the behaviour section

        "uip": request.META.get("REMOTE_ADDR"),  # User ip override
        "aip": "1",  # Anonymise user ip
        "ua": request.META.get("HTTP_USER_AGENT"),  # User agent override
        "dr": request.META.get("HTTP_REFERER"),  # Document referrer
        "dl": request.build_absolute_uri(),  # Document location URL

        **additional_data,
    }

    return data


def send_tracking_data(tracking_data):
    if not settings.TRACK_GA_EVENTS:
        return

    response = requests.post(
        GOOGLE_ANALYTICS_ENDPOINT,
        params=tracking_data,
    )

    return response


def track_event(request, category, action, label=None, value=None):
    event_data = {
        "t": "event",
        "ec": category,
        "ea": action,
    }
    if label:
        event_data["el"] = label

    if value:
        event_data["ev"] = value

    data = build_tracking_data(request, event_data)

    return send_tracking_data(data)


def track_page_view(request):
    page_view_data = {
        "t": "pageview",
    }

    data = build_tracking_data(request, page_view_data)

    return send_tracking_data(data)
