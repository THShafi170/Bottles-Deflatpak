#!/bin/bash
# Description: Run all quality checks using the project venv

VENV_PATH="./venv"
PYTHON="$VENV_PATH/bin/python3"

if [ ! -d "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

echo "--- Running Ruff (Linter & Formatter) ---"
$VENV_PATH/bin/ruff check .
$VENV_PATH/bin/ruff format --check .

echo "--- Running Mypy (Type Checker) ---"
$VENV_PATH/bin/mypy .

echo "--- Running Pylint ---"
$VENV_PATH/bin/pylint bottles

echo "--- Running Unit Tests ---"
$VENV_PATH/bin/pytest

echo "--- Running Pre-commit (all files) ---"
$VENV_PATH/bin/pre-commit run --all-files
