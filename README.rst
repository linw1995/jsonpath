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

v0.4.0
~~~~~~

- 9f8f039 New:Add Command-line interface support


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
