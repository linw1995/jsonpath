#!/bin/bash
# GitHub does not support poetry for creating dependency graph.
# https://help.github.com/en/github/visualizing-repository-data-with-graphs/listing-the-packages-that-a-repository-depends-on#supported-package-ecosystems
.venv/bin/poetry export -f requirements.txt --dev -E lint -E test > requirements.txt
.venv/bin/poetry export -f requirements.txt > requirements-mini.txt
