import time
from django.views.generic import TemplateView
from raven.contrib.django.raven_compat.models import client
from healthcheck.models import HealthCheck


class HealthCheckView(TemplateView):
    template_name = "healthcheck.html"

    def _do_check(self):
        """
        Performs a basic check on the database by performing a select query on a simple table
        :return: True or False according to successful retrieval
        """
        try:
            HealthCheck.objects.get(health_check_field=True)
            return True

        except Exception:
            client.captureException()
            return False

    def get_context_data(self, **kwargs):
        """ Adds status and response time to response context"""
        context = super().get_context_data(**kwargs)
        context["status"] = "OK" if self._do_check() is True else "FAIL"
        # nearest approximation of a response time
        context["response_time"] = time.time() - self.request.start_time
        return context
