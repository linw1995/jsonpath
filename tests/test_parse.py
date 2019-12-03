# Standard Library
import json
import reprlib

# Third Party Library
import pytest

# First Party Library
from jsonpath import JSONPathSyntaxError, parse


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
            "$[@]",
            [{"price": 100}, {"isbn": ""}, {}],
            [{"price": 100}, {"isbn": ""}],
        ),
        (
            "$[@.*]",
            [{"price": 100}, {"isbn": ""}, {"isbn": "", "price": 100}],
            [{"price": 100}, {"isbn": "", "price": 100}],
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
        (
            "$[name='john']",
            [{"name": "jack"}, {"name": "john"}],
            [{"name": "john"}],
        ),
        (
            '$[name="john"]',
            [{"name": "jack"}, {"name": "john"}],
            [{"name": "john"}],
        ),
        (
            """$[name='"john"']""",
            [{"name": "jack"}, {"name": '"john"'}],
            [{"name": '"john"'}],
        ),
        (
            """$[name="'john'"]""",
            [{"name": "jack"}, {"name": "'john'"}],
            [{"name": "'john'"}],
        ),
        (
            """$[name=`john'`]""",
            [{"name": "jack"}, {"name": "john'"}],
            [{"name": "john'"}],
        ),
        (
            """$[*].'name'""",
            [{"name": "jack"}, {"name": "john"}],
            ["jack", "john"],
        ),
        (
            "$[key()='bookA']",
            {"bookA": {"price": 100}, "bookB": {}},
            [{"price": 100}],
        ),
        ("$[key()=0]", [{"price": 100}, {"price": 200}], [{"price": 100}],),
        (
            "$[contains(key(),'book')]",
            {"bookA": {"price": 100}, "bookB": {"price": 200}, "pictureA": {}},
            [{"price": 100}, {"price": 200}],
        ),
        (
            "$[contains(@.category,'book')]",
            [
                {"price": 100, "category": "Comic book"},
                {"price": 200, "category": "magazine"},
                {"price": 200, "no category": ""},
            ],
            [{"price": 100, "category": "Comic book"}],
        ),
        (
            "$.goods[contains(@.category, $.targetCategory)]",
            {
                "goods": [
                    {"price": 100, "category": "Comic book"},
                    {"price": 200, "category": "magazine"},
                    {"price": 200, "no category": ""},
                ],
                "targetCategory": "book",
            },
            [{"price": 100, "category": "Comic book"}],
        ),
        (
            "$[contains(@.category,$.targetCategory)]",
            [{"price": 100, "category": "Comic book"}],
            [],
        ),
        (
            "$[type='book' and price > 100]",
            [
                {"type": "book", "price": 100},
                {"type": "book", "price": 200},
                {"type": "video", "price": 200},
            ],
            [{"type": "book", "price": 200}],
        ),
        (
            "$[(type='book' or type='video') and price > 100]",
            [
                {"type": "book", "price": 100},
                {"type": "book", "price": 200},
                {"type": "video", "price": 200},
            ],
            [{"type": "book", "price": 200}, {"type": "video", "price": 200}],
        ),
        (
            "$[type='book' or type='video']",
            [
                {"type": "book", "price": 100},
                {"type": "book", "price": 200},
                {"type": "video", "price": 200},
                {"type": "audio", "price": 100},
            ],
            [
                {"type": "book", "price": 100},
                {"type": "book", "price": 200},
                {"type": "video", "price": 200},
            ],
        ),
        (
            "$[type='book' or type='video' or type='audio']",
            [
                {"type": "book", "price": 200},
                {"type": "video", "price": 200},
                {"type": "audio", "price": 100},
            ],
            [
                {"type": "book", "price": 200},
                {"type": "video", "price": 200},
                {"type": "audio", "price": 100},
            ],
        ),
        (
            "$[is]",
            [
                {"is": 1},
                {"is": 0},
                {"is": True},
                {"is": False},
                {"is": []},
                {"is": None},
                {"is": {}},
                {"is": "str"},
                {"is": 1.1},
                {"is": 0.0},
                {},
            ],
            [{"is": 1}, {"is": True}, {"is": "str"}, {"is": 1.1}],
        ),
        (
            "$[contains(@, 'is')]",
            [
                {"is": 1},
                {"is": 0},
                {"is": True},
                {"is": False},
                {"is": []},
                {"is": None},
                {"is": {}},
                {"is": "str"},
                {"is": 1.1},
                {"is": 0.0},
                {},
            ],
            [
                {"is": 1},
                {"is": 0},
                {"is": True},
                {"is": False},
                {"is": []},
                {"is": None},
                {"is": {}},
                {"is": "str"},
                {"is": 1.1},
                {"is": 0.0},
            ],
        ),
    ],
    ids=lambda x: reprlib.repr(json.dumps(x)),
)(test_find)


@pytest.mark.parametrize("expr", ["array[]", "$*", "[*]"])
def test_syntax_error(expr):
    with pytest.raises(JSONPathSyntaxError):
        parse(expr)
