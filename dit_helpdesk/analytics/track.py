import logging
import requests
import uuid

from django.conf import settings


logger = logging.getLogger(__name__)


API_VERSION = "1"
GOOGLE_ANALYTICS_ENDPOINT = "http://www.google-analytics.com/collect"


def track_event(category, action, label=None, value=None):
    data = {
        "v": API_VERSION,  # API Version.
        "tid": settings.HELPDESK_GA_GTM,  # Tracking aID / Property ID.
        "cid": uuid.uuid4(),
        "t": "event",  # Event hit type.
        "ec": category,  # Event category.
        "ea": action,  # Event action.
    }

    if label:
        data["el"] = label

    if value:
        data["ev"] = value

    logger.info("Sending analytics event %s", data)

    requests.post(
        GOOGLE_ANALYTICS_ENDPOINT,
        data=data,
    )
