import pytest
import ui_test.config as config
from splinter import Browser


@pytest.fixture(scope='module')
def browser():
    browser = Browser('chrome')
    yield browser
    print('teardown')
    browser.quit()

@pytest.fixture(autouse=True)
def fixture_func(browser):
    browser.visit(config.BASE_URL)
