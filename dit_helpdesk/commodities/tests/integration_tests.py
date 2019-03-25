import unittest
from selenium import webdriver


class TestCommodity(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_commodity_page_exists(self):
        self.driver.get("http://localhost:8080/country/au/commodity/0101210000")

    def tearDown(self):
        self.driver.quit


if __name__ == '__main__':
    unittest.main()