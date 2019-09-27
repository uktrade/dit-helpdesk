#!/bin/bash -xe

coverage run manage.py test dit_helpdesk --settings=config.settings.test --noinput
coverage report -m
coverage xml
coverage html -d $TEST_OUTPUT_DIR/coverage_html
# -----------------------------------------------------------------------------
# To destroy and rebuild:
# -----------------------------------------------------------------------------
# $ docker-compose -f test.yml stop
# $ docker-compose -f test.yml rm
# $ docker-compose -f test.yml build
# $ docker-compose -f test.yml up
# -----------------------------------------------------------------------------
