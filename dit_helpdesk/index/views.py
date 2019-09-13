from django.conf import settings
from django.views.generic.base import RedirectView


class IndexRedirect(RedirectView):
    """
    Placeholder class based generic view redirecting to the DNS entry for the application

    """
    url = "https://{0}/".format(settings.APP_START_DOMAIN)
