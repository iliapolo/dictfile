#!/usr/bin/env bash -e

echo "Installing test requirements"
pip install -r test-requirements.txt

echo "Installing dependencies"
pip install -e .

echo "Running tests"
py.test --cov-report term-missing --cov=fileconfig fileconfig/tests

echo "Running code analysis"
pylint --rcfile .pylint.ini fileconfig/tests

echo "Done!"