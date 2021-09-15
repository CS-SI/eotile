.PHONY: help test lint

help:  ## this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install:  ## install environment for development target
	@virtualenv -p `which python3` .venv
	@.venv/bin/pip install -e .[dev]
	@.venv/bin/pre-commit install -t pre-commit
	@.venv/bin/pre-commit install -t pre-push

test:  ## run tests (requires venv activation)
	@python tests/test_eotile.py

lint:  ## run black and isort
	@isort **/*.py
	@black **/*.py

mypy :  ## run tests using mypy
	@mypy tests/test_eotile.py --ignore-missing-import

pylint :  ## run pylint
	@pylint eotile/**/*.py
