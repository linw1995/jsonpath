all: test

EMPTY :=
SPACE := $(EMPTY) $(EMPTY)

POETRY_VERSION = 1.0.0
POETRY_EXTRAS = lint test docs
POETRY_EXTRAS_ARGS = $(if $(POETRY_EXTRAS),-E,) $(subst $(SPACE),$(SPACE)-E$(SPACE),$(POETRY_EXTRAS))

init_by_venv:
	@echo ">> initing by venv..."
	@echo ">> creating venv..."
	@python3 -m virtualenv .venv
	@echo ">> installing Poetry ${POETRY_VERSION}"
	@.venv/bin/pip install poetry==$(POETRY_VERSION)
	@echo ">> installing $(if $(POETRY_EXTRAS),\"$(POETRY_EXTRAS)\" ,)dependencies by poetry"
	@.venv/bin/poetry install $(POETRY_EXTRAS_ARGS)
	@echo ">> all dependencies installed completed! please execute below command for development"
	@echo "> source .venv/bin/acitvate"

init_by_poetry:
	@echo ">> initing by `poetry --version`..."
	@echo ">> installing $(if $(POETRY_EXTRAS),\"$(POETRY_EXTRAS)\" ,)dependencies by poetry"
	@poetry install $(POETRY_EXTRAS_ARGS)
	@echo ">> make a symlink from the env created by poetry to ./.venv"
	@[ -h .venv ] && unlink .venv && echo ">> remove old link" || true
	@poetry run python -c "import sys; print(sys.prefix)" | { \
		read PYTHON_PREFIX; \
		echo ">> link .venv -> $$PYTHON_PREFIX"; \
		ln -s $$PYTHON_PREFIX .venv; \
		ln -s `which poetry` .venv/bin/poetry >/dev/null 2>&1 || true; \
	}
	@echo ">> all dependencies installed completed! please execute below command for development"
	@echo "> poetry shell"
	@echo ">> or:"
	@echo "> source .venv/bin/acitvate"


isort:
	@.venv/bin/pre-commit run isort

check-isort:
	@.venv/bin/pre-commit run check-isort

flake8:
	@.venv/bin/pre-commit run flake8

black:
	@.venv/bin/pre-commit run black

check-black:
	@.venv/bin/pre-commit run check-black

mypy:
	@.venv/bin/pre-commit run mypy

doc8:
	@.venv/bin/pre-commit run doc8

blacken-docs:
	@.venv/bin/pre-commit run blacken-docs

check:
	@.venv/bin/pre-commit run --hook-stage push

check-all:
	@.venv/bin/pre-commit run --all-files --hook-stage push

format-code: isort black blacken-docs
fc: format-code

_stash:
	@git diff > unstaged.diff && \
		if [ -s unstaged.diff ]; then \
			echo ">> Stashing into unstaged.diff"; \
			git apply -R unstaged.diff; \
		else \
			rm unstaged.diff; \
		fi;

_unstash:
	@if [ -s unstaged.diff ]; then \
		echo ">> Recovering from unstaged.diff"; \
		git apply unstaged.diff && \
		rm unstaged.diff; \
	fi;

_finally=|| code=$$?; \
	make _unstash \
		&& exit $$code

_test:
	@.venv/bin/pytest -q -x --ff --nf -s

test: _stash
	@make _test $(_finally)

_vtest:
	@.venv/bin/pytest -vv -x --ff --nf -s

vtest: _stash
	@make _vtest $(_finally)

_cov:
	@.venv/bin/pytest -vv --cov=jsonpath
	@.venv/bin/coverage xml
	@.venv/bin/coverage html
	@echo ">> open file://`pwd`/htmlcov/index.html to see coverage"

cov: _stash
	@make _cov $(_finally)

livereload_docs:
	@.venv/bin/python scripts/watch_build_and_serve_html_docs.py
live_docs: livereload_docs

clean:
	@rm -f .coverage
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@rm -rf coverage.xml
	@rm -rf *.egg-info
	@rm -rf dist

.PHONY: all init_by_venv init_by_poetry isort check-isort flake8 black blacken-docs \
	check-black check check-all format-code fc mypy _stash _unstash _finally _test \
	test _vtest vtest _cov cov clean
