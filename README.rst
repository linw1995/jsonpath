========
JSONPATH
========

|license| |Pypi Status| |Python version| |Package version| |PyPI - Downloads|
|GitHub last commit| |Code style: black| |Build Status| |codecov|

A selector expression for extracting data from JSON.

Quickstarts
<<<<<<<<<<<


Installation
~~~~~~~~~~~~

Install the stable version from PYPI.

.. code-block:: shell

    pip install jsonpath-extractor

Or install the latest version from Github.

.. code-block:: shell

    pip install git+https://github.com/linw1995/jsonpath.git@master

Usage
~~~~~

.. code-block:: json

    {
        "goods": [
            {"price": 100, "category": "Comic book"},
            {"price": 200, "category": "magazine"},
            {"price": 200, "no category": ""}
        ],
        "targetCategory": "book"
    }


How to parse and extract all the comic book data from the above JSON file.

.. code-block:: python3

    import json

    from jsonpath import parse

    with open("example.json", "r") as f:
        data = json.load(f)

    assert parse("$.goods[contains(@.category, $.targetCategory)]").find(
        data
    ) == [{"price": 100, "category": "Comic book"}]

Or use the `jsonpath.core <https://jsonpath.readthedocs.io/en/latest/api_core.html>`_ module to extract it.

.. code-block:: python3

    from jsonpath.core import Root, Contains, Self

    assert Root().Name("goods").Array(
        Contains(Self().Name("category"), Root().Name("targetCategory"))
    ).find(data) == [{"price": 100, "category": "Comic book"}]

Changelog
<<<<<<<<<

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



.. |license| image:: https://img.shields.io/github/license/linw1995/jsonpath.svg
    :target: https://github.com/linw1995/jsonpath/blob/master/LICENSE

.. |Pypi Status| image:: https://img.shields.io/pypi/status/jsonpath-extractor.svg
    :target: https://pypi.org/project/jsonpath-extractor

.. |Python version| image:: https://img.shields.io/pypi/pyversions/jsonpath-extractor.svg
    :target: https://pypi.org/project/jsonpath-extractor

.. |Package version| image:: https://img.shields.io/pypi/v/jsonpath-extractor.svg
    :target: https://pypi.org/project/jsonpath-extractor

.. |PyPI - Downloads| image:: https://img.shields.io/pypi/dm/jsonpath-extractor.svg
    :target: https://pypi.org/project/jsonpath-extractor

.. |GitHub last commit| image:: https://img.shields.io/github/last-commit/linw1995/jsonpath.svg
    :target: https://github.com/linw1995/jsonpath

.. |Code style: black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

.. |Build Status| image:: https://img.shields.io/github/workflow/status/linw1995/jsonpath/Python%20package
    :target: https://github.com/linw1995/jsonpath/actions?query=workflow%3A%22Python+package%22

.. |codecov| image:: https://codecov.io/gh/linw1995/jsonpath/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/linw1995/jsonpath
