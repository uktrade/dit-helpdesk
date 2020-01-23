# Ui Testing

Note that the assertions were set from a given data snapshot which will most likely change.
In order to make these tests repteable at all times, we should commit and not change the "prepared"
folder content under "testing_prepared" and ensure that when docker is started we skip the tests that pottentially overwrite these files. Following this strategy we can ensure commodity codes are consistent across run.

## Setup

1) Ensure you download the latest chromedriver from the URL below:

https://chromedriver.chromium.org/downloads

Then move the binary to /usr/bin which is on your PATH already or create a folder and add it to the PATH environment variable I.E export PATH=$PATH:~/webdriver

2) Install dependencies: `$ pip install -r requirements/development.txt`

It's advised to run the command above on an isolated environment, like for example virtualenv.

## Run the tests

Execute the following command to run the tests: `pytest ui_test/specs`
