import pytest
from ui_test.selectors.commodity import COMMODITY
from ui_test.user_flows import search_country, search_commodity


def test_sort_commodity_by_code_and_ranking(browser):
    search_country(browser, 'Brazil')
    search_commodity(browser, 'Coffee')

    browser.select(COMMODITY['sort'], 'ranking')
    firstCommodity = browser.find_by_css(COMMODITY['commodityCode']).first
    assert(firstCommodity.text == '6911100010')

    browser.select(COMMODITY['sort'], 'commodity_code')
    firstCommodity = browser.find_by_css(COMMODITY['commodityCode']).first
    assert(firstCommodity.text == '0901210000')
