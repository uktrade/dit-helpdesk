import re

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import resolve

from .ip_filter import is_valid_admin_ip, get_client_ip


def NoIndexMiddleware(get_response):
    def middleware(request):
        response = get_response(request)

        response["X-Robots-Tag"] = "noindex, nofollow"

        return response

    return middleware


def AdminIpRestrictionMiddleware(get_response):
    """
    Middleware to check if a client IP address has authority to view the admin or not, returning an HTTP 401 error
    response if not.
    :param get_response: django http request
    :return: django http response
    """

    def middleware(request):
        if resolve(request.path).app_name == "admin":
            if settings.RESTRICT_ADMIN:
                client_ip = get_client_ip(request)
                if not is_valid_admin_ip(client_ip):
                    return HttpResponse("Unauthorized", status=401)

        return get_response(request)

    return middleware


def CheckCountryUrlMiddleware(get_response):
    def middleware(request):
        response = get_response(request)

        request_path = request.path
        pattern = r"\/country\/([a-z]{2})"
        matches = re.search(pattern, request_path)
        subst = "/country/eu"

        if matches and matches.group(1).upper() in settings.EU_COUNTRY_CODES:
            if (
                "origin_country" not in request.session
                or request.session["origin_country"] != "EU"
            ):
                request.session["origin_country"] = "EU"
            return HttpResponseRedirect(re.sub(pattern, subst, request_path, 1))

        return response

    return middleware
