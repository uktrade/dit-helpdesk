from django.conf import settings
from django.http import HttpResponse
from django.urls import resolve


from .ip_filter import is_valid_admin_ip, get_client_ip


def AdminIpRestrictionMiddleware(get_response):
    """
    Middleware to check if a client IP address has authority to view the admin or not, returning an HTTP 401 error
    response if not.
    :param get_response: django http request
    :return: django http response
    """

    def middleware(request):
        if resolve(request.path).app_name == 'admin':
            if settings.RESTRICT_ADMIN:
                client_ip = get_client_ip(request)
                if not is_valid_admin_ip(client_ip):
                    return HttpResponse('Unauthorized', status=401)

        return get_response(request)

    return middleware
