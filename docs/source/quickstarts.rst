===========
Quickstarts
===========


Installation
~~~~~~~~~~~~

.. include:: installation.rst
    :start-line: 4


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

Or use the :py:mod:`jsonpath.core` module to extract it.

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
