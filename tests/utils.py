# Standard Library
from typing import Any, List

# Third Party Library
import pytest

# First Party Library
from jsonpath import Expr, JSONPathFindError


def assert_find(jp: Expr, data: Any, expect: List[Any]):
    if expect:
        assert expect[0] == jp.find_first(data)
    else:
        with pytest.raises(JSONPathFindError):
            jp.find_first(data)

    assert expect == jp.find(data)
