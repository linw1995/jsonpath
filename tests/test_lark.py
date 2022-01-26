# Standard Library
import json
import logging

from contextlib import nullcontext

# Third Party Library
import _pytest.python_api
import pytest

# First Party Library
from jsonpath.core import JSONPathSyntaxError, JSONPathUndefinedFunctionError
from jsonpath.lark import Lark, UnexpectedToken
from jsonpath.parser import parse, parser

# Local Folder
from .utils import assert_find

does_not_raise = nullcontext()


@pytest.mark.xfail(raises=NameError)
def test_no_conflict(caplog):
    with caplog.at_level(logging.DEBUG, logger="lark"):
        Lark.open(
            "jsonpath/grammar.lark",
            parser="lalr",
            debug=True,
            keep_all_tokens=True,
        )

    assert len(caplog.records) == 0


def ids(x):
    if x is does_not_raise:
        return "does not raise"
    elif isinstance(x, _pytest.python_api.RaisesContext):
        return f"raise {x.expected_exception.__name__}"
    else:
        return json.dumps(x)


def test_parser_parse(expression, raises_what):
    with raises_what:
        tree = parser.parse(expression)
        logging.debug(f"parser.parse {expression!r} result: {tree.pretty()}")


parser_parse_not_raises_exception_testcases = [
    "a.b",
    "a.b.c",
    "a.b.c.d",
    "a[:3]",
    "a[:-3]",
    "a[-1]",
    "a[0]",
    "a[*]",
    "$[@]",
    "$[$]",
    "a[b]",
    "a[b][c]",
    "(a[b])[c]",
    "a.*",
    "a.'*'",
    "a.'b'",
    "a..[b]",
    "a..[0]",
    "a..[:3]",
    "$.goods[contains(@.category, $.targetCategory)]",
    "$.goods[@.category]",
    "$.goods[@.price > 10]",
    "$.goods[@.price >= 10 and @.price < 20]",
    "$.goods[@.price >= 10 and @.price < 20 and @.category = $.targetCategory]",
    "$.goods" "[(@.price >= 10 and @.price < 20) or @.category = $.targetCategory]",
    "$.goods[@.'price' > 10]",
    '$."price"',
    "$.'price'",
    "$.`price`",
    "($.*[*])[0]",
    "($.*)[0]",
    "$..boo.bar",
    "$[(type='book' or type='video') and price > 100]",
    "(a.b).b",
    "a[(b[0] or b[1]) and (b.c)[0].d]",
    "a[((b[0]).c or b[1]) and d]",
    "$[c and (a or b)]",
    "$[c and ((a or b) or c)]",
    "((a.b).c).d",
    "((a.b)).c",
    "$[((a.b).c)]",
    "$[1 < @]",
    "$[@ and 1]",
    "$[(a and b)]",
    "$[((a and b)) or c]",
    "$[not((a and b)) or c]",
]

parser_parse_raises_exception_testcases = [
    "array[]",
    "$*",
    "[*]",
    '"abc"',
    "'abc'",
    "`abc`",
]
parser_parse_testcases = [
    *(
        (expression, does_not_raise)
        for expression in parser_parse_not_raises_exception_testcases
    ),
    *(
        (expression, pytest.raises(UnexpectedToken))
        for expression in parser_parse_raises_exception_testcases
    ),
]

pytest.mark.parametrize(
    "expression, raises_what",
    parser_parse_testcases,
    ids=ids,
)(test_parser_parse)


def test_parse_check_and_extract(expression, data, expect):
    jp = parse(expression)
    logging.debug(f"parse {expression!r} result: {jp}")
    assert jp.get_expression() == expression
    assert_find(jp, data, expect)


