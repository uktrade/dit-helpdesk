import pytest
from ui_test.selectors.search import SEARCH
from selenium.webdriver.common.keys import Keys


def test_search_country_and_commodity_by_keyword(browser):
    search_country(browser, 'Brazil')
    search_commodity(browser, 'Coffee')
    assert(browser.is_text_present('Showing 2 results for Coffee'))


def test_search_country_and_commodity_by_code(browser):
    search_country(browser, 'Brazil')
    search_commodity(browser, '2101301100')
    assert(browser.is_text_present('Export 2101.30.11.00 from Brazil to the United Kingdom'))


def search_country(browser, country_name):
    search = browser.find_by_css(SEARCH['country'])
    search.first.type(country_name)
    search.type(Keys.RETURN)
    browser.find_by_css(SEARCH['continue']).click()


def search_commodity(browser, commodity):
    search = browser.find_by_css(SEARCH['commodity'])
    search.first.type(commodity)
    browser.find_by_css(SEARCH['continue']).click()
