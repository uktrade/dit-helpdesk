import pytest
import ui_test.config as config
import os 

from selenium.webdriver import ChromeOptions
from splinter import Browser

chrome_options = ChromeOptions()
chrome_options.add_argument('--no-sandbox')
dir_path = os.path.dirname(os.path.realpath(__file__))
screenshot_path = '{path}/screenshots'.format(path=dir_path)

if not os.path.exists(screenshot_path):
    os.mkdir(screenshot_path)

@pytest.fixture(scope='module')
def browser():
    browser = Browser('chrome', headless=True, options=chrome_options)
    yield browser
    print('teardown')
    browser.quit()


@pytest.fixture(autouse=True)
def fixture_func(browser):
    browser.visit(config.BASE_URL)


@pytest.fixture(autouse=True, scope='function')
def teardown(request, browser):
    yield
    method_name = request.node.name
    print('test {name} failed '.format(name=method_name))
    browser.screenshot('{path}/screenshots/{name}'.format(path=dir_path, name=method_name), full=True)
