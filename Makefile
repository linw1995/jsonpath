all: test

EMPTY :=
SPACE := $(EMPTY) $(EMPTY)

POETRY_VERSION = 0.12.17
POETRY_EXTRAS = linting test
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

check:
	@.venv/bin/pre-commit run --hook-stage push

check-all:
	@.venv/bin/pre-commit run --all-files --hook-stage push

format-code: isort black
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
	@.venv/bin/coverage html
	@echo ">> open file://`pwd`/htmlcov/index.html to see coverage"

cov: _stash
	@make _cov $(_finally)

clean:
	@rm -f .coverage
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@rm -rf *.egg-info
	@rm -rf dist

.PHONY: all init_by_venv init_by_poetry isort check-isort flake8 black \
	check-black check check-all format-code fc _stash _unstash _finally _test \
	test _vtest vtest _cov cov clean
