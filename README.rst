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

Changelog
~~~~~~~~~

- 35f0960 New:Add release actions for pypi and gh-release
- ce022b6 New:Add codecov for code coverage report
- 7f4fe3c Fix:The reduce/reduce conflicts
- 258b0fa Fix:The shift/reduce conflicts
- 95f088d New:Add Github Actions for CI


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
