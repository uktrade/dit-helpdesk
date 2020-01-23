from ui_test.selectors.search import SEARCH
from selenium.webdriver.common.keys import Keys


def search_country(browser, country_name):
    search = browser.find_by_css(SEARCH['country'])
    search.first.type(country_name)
    search.type(Keys.RETURN)
    browser.find_by_css(SEARCH['continue']).click()


def search_commodity(browser, commodity):
    search = browser.find_by_css(SEARCH['commodity'])
    search.first.type(commodity)
    browser.find_by_css(SEARCH['continue']).click()