pytest.mark.parametrize(
    "expression, data, expect",
    [
        ("boo", {"boo": 1}, [1]),
        ("boo.bar", {"boo": {"bar": 1}}, [1]),
        ("boo.bar.boo", {"boo": {"bar": {"boo": 1}}}, [1]),
        ("$.*", {"boo": 1, "bar": 2}, [1, 2]),
        ("$.'*'", {"boo": 1, "bar": 2, "*": 3}, [3]),
        ("boo.*", {"boo": {"boo": 1, "bar": 2}}, [1, 2]),
        ("boo.*.boo", {"boo": {"boo": {"boo": 1}, "bar": {"boo": 2}}}, [1, 2]),
        ("boo.*.boo", {"boo": {"boo": {"boo": 1}, "bar": {"bar": 2}}}, [1]),
        ("boo.*.boo", {"boo": {"boo": {"boo": 1}, "bar": 1}}, [1]),
        ("$[0]", [1, 2], [1]),
        ("$[1]", [1, 2], [2]),
        ("$[2]", [1, 2], []),
        ("$[-1]", [], []),
        ("$[-1]", [1], [1]),
        ("boo[0]", {"boo": [1, 2]}, [1]),
        ("$[*]", [1, 2], [1, 2]),
        ("$[:1]", [1, 2], [1]),
        ("$[1:2]", [1, 2], [2]),
        ("$[:]", [1, 2], [1, 2]),
        ("$[:-1]", [1, 2, 3], [1, 2]),
        ("$[::2]", [1, 2, 3], [1, 3]),
        ("$[a:]", [1, 2], []),
        ("$[:a]", [1, 2], []),
        ("$[::a]", [1, 2], []),
        ("$.data[$.a:]", {"data": [1, 2]}, []),
        ("$.data[$.a:]", {"data": [1, 2], "a": 1}, [2]),
        ("$.data[a:]", {"data": [1, 2], "a": 1}, [2]),
        ("$.data[a:b]", {"data": [1, 2], "a": 1, "b": 1}, []),
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
        (
            "$..boo.bar",
            {"boo": {"boo": {"boo": 1}, "bar": {"boo": 2}}},
            [{"boo": 2}],
        ),
        ("$..[0]", {"boo": [{"boo": [1]}]}, [{"boo": [1]}, 1]),
        ("$..[*]", {"boo": [{"boo": [1, 2]}]}, [{"boo": [1, 2]}, 1, 2]),
        (
            "$..[:-1:2]",
            {"boo": [{"boo": [1, 2, 3, 4, 5]}, 1]},
            [{"boo": [1, 2, 3, 4, 5]}, 1, 3],
        ),
        ("@", "abc", ["abc"]),
        ("$[@ < 10]", [0, 10, 12, 1, 3], [0, 1, 3]),
        ("($[@ < 10])[@ > 1]", [0, 10, 12, 1, 3], [3]),
        (
            "$[@.price > 100]",
            [{"price": 100}, {"price": 200}],
            [{"price": 200}],
        ),
        (
            "$[price > 100]",
            [{"price": 100}, {"price": 200}],
            [{"price": 200}],
        ),
        (
            "$[price >= 100]",
            [{"price": 100}, {"price": 200}],
            [{"price": 100}, {"price": 200}],
        ),
        (
            "$[price < 100]",
            [{"price": 100}, {"price": 200}],
            [],
        ),
        (
            "$[price <= 100]",
            [{"price": 100}, {"price": 200}],
            [{"price": 100}],
        ),
        (
            "$[price = 100]",
            [{"price": 100}, {"price": 200}],
            [{"price": 100}],
        ),
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
            [{"price": 100}],
        ),
        ("$[price]", [{"price": 100}, {}], [{"price": 100}]),
        ("$[price]", {"bookA": {"price": 100}, "bookB": {}}, [{"price": 100}]),
        (
            "$..[result]",
            [{"result": {"result": "result"}}],
            [{"result": {"result": "result"}}, {"result": "result"}],
        ),
        (
            "$..[result]",
            {"result": {"result": "result"}},
            [{"result": {"result": "result"}}, {"result": "result"}],
        ),
        (
            "$..[price > 100]",
            {
                "price": 200,
                "charpter": [{"price": 100}, {"price": 200}, {"price": 300}],
            },
            [
                {
                    "price": 200,
                    "charpter": [{"price": 100}, {"price": 200}, {"price": 300}],
                },
                {"price": 200},
                {"price": 300},
            ],
        ),
        ("$[price > 100.5]", [{"price": 100}, {"price": 200}], [{"price": 200}]),
        ("$[on = null]", [{"on": None}, {"on": False}], [{"on": None}]),
        ("$[on = true]", [{"on": True}, {"on": False}], [{"on": True}]),
        ("$[on = false]", [{"on": True}, {"on": False}], [{"on": False}]),
        (
            "$.systems[on = $.on]",
            {"systems": [{"on": True}, {"on": False}], "on": False},
            [{"on": False}],
        ),
        (
            "$.systems[on = $.notexists]",
            {"systems": [{"on": True}, {"on": False}], "on": False},
            [],
        ),
        ('$[name = "john"]', [{"name": "jack"}, {"name": "john"}], [{"name": "john"}]),
        ('$[name = "john"]', [{"name": "jack"}, {"name": "john"}], [{"name": "john"}]),
        ("$[*].name", [{"name": "jack"}, {"name": "john"}], ["jack", "john"]),
        (
            '$[key() = "bookA"]',
            {"bookA": {"price": 100}, "bookB": {}},
            [{"price": 100}],
        ),
        ("$[key() = 0]", [{"price": 100}, {"price": 200}], [{"price": 100}]),
        (
            '$[contains(key(), "book")]',
            {"bookA": {"price": 100}, "bookB": {"price": 200}, "pictureA": {}},
            [{"price": 100}, {"price": 200}],
        ),
        (
            '$[contains(@.category, "book")]',
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
            "$[contains(@.category, $.targetCategory)]",
            [{"price": 100, "category": "Comic book"}],
            [],
        ),
        (
            '$[type = "book" and price > 100]',
            [
                {"type": "book", "price": 100},
                {"type": "book", "price": 200},
                {"type": "video", "price": 200},
            ],
            [{"type": "book", "price": 200}],
        ),
        (
            '$[(type = "book" or type = "video") and price > 100]',
            [
                {"type": "book", "price": 100},
                {"type": "book", "price": 200},
                {"type": "video", "price": 200},
            ],
            [{"type": "book", "price": 200}, {"type": "video", "price": 200}],
        ),
        (
            '$[type = "book" or type = "video"]',
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
            '$[type = "book" or type = "video" or type = "audio"]',
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
            '$[contains(@, "is")]',
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
        (
            "$[not(is)]",
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
                {"is": 0},
                {"is": False},
                {"is": []},
                {"is": None},
                {"is": {}},
                {"is": 0.0},
            ],
        ),
        (
            '$[not(contains(@, "is"))]',
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
            [{}],
        ),
        (
            '$[not(type = "book" or type = "video")]',
            [
                {"type": "book", "price": 100},
                {"type": "video", "price": 200},
                {"type": "audio", "price": 100},
            ],
            [{"type": "audio", "price": 100}],
        ),
        ("$[100 = price]", [{"price": 100}, {"price": 0}], [{"price": 100}]),
        (
            "$.data[$.start:$.stop:$.step]",
            {"data": [0, 1, 2, 3, 4], "start": 1, "stop": 10, "step": 2},
            [1, 3],
        ),
        (
            "$.data[$.start:$.stop:$.step]",
            {"data": [0, 1, 2, 3, 4], "start": "not integer", "stop": 10, "step": 2},
            [],
        ),
        (
            "$.data[$.start:$.stop:$.step]",
            {"data": [0, 1, 2, 3, 4], "start": 1, "stop": "not integer", "step": 2},
            [],
        ),
        (
            "$.data[$.start:$.stop:$.step]",
            {"data": [0, 1, 2, 3, 4], "start": 1, "stop": 10, "step": "not integer"},
            [],
        ),
    ],
    ids=ids,
)(test_parse_check_and_extract)


def test_parse_and_extract(expression, data, expect):
    jp = parse(expression)
    logging.debug(f"parse {expression!r} result: {jp}")
    assert_find(jp, data, expect)


pytest.mark.parametrize(
    "expression, data, expect",
    [
        ('$."*"', {"*": ""}, [""]),
        ("$.'*'", {"*": ""}, [""]),
        ("$.`*`", {"*": ""}, [""]),
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
    ],
    ids=ids,
)(test_parse_and_extract)


@pytest.mark.parametrize("expression", parser_parse_raises_exception_testcases)
def test_syntax_error(expression):
    with pytest.raises(JSONPathSyntaxError):
        parse(expression)


def test_undefined_function_error():
    with pytest.raises(JSONPathUndefinedFunctionError):
        parse("$[abc(@)]")
