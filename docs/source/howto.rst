=====
HowTo
=====

Check specific key in dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    >>> from jsonpath import parse
    >>> expr = parse('$[contains(@, "a")]')
    >>> expr.find([{"a": 0}, {"a": 1}, {}, {"b": 1}])
    [{'a': 0}, {'a': 1}]
