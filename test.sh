#!/usr/bin/env bash

echo "Installing test requirements"
pip install -r test-requirements.txt

echo "Installing dependencies"
pip install -e .

echo "Running tests"
pytest

echo "Done!"