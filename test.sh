#!/usr/bin/env bash

set -x -e

black .
mypy .
python -m pytest
