all: test

EMPTY :=
SPACE := $(EMPTY) $(EMPTY)

POETRY_EXTRAS = lint test docs
POETRY_EXTRAS_ARGS = $(if $(POETRY_EXTRAS),-E,) $(subst $(SPACE),$(SPACE)-E$(SPACE),$(POETRY_EXTRAS))

PYTHON = system
QUIET =

link_venv:
	@[ $(QUIET) ] || echo ">> make a symlink from the env created by poetry to ./.venv"
	@[ -h .venv ] && unlink .venv && ( [ $(QUIET) ] || echo ">> remove old link" ) || true
	@poetry run python -c "import sys; print(sys.prefix)" | tail -n 1 | { \
		read PYTHON_PREFIX; \
		[ -d $$PYTHON_PREFIX ] && { \
			[ $(QUIET) ] || echo ">> link .venv -> $$PYTHON_PREFIX"; \
			ln -s $$PYTHON_PREFIX .venv; \
			ln -s `which poetry` .venv/bin/poetry >/dev/null 2>&1 || true; \
		} \
	}
	@[ $(QUIET) ] || { \
		echo ">> please execute below command for development"; \
		echo "> poetry shell"; \
		echo ">> or:"; \
		echo "> source .venv/bin/activate"; \
	}

activate:
	@poetry env use $(PYTHON)
	@make PYTHON=$(PYTHON) QUIET=$(QUIET) link_venv

deactivate: # must deactivate before using nox
	@make PYTHON=$(PYTHON) QUIET=true activate
	@poetry env use system

deinit:
	@echo ">> remove venv..."
	@[ -h .venv ] && rm -rf `realpath .venv` && rm .venv && echo ">> remove success" || true
	@[ -d .venv ] && rm -rf .venv && echo ">> remove success" || true

init_by_poetry:
	@echo ">> initing by `poetry --version`..."
	@echo ">> installing $(if $(POETRY_EXTRAS),\"$(POETRY_EXTRAS)\" ,)dependencies by poetry"
	@make activate
	@poetry install $(POETRY_EXTRAS_ARGS)
	@echo ">> all dependencies installed completed!"
	@make QUIET=true activate

pre-commit_init:
	@.venv/bin/pre-commit install

_clean_codegen:
	@rm -f jsonpath/lark_parser.py

isort: _clean_codegen
	@.venv/bin/pre-commit run isort

check-isort: _clean_codegen
	@.venv/bin/pre-commit run check-isort

flake8: _clean_codegen
	@.venv/bin/pre-commit run flake8

black: _clean_codegen
	@.venv/bin/pre-commit run black

check-black: _clean_codegen
	@.venv/bin/pre-commit run check-black

mypy: _clean_codegen
	@.venv/bin/pre-commit run mypy

doc8: _clean_codegen
	@.venv/bin/pre-commit run doc8

blacken-docs: _clean_codegen
	@.venv/bin/pre-commit run blacken-docs

check: _clean_codegen
	@.venv/bin/pre-commit run --hook-stage push

check-all: _clean_codegen
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
	@.venv/bin/pytest -q -x --ff --nf

test: _stash
	@make _test $(_finally)

_vtest:
	@.venv/bin/pytest -vv -x --ff --nf

vtest: _stash
	@make _vtest $(_finally)

_cov:
	@.venv/bin/pytest -vv --cov=jsonpath
	@.venv/bin/coverage xml
	@.venv/bin/coverage html
	@echo ">> open file://`pwd`/htmlcov/index.html to see coverage"

cov: _stash
	@make _cov $(_finally)

_nox:
	@make QUIET=true deactivate
	@rm -f .coverage
	@.venv/bin/nox -k test
	@.venv/bin/coverage xml
	@.venv/bin/coverage html
	@echo ">> open file://`pwd`/htmlcov/index.html to see coverage"
	@make QUIET=true activate

nox: _stash
	@make _nox $(_finally)

build: _stash
	@.venv/bin/nox -k build $(_finally)

clean_nox:
	@rm -rf .nox

livereload_docs:
	@.venv/bin/python scripts/watch_build_and_serve_html_docs.py
live_docs: livereload_docs

export_requirements_txt: deactivate
	@.venv/bin/nox -k export_requirements_txt

export: export_requirements_txt

clean: _clean_codegen
	@rm -f .coverage
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@rm -rf coverage.xml
	@rm -rf *.egg-info
	@rm -rf dist
	@rm -rf __pycache__
	@rm -rf **/__pycache__

.PHONY: all init_by_venv init_by_poetry isort check-isort flake8 black blacken-docs \
	check-black check check-all format-code fc mypy _stash _unstash _finally _test \
	test _vtest vtest _cov cov clean _clean_codegen pre-commit_init \
	export_requirements_txt export activate deactivate link_venv
