import pytest
import ui_test.config as config

from selenium.webdriver import ChromeOptions
from splinter import Browser

chrome_options = ChromeOptions()
chrome_options.add_argument('--no-sandbox')

@pytest.fixture(scope='module')
def browser():
    browser = Browser('chrome', headless=True, options=chrome_options)
    yield browser
    print('teardown')
    browser.quit()


@pytest.fixture(autouse=True)
def fixture_func(browser):
    browser.visit(config.BASE_URL)
