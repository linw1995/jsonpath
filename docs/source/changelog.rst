=========
Changelog
=========

v0.2.0-alpha
~~~~~~~~~~~~

- 1be3dbf New:Add scripts/export_requirements_txt.sh
- 56d09bd Chg:Upgrade dependencies
- ba5868c Chg:Update GitHub Actions config
- 944fe7b New:Add caches action
- 8625aeb New:Upload release built from actions
- b882c38 Chg:Use lark-parser to replace sly
- dad27f8 Fix,Dev:CI err because of poetry install git dep
- 1fd8c41 Chg:Replace tab with space in grammar.lark
- e1a73a4 Chg:more specific type annotation
- 9dbbdfb Chg:Upgrade lark to 0.8.1
- b62b848 Chg:Rafactoring for reducing non-neccessory code
- b84fb93 Fix:Not raise JSONPath undefined function error explicitly
- d9ff6f6 Chg:Use type.__new__ to overwrite expr's find method
- 3b8d41d Chg:Refactoring for reducing the duplicated code
- ce42257 New:Create docs by sphinx
- bb31c2c Fix,Dev:lint docs error
- b09ec5e New,Dev:Watch related files,
  build and serve Sphinx documentation automatically.
- a078e8f Fix,Dev:Isort error
- db56773 New,Dev:Test with doctest by pytest
- 48ad21c Fix,Dev:shell function not inherits envs of parent process
- 28a4fc0 Fix,Dev:lint error
- a78fdf8 Fix,Dev:Live reload docs error
  due to .venv/bin/python not setting env-values
- 2995f46 New,Doc:API reference
- d918d80 Chg,Doc:Update quickstarts.rst
- f18d92c New:Add .readthedocs.yaml for docs deployment
- e6b7576 New,Doc:Translate :py:mod: directive into link


.. include:: history.rst
    :start-line: 4
