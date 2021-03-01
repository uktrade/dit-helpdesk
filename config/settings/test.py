"""
With these settings, tests run faster.
"""
import logging.config
import os
import re

from django.conf import settings

DEBUG = False
from django.utils.log import DEFAULT_LOGGING

from .base import *

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env.str("DJANGO_SECRET_KEY")
# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
# TEST_RUNNER = "django.test.runner.DiscoverRunner"
#
# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES[0]["OPTIONS"]["debug"] = True  # noqa F405
TEMPLATES[0]["APP_DIRS"]: False
TEMPLATES[0]["OPTIONS"]["loaders"] = [  # noqa F405
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]


DATABASES = {
    "default": {
        "ENGINE": "psqlextra.backend",  # 'django.db.backends.postgresql_psycopg2',
        "NAME": env.str("POSTGRES_DB"),
        "USER": env.str("POSTGRES_USER"),
        "PASSWORD": env.str("POSTGRES_PASSWORD"),
        "HOST": env.str("POSTGRES_HOST"),
        "PORT": env.str("POSTGRES_PORT"),
    }
}

INSTALLED_APPS.append("django_nose")
TEST_RUNNER = "django_nose.NoseTestSuiteRunner"

TEST_OUTPUT_DIR = env.str("TEST_OUTPUT_DIR")
NOSE_ARGS = [
    "--verbosity=3",
    "--nologcapture",
    "--with-spec",
    "--spec-color",
    "--with-xunit",
    "--xunit-file=%s/unittests.xml" % TEST_OUTPUT_DIR,
]

# Disable Django's logging setup
LOGGING_CONFIG = None


LOG_LEVEL = env("LOG_LEVEL")


# Test Data
TEST_COMMODITY_CODE = "0101210000"
TEST_COMMODITY_CODE_SPLIT = list(
    re.search("([0-9]{6})([0-9]{2})([0-9]{2})", TEST_COMMODITY_CODE).groups()
)
TEST_SUBHEADING_CODE = "0101210000"
TEST_HEADING_CODE = "0101000000"
TEST_HEADING_CODE_SHORT = "0101"
TEST_CHAPTER_CODE = "0100000000"
TEST_SECTION_ID = "1"
TEST_COUNTRY_CODE = "AU"
TEST_COUNTRY_NAME = "Australia"
TEST_COMMODITY_DESCRIPTION = "Pure-bred breeding animals"
TEST_HEADING_DESCRIPTION = "Live horses, asses, mules and hinnies"
TEST_SUBHEADING_DESCRIPTION = "Horses"
TEST_CHAPTER_DESCRIPTION = "Live animals"
TEST_SECTION_DESCRIPTION = "Live animals; animal products"

COMMODITY_DATA = APPS_DIR + "/commodities/tests/commodity_{0}.json".format(
    TEST_COMMODITY_CODE
)
COMMODITY_STRUCTURE = APPS_DIR + "/commodities/tests/structure_{0}.json".format(
    TEST_COMMODITY_CODE
)
SUBHEADING_STRUCTURE = (
    APPS_DIR
    + "/hierarchy/tests/subheading_{0}_structure.json".format(TEST_SUBHEADING_CODE)
)
HEADING_STRUCTURE = APPS_DIR + "/hierarchy/tests/heading_{0}_structure.json".format(
    TEST_HEADING_CODE
)
CHAPTER_STRUCTURE = APPS_DIR + "/hierarchy/tests/chapter_{0}_structure.json".format(
    TEST_CHAPTER_CODE
)
SECTION_STRUCTURE = APPS_DIR + "/hierarchy/tests/section_{}_structure.json".format(
    TEST_SECTION_ID
)
SECTIONJSON_DATA = APPS_DIR + "/trade_tariff_service/import_data/SectionJson.json"
CHAPTERJSON_DATA = APPS_DIR + "/trade_tariff_service/import_data/ChapterJson.json"
HEADINGJSON_DATA = APPS_DIR + "/trade_tariff_service/import_data/HeadingJson.json"
SUBHEADINGJSON_DATA = APPS_DIR + "/trade_tariff_service/import_data/SubHeadingJson.json"
COMMODITYHEADINGJSON_DATA = (
    APPS_DIR + "/trade_tariff_service/import_data/CommodityHeadingJson.json"
)
IMPORTMEASUREJSON_DATA = (
    APPS_DIR + "/trade_tariff_service/import_data/ImportMeasureJson.json"
)

ELASTICSEARCH_INDEX_NAMES = {
    "search.documents.section": "test_sections",
    "search.documents.chapter": "test_chapters",
    "search.documents.heading": "test_headings",
    "search.documents.subheading": "test_subheadings",
    "search.documents.commodity": "test_commodities",
}
ES_URL = "http://es:9200"
ELASTICSEARCH_DSL = {"default": {"hosts": ES_URL}}

SITE_READ_ONLY = False

INSTALLED_APPS += [
    "cms",
    "deferred_changes.tests.apps.DeferredChangesTestsConfig",
]

TRADE_TARIFF_CONFIG = {
    "UK": {
        "TREE": {
            "BASE_URL": "https://www.trade-tariff.service.gov.uk/api/v2/"
        },
        "JSON_OBJ": {
            "BASE_URL": "https://www.trade-tariff.service.gov.uk/api/v1/"
        }
    },
    "EU": {
        "TREE": {
            "BASE_URL": "https://www.trade-tariff.service.gov.uk/api/v2/"
        },
        "JSON_OBJ": {
            "BASE_URL": "https://www.trade-tariff.service.gov.uk/api/v1/"
        }
    }
}
