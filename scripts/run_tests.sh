#!/bin/bash
# Run in container

set -e
python3 -m pylint --rcfile=.pylintrc crawler
python3 -m pylint --rcfile=.pylintrc backend
python3 -m pylint --rcfile=.pylintrc scripts
python3 -m pytest --junitxml="${TEST_REPORT_FILE:./pytest-results.xml}"