from django.conf import settings
from django.views.generic.base import RedirectView


class IndexRedirect(RedirectView):
    """
    Placeholder class based generic view redirecting to the DNS entry for the application and the start page
    requires setting the ENV variable bellow in the vault
    """

    url = settings.APP_START_DOMAIN
