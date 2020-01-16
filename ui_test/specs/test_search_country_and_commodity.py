import pytest
from ui_test.selectors.search import SEARCH
from ui_test.user_flows import search_country, search_commodity


def test_search_country_and_commodity_by_keyword(browser):
    search_country(browser, 'Brazil')
    search_commodity(browser, 'Coffee')
    assert(browser.is_text_present('Showing 2 results for Coffee'))


def test_search_country_and_commodity_by_code(browser):
    search_country(browser, 'Brazil')
    search_commodity(browser, '2101301100')
    assert(browser.is_text_present('Export 2101.30.11.00 from Brazil to the United Kingdom'))
