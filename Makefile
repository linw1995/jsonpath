help:
	@echo "PYTHON=X.Y init	setup development environemnt with specific Python version"
	@echo "init		setup development environment with defualt Python version 3.9"
	@echo "update-dev	update devepoment dependencies via pdm and via pre-commit"
	@echo "update		update all dependencies via pdm and via pre-commit"
	@echo "pre-commit	setup git hooks"
	@echo "check-all	run code quality checkers"
	@echo "test		run quick tests"
	@echo "vtest		run quick tests with verbose"
	@echo "PYTHON=X.Y cov	run tests with coverage and with specific Python version"
	@echo "cov		run tests with coverage and with default Python version 3.9"
	@echo "serve-docs	serve documents with live-reloading"

EMPTY :=
SPACE := $(EMPTY) $(EMPTY)

PYTHON = 3.10
EXTRAS = parser
DEV_EXTRAS = test docs
EXTRAS_ARGS = $(if $(EXTRAS),-G,) $(subst $(SPACE),$(SPACE)-G$(SPACE),$(EXTRAS))
DEV_EXTRAS_ARGS = $(if $(DEV_EXTRAS),-G,) $(subst $(SPACE),$(SPACE)-G$(SPACE),$(DEV_EXTRAS))

# Environment setup
init:
	@echo ">> installing $(if $(EXTRAS),\"$(EXTRAS)\" ,)dependencies by pdm"
	$(if $(PYTHON),pdm use -f $(PYTHON),)
	pdm info && pdm info --env
	pdm sync -v $(EXTRAS_ARGS) $(DEV_EXTRAS_ARGS)
	pdm config -l use_venv true

deinit:
	rm -rf .nox
	rm -rf __pypackages__
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .pytest_cache
	rm -rf *.egg-info


update-dev:
	pdm update $(DEV_EXTRAS_ARGS)
	pre-commit autoupdate

update:
	pdm update
	pre-commit autoupdate

# Environment setup end

pre-commit:
	pre-commit install --hook-type commit-msg --hook-type pre-commit --overwrite

check-all:
	pre-commit run --all-files

test:
	pdm run pytest -q -x --ff --nf

vtest:
	pdm run pytest -vv -x --ff --nf

cov:
	rm -rf .coverage
	nox -p $(PYTHON) -s coverage_test coverage_report -- $(TARGET)

# Docs
serve-docs:
	pdm run python scripts/watch_build_and_serve_html_docs.py
