import logging
import os

from django.conf import settings
from django.test import TestCase
from pandas import DataFrame

from unittest import mock

from regulations.documents_scraper import (
    data_loader,
    DocumentScraper,
    extract_html_title,
    data_writer,
)

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, html_doc):
            self.text = html_doc

    return MockResponse("<html><head><title>Response Placeholder</title></head></html>")


class RegulationsDocumentScraperTestCase(TestCase):
    """
    Test Regulations document scraper
    """

    def test_data_loader_with_csv(self):

        file_path = settings.REGULATIONS_DATA_PATH.format(
            "product_specific_regulations.csv"
        )
        logger.debug(file_path)
        data = data_loader(file_path)
        self.assertTrue(isinstance(data, DataFrame))

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_appending_url_title(self, mock_request):
        scraper = DocumentScraper()
        scraper.source_file = "test_product_specific_regulations.csv"
        scraper.output_file = "test_out_product_specific_regulations.csv"
        scraper.load()

        self.assertIsInstance(scraper.documents, dict)
        self.assertEqual(len(scraper.documents.keys()), 1)

    def test_data_writer(self):
        file_path = settings.REGULATIONS_DATA_PATH.format("test.json")
        data_writer(file_path, {"foo": "bar"})
        self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_extract_html(self, mock_request):
        title = extract_html_title(
            "http://www.legislation.gov.uk/eur/2010/640/contents"
        )
        self.assertEqual(
            title,
            "Response Placeholder",
        )
