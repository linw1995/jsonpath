# Standard Library
import reprlib

# Third Party Library
import pytest

# First Party Library
from jsonpath.core import Name, Root, Slice


@pytest.mark.parametrize(
    "name,data,expect",
    [("boo", {"boo": 1}, [1]), (None, {"boo": 1, "bar": 2}, [1, 2])],
    ids=reprlib.repr,
)
def test_name_find(name, data, expect):
    assert Name(name).find(data) == expect


@pytest.mark.parametrize(
    "names,data,expect",
    [
        (["boo", "bar"], {"boo": {"bar": 1}}, [1]),
        (["boo", "bar", "boo"], {"boo": {"bar": {"boo": 1}}}, [1]),
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


@pytest.mark.parametrize(
    "start,end,step,data,expect",
    [
        (0, 1, 1, [1, 2], [1]),
        (0, None, 1, [1, 2], [1, 2]),
        (None, -1, 1, [1, 2, 3], [1, 2]),
        (None, None, 2, [1, 2, 3], [1, 3]),
    ],
    ids=reprlib.repr,
)
def test_slice_in_array(start, end, step, data, expect):
    jp = Root().Array(Slice(start, end, step))
    assert jp.find(data) == expect


@pytest.mark.parametrize(
    "start,end,step,data,expect",
    [
        (0, 1, 1, [1, 2], [1]),
        (0, None, 1, [1, 2], [1, 2]),
        (None, -1, 1, [1, 2, 3], [1, 2]),
        (None, None, 2, [1, 2, 3], [1, 3]),
    ],
    ids=reprlib.repr,
)
def test_slice(start, end, step, data, expect):
    jp = Root().Slice(start, end, step)
    assert jp.find(data) == expect
