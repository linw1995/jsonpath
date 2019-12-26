========
JSONPATH
========

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

.. code-block:: python3

    import json

    from jsonpath import parse, Root, Contains, Self

    data = json.loads(
        """
        {
            "goods": [
                {"price": 100, "category": "Comic book"},
                {"price": 200, "category": "magazine"},
                {"price": 200, "no category": ""}
            ],
            "targetCategory": "book"
        }
    """
    )
    expect = [{"price": 100, "category": "Comic book"}]

    assert parse("$.goods[contains(@.category, $.targetCategory)]").find(data) == expect

    assert (
        Root()
        .Name("goods")
        .Array(Contains(Self().Name("category"), Root().Name("targetCategory")))
        .find(data)
        == expect
    )
