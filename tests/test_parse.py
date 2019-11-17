# Standard Library
import reprlib

# Third Party Library
import pytest

# First Party Library
from jsonpath import parse


def test_find(expr, data, expect):
    assert parse(expr).find(data) == expect


test_find = pytest.mark.parametrize(
    "expr,data,expect",
    [
        ("boo", {"boo": 1}, [1]),
        ("boo.bar", {"boo": {"bar": 1}}, [1]),
        ("boo.bar.boo", {"boo": {"bar": {"boo": 1}}}, [1]),
        ("$.*", {"boo": 1, "bar": 2}, [1, 2]),
        ("boo.*", {"boo": {"boo": 1, "bar": 2}}, [1, 2]),
        ("boo.*.boo", {"boo": {"boo": {"boo": 1}, "bar": {"boo": 2}}}, [1, 2]),
        ("boo.*.boo", {"boo": {"boo": {"boo": 1}, "bar": {"bar": 2}}}, [1]),
        ("boo.*.boo", {"boo": {"boo": {"boo": 1}, "bar": 1}}, [1]),
        ("$[0]", [1, 2], [1]),
        ("boo[0]", {"boo": [1, 2]}, [1]),
        ("$[*]", [1, 2], [1, 2]),
        ("$[0:1]", [1, 2], [1]),
        ("$[0:]", [1, 2], [1, 2]),
        ("$[:-1]", [1, 2, 3], [1, 2]),
        ("$[::2]", [1, 2, 3], [1, 3]),
        ("$.*[0]", {"boo": [1, 2, 3], "bar": [2, 3, 4]}, [1, 2]),
        ("$.*[*]", {"boo": [1, 2, 3], "bar": [2, 3, 4]}, [1, 2, 3, 2, 3, 4]),
        ("($.*)[0]", {"boo": [1, 2, 3], "bar": [2, 3, 4]}, [[1, 2, 3]]),
        ("($.*[*])[0]", {"boo": [1, 2, 3], "bar": [2, 3, 4]}, [1]),
        ("$.*", {"boo": [1, 2, 3], "bar": [2, 3, 4]}, [[1, 2, 3], [2, 3, 4]]),
        (
            "$..boo",
            {"boo": {"boo": {"boo": 1}, "bar": {"boo": 2}}},
            [{"boo": {"boo": 1}, "bar": {"boo": 2}}, {"boo": 1}, 1, 2],
        ),
        ("$..[0]", {"boo": [{"boo": [1]}]}, [{"boo": [1]}, 1]),
        ("$..[*]", {"boo": [{"boo": [1, 2]}]}, [{"boo": [1, 2]}, 1, 2]),
        (
            "$..[:-1:2]",
            {"boo": [{"boo": [1, 2, 3, 4, 5]}, 1]},
            [{"boo": [1, 2, 3, 4, 5]}, 1, 3],
        ),
        ("@", "abc", ["abc"]),
        (
            "$[@.price > 100]",
            [{"price": 100}, {"price": 200}],
            [{"price": 200}],
        ),
        ("$[price > 100]", [{"price": 100}, {"price": 200}], [{"price": 200}],),
        (
            "$[price >= 100]",
            [{"price": 100}, {"price": 200}],
            [{"price": 100}, {"price": 200}],
        ),
        ("$[price < 100]", [{"price": 100}, {"price": 200}], [],),
        (
            "$[price <= 100]",
            [{"price": 100}, {"price": 200}],
            [{"price": 100}],
        ),
        ("$[price = 100]", [{"price": 100}, {"price": 200}], [{"price": 100}],),
        (
            "$[price != 100]",
            [{"price": 100}, {"price": 200}],
            [{"price": 200}],
        ),
        ("$[@.price]", [{"price": 100}, {}], [{"price": 100}]),
        (
            "$[@.*]",
            [{"price": 100}, {"isbn": ""}, {}],
            [{"price": 100}, {"isbn": ""}],
        ),
        ("$[price]", [{"price": 100}, {}], [{"price": 100}]),
        ("$[price]", {"bookA": {"price": 100}, "bookB": {}}, [{"price": 100}]),
        (
            "$..[result]",
            [{"result": {"result": "result"}}],
            [{"result": {"result": "result"}}, {"result": "result"}],
        ),
        (
            "$..[price>100]",
            {
                "price": 200,
                "charpter": [{"price": 100}, {"price": 200}, {"price": 300}],
            },
            [
                {
                    "price": 200,
                    "charpter": [
                        {"price": 100},
                        {"price": 200},
                        {"price": 300},
                    ],
                },
                {"price": 200},
                {"price": 300},
            ],
        ),
        ("$[price>100.5]", [{"price": 100}, {"price": 200}], [{"price": 200}],),
        ("$[on=null]", [{"on": None}, {"on": False}], [{"on": None}],),
        ("$[on=true]", [{"on": True}, {"on": False}], [{"on": True}],),
        ("$[on=false]", [{"on": True}, {"on": False}], [{"on": False}],),
        (
            "$.systems[on=$.on]",
            {"systems": [{"on": True}, {"on": False}], "on": False},
            [{"on": False}],
        ),
        (
            "$.systems[on=$.notexists]",
            {"systems": [{"on": True}, {"on": False}], "on": False},
            [],
        ),
    ],
    ids=reprlib.repr,
)(test_find)
