=========
Changelog
=========

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

.. include:: history.rst
    :start-line: 4
