========
JSONPATH
========

|license| |Pypi Status| |Python version| |Package version| |PyPI - Downloads|
|GitHub last commit| |Code style: black| |Build Status| |codecov| |PDM managed|

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

    assert parse("$.goods[contains(@.category, $.targetCategory)]").find(data) == [
        {"price": 100, "category": "Comic book"}
    ]

Or use the `jsonpath.core <https://jsonpath.readthedocs.io/en/latest/api_core.html>`_ module to extract it.

.. code-block:: python3

    from jsonpath.core import Root, Contains, Self

    assert Root().Name("goods").Predicate(
        Contains(Self().Name("category"), Root().Name("targetCategory"))
    ).find(data) == [{"price": 100, "category": "Comic book"}]


Usage via CLI
~~~~~~~~~~~~~

The faster way to extract by using CLI.

.. code-block:: shell

    jp -f example.json "$.goods[contains(@.category, $.targetCategory)]"

Or pass content by pipeline.

.. code-block:: shell

    cat example.json | jp "$.goods[contains(@.category, $.targetCategory)]"

The output of the above commands.

.. code-block:: json

    [
      {
        "price": 100,
        "category": "Comic book"
      }
    ]

Changelog
<<<<<<<<<

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


Contributing
<<<<<<<<<<<<


Environment Setup
~~~~~~~~~~~~~~~~~

Clone the source codes from Github.

.. code-block:: shell

    git clone https://github.com/linw1995/jsonpath.git
    cd jsonpath

Setup the development environment.
Please make sure you install the pdm_,
pre-commit_ and nox_ CLIs in your environment.

.. code-block:: shell

    make init
    make PYTHON=3.7 init  # for specific python version

Linting
~~~~~~~

Use pre-commit_ for installing linters to ensure a good code style.

.. code-block:: shell

    make pre-commit

Run linters. Some linters run via CLI nox_, so make sure you install it.

.. code-block:: shell

    make check-all

Testing
~~~~~~~

Run quick tests.

.. code-block:: shell

    make

Run quick tests with verbose.

.. code-block:: shell

    make vtest

Run tests with coverage.
Testing in multiple Python environments is powered by CLI nox_.

.. code-block:: shell

    make cov

Documentation
~~~~~~~~~~~~~

Run serving documents with live-reloading.

.. code-block:: shell

    make serve-docs

.. _pdm: https://github.com/pdm-project/pdm
.. _pre-commit: https://pre-commit.com/
.. _nox: https://nox.thea.codes/en/stable/

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

.. |Build Status| image:: https://github.com/linw1995/jsonpath/workflows/Lint&Test/badge.svg
    :target: https://github.com/linw1995/jsonpath/actions?query=workflow%3ALint%26Test

.. |codecov| image:: https://codecov.io/gh/linw1995/jsonpath/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/linw1995/jsonpath

.. |PDM managed| image:: https://img.shields.io/badge/pdm-managed-blueviolet
    :target: https://pdm.fming.dev
