from django.conf import settings
from django.conf.urls import handler404
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.core.exceptions import PermissionDenied


def admin_login_view(request):
    """A replacement admin login view that will direct the user through the SSO
    authentication flow. """

    # print(settings.ADMIN_ENABLED)
    # if settings.ADMIN_ENABLED is False:
    #     return HttpResponse("", status=404)

    next_url = request.GET.get(
        'next',
        request.session.get('admin_next_url',
                            reverse('admin:index')))

    if request.user.is_authenticated:
        if not request.user.is_staff:
            raise PermissionDenied
        else:
            if 'admin_next_url' in request.session:
                del request.session['admin_next_url']

            return redirect(next_url)
    else:
        request.session['admin_next_url'] = next_url

        return redirect('authbroker:login')
