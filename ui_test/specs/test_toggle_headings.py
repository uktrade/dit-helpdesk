import pytest
from ui_test.selectors.commodity import COMMODITY
from ui_test.user_flows import search_country, search_commodity


def test_toggle_between_headings(browser):
    search_country(browser, 'Brazil')
    search_commodity(browser, 'Coffee')

    browser.find_by_css(COMMODITY['hideHeadings']).click()
    assert(browser.is_text_present('Showing 63 results for Coffee', 10))

    browser.find_by_css(COMMODITY['showHeadings']).click()
    assert(browser.is_text_present('Showing 147 results for Coffee', 10))