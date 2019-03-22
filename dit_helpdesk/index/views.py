from django.views.generic.base import RedirectView


class IndexRedirect(RedirectView):
  url = 'https://gov.uk/get-rules-tariffs-trade-with-uk/'
