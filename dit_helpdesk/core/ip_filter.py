from ipaddress import ip_network, ip_address
import logging

from django.conf import settings

logger = logging.getLogger(__file__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.ERROR)


def is_valid_admin_ip(client_ip):
    """
    Middleware helper function to filter out client IPs that are not allowed access to the django admin system
    :param client_ip: string
    :return: boolean
    """

    if not client_ip:
        return False

    if client_ip in settings.ALLOWED_ADMIN_IPS:
        return True

    ip_addr = ip_address(client_ip)
    for cidr in settings.ALLOWED_ADMIN_IP_RANGES:
        if ip_addr in ip_network(cidr):
            return True

    return False


def get_client_ip(request):
    """
    Middleware helper function to extract the IP from the client request object, throws and exception if the
    X-Forwarded-For header is not present or does not contain enough information to determine the IP
    :param request: django http request
    :return: string or None
    """

    try:
        return request.META['HTTP_X_FORWARDED_FOR'].split(',')[settings.IP_SAFELIST_XFF_INDEX].strip()
    except (IndexError, KeyError):
        logger.warning(
            'X-Forwarded-For header is missing or does not '
            'contain enough elements to determine the '
            'client\'s ip')
        return None
