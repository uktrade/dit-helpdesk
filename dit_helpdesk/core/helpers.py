import sys

from contextlib import contextmanager
from functools import wraps
from importlib import import_module, reload
from time import time

from django.conf import settings
from django.http import Http404
from django.test import override_settings
from django.urls import clear_url_caches


class Timer:

    def __init__(self):
        self.start_time = None
        self.stop_time = None

    def start(self):
        self.start_time = time()

    def stop(self):
        self.stop_time = time()

    def elapsed(self):
        if not (self.start_time and self.stop_time):
            return 0.

        return self.stop_time - self.start_time


def reload_urls(urlconf=None):
    clear_url_caches()
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        reload(sys.modules[urlconf])
    import_module(urlconf)


@contextmanager
def reset_urls_for_settings(urlconf=None, **kwargs):
    with override_settings(**kwargs):
        reload_urls(urlconf)
        yield

    reload_urls(urlconf)


def require_feature(feature_switch):
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if not getattr(settings, feature_switch, False):
                raise Http404

            return func(request, *args, **kwargs)
        return inner
    return decorator
