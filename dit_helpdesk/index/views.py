from django.views.generic.base import RedirectView


class IndexRedirect(RedirectView):
    """
    Placeholder class based generic view redirecting to the DNS entry for the application

    """
    url = 'https://gov.uk/get-rules-tariffs-trade-with-uk/'
