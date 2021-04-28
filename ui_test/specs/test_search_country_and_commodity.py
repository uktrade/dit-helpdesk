from ui_test.user_flows import search_country, search_commodity


def test_search_country_and_commodity_by_keyword(browser):
    search_country(browser, "Brazil")
    search_commodity(browser, "Coffee")
    assert browser.is_text_present("Showing 3 results for Coffee")


def test_search_country_and_commodity_by_code(browser):
    search_country(browser, "Brazil")
    search_commodity(browser, "2101000000")
    assert browser.is_text_present(
        "Export 2101.00.00.00 from Brazil to the United Kingdom"
    )


def test_empty_country(browser):
    search_country(browser, "")
    assert browser.is_text_present("There is a problem")
    assert browser.is_text_present("Enter a country")

    search_country(browser, "India")
    assert browser.is_text_present("India")
    assert browser.is_text_present("United Kingdom")


def test_empty_commodity_search(browser):
    search_country(browser, "India")
    search_commodity(browser, "6435643534656")
    assert browser.is_text_present("There are no results for 6435643534656")

    search_commodity(browser, "_INVALID_")
    assert browser.is_text_present("_INVALID_")
