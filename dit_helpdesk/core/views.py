from django.shortcuts import render


def error404handler(request, exception):
    """
    Http 404 page not found error handler
    :param request: django http request
    :return: http response
    """
    return render(request, "core/404.html", status=404)


def error500handler(request):
    """
    Http 500 application error handler
    :param request: django request object
    :return: http response object
    """
    return render(request, "core/500.html", status=500)


def robots(request):
    """
    :param request: django http request
    :return: http response
    """
    return render(
        request,
        "core/robots.txt",
        content_type="text/plain",
    )
