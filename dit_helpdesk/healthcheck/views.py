import time
import datetime as dt

from django.views.generic import View, TemplateView
from django.http import HttpResponse

from sentry_sdk import capture_exception

from healthcheck.models import HealthCheck
from healthcheck.tree_refresh import check_tree_freshness


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

        except Exception as e:
            capture_exception(e)
            return False

    def get_context_data(self, **kwargs):
        """ Adds status and response time to response context"""
        context = super().get_context_data(**kwargs)
        context["status"] = "OK" if self._do_check() is True else "FAIL"
        # nearest approximation of a response time
        context["response_time"] = time.time() - self.request.start_time
        return context


class TreeRefreshCheckView(View):

    MAX_DELTA = dt.timedelta(days=7, hours=2)

    CHECK_SUCCEEDED_STATUS = 200
    CHECK_FAILED_STATUS = 503

    def get(self, *args, **kwargs):
        is_fresh = check_tree_freshness(self.MAX_DELTA)

        if is_fresh:
            resp = HttpResponse('OK', status=self.CHECK_SUCCEEDED_STATUS)
        else:
            resp = HttpResponse('Failed', status=self.CHECK_FAILED_STATUS)

        return resp
