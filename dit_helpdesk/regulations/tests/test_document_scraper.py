import logging
import os
import requests
import requests_mock

from django.conf import settings
from django.test import TestCase
from pandas import DataFrame

from regulations.documents_scraper import (
    data_loader,
    DocumentScraper,
    extract_html_title,
    data_writer,
)

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


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

    @requests_mock.Mocker()
    def test_appending_url_title(self, mock):

        legislation_url = "http://www.legislation.gov.uk/eur/2010/640/contents"
        legislation_html = (
            "<html><head><title>Response Placeholder</title></head></html>"
        )
        mock.get(
            legislation_url,
            text=legislation_html,
        )
        requests.get(legislation_url).text

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

    @requests_mock.Mocker()
    def test_extract_html(self, mock):

        legislation_url = "http://www.legislation.gov.uk/eur/2010/640/contents"
        legislation_html = (
            "<html><head><title>Response Placeholder</title></head></html>"
        )
        mock.get(
            legislation_url,
            text=legislation_html,
        )
        requests.get(legislation_url).text

        title = extract_html_title(legislation_url)
        self.assertEqual(
            title,
            "Response Placeholder",
        )
