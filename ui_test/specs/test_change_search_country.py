import pytest
from ui_test.selectors.search import SEARCH
from ui_test.user_flows import search_country, search_commodity

def test_change_search_country(browser):
    search_country(browser, 'Brazil')
    assert(browser.is_text_present('Brazil'))
    assert(browser.is_text_present('United Kingdom'))

    browser.links.find_by_text('Change').click()
    search_country(browser, 'India')
    assert(browser.is_text_present('India'))
    assert(browser.is_text_present('United Kingdom'))
