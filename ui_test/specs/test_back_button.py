import pytest
from ui_test.selectors.search import SEARCH
from ui_test.user_flows import search_country, search_commodity


def test_back_button_redirects_to_commodity_search(browser):
    search_country(browser, "Brazil")
    search_commodity(browser, "Coffee")
    browser.links.find_by_text("New search").click()

    assert browser.is_text_present("Search for the goods you are exporting")


def test_country_form_errors_when_resubmitting_after_hitting_back_button_from_search_page(
    browser
):
    search_country(browser, "Brazil")
    assert browser.is_text_present("Brazil United Kingdom")

    browser.execute_script("window.history.go(-1)")
    assert browser.is_text_present("What country are you exporting from?")

    search_country(browser, "")
    assert browser.is_text_present("There is a problem")
    assert browser.is_text_present("Enter a country")
