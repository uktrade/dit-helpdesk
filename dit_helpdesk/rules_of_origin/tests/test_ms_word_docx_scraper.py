import logging

from django.test import TestCase

from rules_of_origin.DocxScraper import DocxScraper

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class MsWrodDocxScraperTestCase(TestCase):
    """
    Test MS Word Docx Scraper
    """

    def test_processing_text_with_footnote_returns_text_with_formatted_html_footnote_link(self):
        scraper = DocxScraper()
        source_text = "This is some text with a footnote(1)"
        result_text = scraper.process_footnote(source_text)
        self.assertEqual(result_text, 'This is some text with a footnote(<a href="#footnote_1">1</a>)')

    def test_footnotes_exist(self):
        self.scraper = DocxScraper()
        self.scraper.load("test_source/GSP ROO v2.docx")
        self.assertTrue(len(self.scraper.footnotes) > 0)
