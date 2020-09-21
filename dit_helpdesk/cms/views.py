from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View


class BaseCMSMixin:

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CMSView(BaseCMSMixin, View):

    def get(self, request):
        return HttpResponse("OK")
