from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView

from regulations.models import RegulationGroup


class BaseCMSMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CMSView(BaseCMSMixin, View):

    def get(self, request):
        return HttpResponse("OK")


class RegulationGroupsListView(BaseCMSMixin, ListView):
    queryset = RegulationGroup.objects.all()[:10]
    template_name = "cms/regulations/regulationgroup_list.html"
