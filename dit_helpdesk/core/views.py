from django.shortcuts import render


def error404handler(request, exception):
    """
    Http 404 page not found error handler
    :param request: django http request
    :return: http response
    """
    response = render(request, 'core/404.html')
    response.status_code = 404

    return response


def error500handler(request):
    """
    Http 500 application error handler
    :param request: django request object
    :return: http response object
    """
    response = render(request, 'core/500.html')
    response.status_code = 500

    return response
