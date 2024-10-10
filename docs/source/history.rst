=======
History
=======

v0.9.0
~~~~~~

Build
*****

- Remove support for Python 3.7

v0.8.0
~~~~~~

Features
********

- 69ff6cb_ add iter_find and find_first methods
- be22151_ better JSONPath object representations

Refactor
********

- 9d9d78f_ raise AttributeError by object.__getattribute__
- 4191b8c_ not registers base class "Expr" for chaining invocations

Build
*****

- cc6ab56_ 2040721_ upgrade lark-parser package to latest
- fb7e902_ fit with latest PDM
- 10ea6d3_ excludes .mypy_cache for local build

Fix
***

- 1dccec1_ fix: right way to generate standalone parser

.. _69ff6cb: https://github.com/linw1995/jsonpath/commit/69ff6cb47a08d3f957224adb163970454b6a1c87
.. _be22151: https://github.com/linw1995/jsonpath/commit/be221513bd8a1821e8007eb1c2d4f10aa6d3f987
.. _9d9d78f: https://github.com/linw1995/jsonpath/commit/9d9d78fd60b7b284c446c06e7102d05decd24c2b
.. _4191b8c: https://github.com/linw1995/jsonpath/commit/4191b8c745871733e58e97be11cdbcd845870484
.. _cc6ab56: https://github.com/linw1995/jsonpath/commit/cc6ab56
.. _2040721: https://github.com/linw1995/jsonpath/commit/2040721
.. _1dccec1: https://github.com/linw1995/jsonpath/commit/1dccec1
.. _fb7e902: https://github.com/linw1995/jsonpath/commit/fb7e902
.. _10ea6d3: https://github.com/linw1995/jsonpath/commit/10ea6d3

v0.7.3
~~~~~~

- a4e3dee Chg:Refactoring
- f46e87e Fix:Exports requirements.txt error
- c085900 New:Supports Python3.9
- 3f8b882 Fix:mypy error when using Python39
- 3b1a40a Fix:Missing Python3.9
- 53905c2 Chg:Update Brace class doc.
- ad76217 Chg:Update Brace class doc.
- c4d9538 Fix:Build document first while running 'make live_docs'
- b12491e Fix,Dev:Must deactivate before using nox
- 82ada7a Fix:build.py file contamination (fixes #26)

v0.7.2
~~~~~~

- 5741909 New:Add a new context variable "parent"
- dde3703 New:Add a helper function 'temporary_set'
- 3336e86 New:Be able to get parent node while searching
- 901354f Fix:Slice nested exprs find erorr
- c0e82d6 Fix:Slice.find apply on list only

v0.7.1
~~~~~~

- 7ba2b1c Fix:IndexError raised from method Array.find (#20)

v0.7.0
~~~~~~

- 46cfd08 Fix,Dev:make init_by_poetry error when python(system) version is
  lower than 3.7
- 19f981f Chg:Upgrade lark-parser
- 982e344 New:Rewrite grammar to support more extensible jsonpath expression,
  e.g., more elegant comparison syntax.
- 1803339 New:Slice supports to cooperate with JSONPath.

v0.6.1
~~~~~~

- c79ef49 Fix:jsonpath/lark_parser.py file is missing in wheel file

v0.6.0
~~~~~~

- 3fa0e29 Chg:Remove redundant code
- 8e33efd Fix:Typo
- d3552ac Fix:Release bad sdist. (closes #11)
- e8eab43 New:Create CODE_OF_CONDUCT.md
- 4d8dcd5 Chg:Better way to use codegen module
- f85bd48 Chg:Raises AssertionError when the operator is not supported

v0.5.1
~~~~~~

- 5d30a84 Fix,Dev,CI:Release stage error

v0.5.0
~~~~~~

- 2971509 New:Add --ensure-ascii argument. (closes #9)
- 1c6f602 New:Be able to use stand-alone parser.
- c78505e Chg:Only release built distribution, wheel. (See #11)

v0.4.0
~~~~~~

- 9f8f039 New:Add Command-line interface support

v0.3.0
~~~~~~

- 98e6718 New:Add Predicate class

v0.2.0
~~~~~~

- Chg:Use lark-parser to replace sly
- New:Create docs by sphinx
- New,Dev:Watch related files,
  build and serve Sphinx documentation automatically.
- New,Dev:Test with doctest by pytest
- New:Add .readthedocs.yaml for docs deployment

v0.2.0-alpha.2
~~~~~~~~~~~~~~

- 2440951 Fix:Cannot release into PyPI

v0.2.0-alpha.1
~~~~~~~~~~~~~~

- ea0aaff Chg,Dev:Allow to commit on master branch
- bc42f61 Fix:Type annotation error

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

v0.1.1
~~~~~~

- 35f0960 New:Add release actions for pypi and gh-release
- ce022b6 New:Add codecov for code coverage report
- 7f4fe3c Fix:The reduce/reduce conflicts
- 258b0fa Fix:The shift/reduce conflicts
- 95f088d New:Add Github Actions for CI
