# Standard Library
import reprlib

# Third Party Library
import pytest

# First Party Library
from jsonpath.core import Name


@pytest.mark.parametrize(
    "name,data,expect",
    [("boo", {"boo": 1}, 1), (None, {"boo": 1, "bar": 2}, [1, 2])],
    ids=reprlib.repr,
)
def test_name_find(name, data, expect):
    assert Name(name).find(data) == expect


@pytest.mark.parametrize(
    "names,data,expect",
    [
        (["boo", "bar"], {"boo": {"bar": 1}}, 1),
        (["boo", "bar", "boo"], {"boo": {"bar": {"boo": 1}}}, 1),
        (
            ["boo", None, "boo"],
            {"boo": {"boo": {"boo": 1}, "bar": {"boo": 2}}},
            [1, 2],
        ),
    ],
    ids=reprlib.repr,
)
def test_name_chain_find(names, data, expect):
    jp = Name(names[0])
    for name in names[1:]:
        jp = jp.Name(name)

    assert jp.find(data) == expect
