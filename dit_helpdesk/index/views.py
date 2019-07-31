from django.views.generic.base import RedirectView


class IndexRedirect(RedirectView):
    """
    Placeholder class based generic view redirecting to the DNS entry for the application

    """
    url = 'http://www.get-rules-tariffs-trade-with-uk.service.gov.uk/'
