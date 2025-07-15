#!/usr/bin/env bash

poetry run isort --profile black src tests
poetry run black --line-length 120 --skip-magic-trailing-comma src tests
