import json
import sys

from contextlib import contextmanager
from importlib import import_module, reload
from time import time
from unittest import mock

from django.conf import settings
from django.test import override_settings
from django.urls import clear_url_caches
from django.db.models import Q


always_true_Q = ~Q(pk__in=[])


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
            return 0.0

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


def flatten(list_of_lists):
    return [item for inner_list in list_of_lists for item in inner_list]


def unique_maintain_order(iterable):
    out = []
    seen = set()

    for val in iterable:
        if val not in seen:
            out.append(val)
            seen.add(val)

    return out


def _get_test_data(file_path):
    with open(file_path) as f:
        json_data = json.load(f)
    return json_data


@contextmanager
def patch_tts_json(model_class, tts_json_data_path):
    test_data = json.dumps(_get_test_data(tts_json_data_path))

    with mock.patch.object(
        model_class, "tts_json", new_callable=mock.PropertyMock(return_value=test_data)
    ):
        yield


@contextmanager
def patch_section_notes(model_class):
    test_data = {
        "id": 1,
        "section_id": 1,
        "content": "1. Any reference in this section to a particular genus or species \
            of an animal, except where the context otherwise requires, includes a reference \
            to the young of that genus or species.\r\n2. Except where the context otherwise \
            requires, throughout the nomenclature any reference to 'dried' products also covers \
            products which have been dehydrated, evaporated or freeze-dried.\r\n",
    }

    with mock.patch.object(
        model_class,
        "section_notes",
        new_callable=mock.PropertyMock(return_value=test_data),
    ):
        yield
