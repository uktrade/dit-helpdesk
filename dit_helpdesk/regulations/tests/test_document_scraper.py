import logging
import os

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

    def test_appending_url_title(self):
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

    def test_extract_html(self):
        title = extract_html_title(
            "http://www.legislation.gov.uk/eur/2010/640/contents"
        )
        self.assertEqual(
            title,
            "Regulation (EU) No 640/2010 of the European Parliament and of the Council of 7 "
            "July 2010 establishing a catch documentation programme for bluefin tuna Thunnus "
            "thynnus and amending Council Regulation (EC) No 1984/2003",
        )
