import time
import datetime as dt
import requests

from django.views.generic import View, TemplateView
from django.http import HttpResponse
from django.conf import settings

from sentry_sdk import capture_exception

from healthcheck.models import HealthCheck
from healthcheck.tree_refresh import check_tree_freshness

from django_elasticsearch_dsl.search import Search
from elasticsearch import Elasticsearch


class HealthCheckView(TemplateView):
    template_name = "healthcheck.html"

    def _do_check(self):
        """
        Performs a basic check on the database by performing a select query on a simple table then
        performs a basic check on ElasticSearch by performing a search without exceptions occuring
        :return: False according to results of check, True if successful False if there is a fail
        """
        try:
            # Perform database check
            HealthCheck.objects.get(health_check_field=True)

            # Perform Elaseticsearch check
            client = Elasticsearch(hosts=[settings.ES_URL])
            query_object = {
                "multi_match": {
                    "query": "a_commodity_or_code",
                    "type": "most_fields",
                    "fields": ["keywords", "description"],
                    "operator": "and" if "," not in "a_commodity_or_code" else "or",
                }
            }
            Search().index("indexes").using(client).query(query_object).sort(
                "sort_object"
            )

            # Return success if we have reached this point
            return True

        except Exception as e:
            capture_exception(e)
            return False

    def get_context_data(self, **kwargs):
        """Adds status and response time to response context"""
        context = super().get_context_data(**kwargs)
        context["status"] = "OK" if self._do_check() is True else "FAIL"
        # nearest approximation of a response time
        context["response_time"] = time.time() - self.request.start_time
        return context


class BaseCheckView(View):
    CHECK_SUCCEEDED_STATUS = 200
    CHECK_FAILED_STATUS = 503

    def check(self):
        raise NotImplementedError("Implement `check`")

    def get(self, request, *args, **kwargs):
        is_check_successful = self.check(request)

        if is_check_successful:
            resp = HttpResponse("OK", status=self.CHECK_SUCCEEDED_STATUS)
        else:
            resp = HttpResponse("Failed", status=self.CHECK_FAILED_STATUS)

        return resp


class TreeRefreshCheckView(BaseCheckView):
    MAX_DELTA = dt.timedelta(days=7, hours=2)

    def check(self, request):
        return check_tree_freshness(self.MAX_DELTA)


class CMSCheckView(BaseCheckView):
    def check(self, request):
        url = request.build_absolute_uri("/cms/")
        response = requests.get(url, allow_redirects=False)

        return response.status_code == 404
