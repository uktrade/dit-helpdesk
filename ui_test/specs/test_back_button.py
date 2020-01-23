import pytest
from ui_test.selectors.search import SEARCH
from ui_test.user_flows import search_country, search_commodity

def test_back_button_redirects_to_commodity_search(browser):
    search_country(browser, 'Brazil')
    search_commodity(browser, 'Coffee')
    browser.links.find_by_text('Back').click()

    assert(browser.is_text_present('Search for the goods you are exporting'))
