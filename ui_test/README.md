# Ui Testing

## Setup

1) Ensure you download the latest chromedriver from the URL below:

https://chromedriver.chromium.org/downloads

Then move the binary to /usr/bin which is on your PATH already or create a folder and add it to the PATH environment variable I.E export PATH=$PATH:~/webdriver

2) Install dependencies: `$ pip install -r requirements/development.txt`

It's advised to run the command above on an isolated environment, like for example virtualenv.

## Run the tests

1) Start the application by using the automation compose by running the following command
in root of project:

`$ docker-compose -f test-automation.yml build`
`$ docker-compose -f test-automation.yml up`

2) Execute the following command to run the tests: 

`$ pytest ui_test/specs`

## Creating Docker container for CircleCI

```bash
export VERSION=1.0.0 # Increment this version each time when you edit Dockerfile.

docker login # Ask webops for Docker Hub access to the ukti group.
docker build -f ui_test/Dockerfile -t dit-helpdesk-test .

docker tag dit-helpdesk-test:latest ukti/dit-helpdesk-test:${VERSION}
docker tag dit-helpdesk-test:latest ukti/dit-helpdesk-test:latest

docker push ukti/dit-helpdesk-test:${VERSION}
docker push ukti/dit-helpdesk-test:latest
```

You image should be now listed at [Docker Hub](https://cloud.docker.com/u/ukti/repository/docker/ukti/dit-helpdesk-test/tags).
