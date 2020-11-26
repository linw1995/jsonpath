# Standard Library
import reprlib

# Third Party Library
import pytest

# First Party Library
from jsonpath.core import (
    Array,
    Brace,
    Contains,
    Key,
    Name,
    Not,
    Predicate,
    Root,
    Self,
    Slice,
    Value,
    var_parent,
)

# Local Folder
from .utils import assert_find


@pytest.mark.parametrize(
    "name,data,expect",
    [("boo", {"boo": 1}, [1]), (None, {"boo": 1, "bar": 2}, [1, 2])],
    ids=reprlib.repr,
)
def test_name_find(name, data, expect):
    assert_find(Name(name), data, expect)


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
        jp = jp.Name(name)  # type: ignore

    assert_find(jp, data, expect)


@pytest.mark.parametrize("data", [[], "abc", {"a": "b"}, 1, 1.0], ids=reprlib.repr)
def test_root(data):
    assert_find(Root(), data, [data])


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
    assert_find(jp, data, expect)


@pytest.mark.parametrize(
    "expr,data,expect",
    [
        (Root().Search(Array(0)), {"boo": [{"boo": [1]}]}, [{"boo": [1]}, 1]),
        (
            Root().Search(Array()),
            {"boo": [{"boo": [1, 2]}]},
            [{"boo": [1, 2]}, 1, 2],
        ),
        (
            Root().Search(Array(Slice(None, -1, 2))),
            {"boo": [{"boo": [1, 2, 3, 4, 5]}, 1]},
            [{"boo": [1, 2, 3, 4, 5]}, 1, 3],
        ),
    ],
)
def test_search(expr, data, expect):
    assert_find(expr, data, expect)


@pytest.mark.parametrize(
    "start,end,step,data,expect",
    [
        (0, 1, 1, [1, 2], [1]),
        (1, 1, 1, [1, 2], []),
        (0, 10, 1, [1, 2, 3], [1, 2, 3]),
        (0, 3, 2, [1, 2, 3], [1, 3]),
        (0, None, 1, [1, 2], [1, 2]),
        (None, -1, 1, [1, 2, 3], [1, 2]),
        (None, None, 2, [1, 2, 3], [1, 3]),
    ],
    ids=reprlib.repr,
)
def test_slice(start, end, step, data, expect):
    jp = Root().Slice(start, end, step)
    assert_find(jp, data, expect)


@pytest.mark.parametrize(
    "expr,data,expect",
    [
        (
            Root().Predicate(Name("price") > 100),
            [{"price": 100}, {"price": 200}],
            [{"price": 200}],
        ),
        (
            Root().Predicate(Name("price").GreaterThan(100)),
            [{"price": 100}, {"price": 200}],
            [{"price": 200}],
        ),
        (
            Root().Predicate(Name("price") >= 100),
            [{"price": 100}, {"price": 200}],
            [{"price": 100}, {"price": 200}],
        ),
        (
            Root().Predicate(Name("price").GreaterEqual(100)),
            [{"price": 100}, {"price": 200}],
            [{"price": 100}, {"price": 200}],
        ),
        (
            Root().Predicate(Name("price") < 100),
            [{"price": 100}, {"price": 200}],
            [],
        ),
        (
            Root().Predicate(Name("price").LessThan(100)),
            [{"price": 100}, {"price": 200}],
            [],
        ),
        (
            Root().Predicate(Name("price") <= 100),
            [{"price": 100}, {"price": 200}],
            [{"price": 100}],
        ),
        (
            Root().Predicate(Name("price").LessEqual(100)),
            [{"price": 100}, {"price": 200}],
            [{"price": 100}],
        ),
        (
            Root().Predicate(Name("price") == 100),
            [{"price": 100}, {"price": 200}],
            [{"price": 100}],
        ),
        (
            Root().Predicate(Name("price").Equal(100)),
            [{"price": 100}, {"price": 200}],
            [{"price": 100}],
        ),
        (
            Root().Predicate(Name("price") != 100),
            [{"price": 100}, {"price": 200}],
            [{"price": 200}],
        ),
        (
            Root().Predicate(Name("price").NotEqual(100)),
            [{"price": 100}, {"price": 200}],
            [{"price": 200}],
        ),
    ],
    ids=reprlib.repr,
)
def test_comparison(expr, data, expect):
    assert_find(expr, data, expect)


@pytest.mark.parametrize(
    "expr,data,expect",
    [
        (
            Root().Search(Predicate(Name("price") > 100)),
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
        (
            Root().Search(Predicate(Name("price") >= 100)),
            {
                "price": 200,
                "charpter": [{"price": 100}, {"price": 200}, {"price": 300}],
            },
            [
                {
                    "price": 200,
                    "charpter": [{"price": 100}, {"price": 200}, {"price": 300}],
                },
                {"price": 100},
                {"price": 200},
                {"price": 300},
            ],
        ),
        (
            Root().Search(Predicate(Name("price") <= 100)),
            {
                "price": 200,
                "charpter": [{"price": 100}, {"price": 200}, {"price": 300}],
            },
            [{"price": 100}],
        ),
        (
            Root().Search(Predicate(Name("price") < 100)),
            {
                "price": 200,
                "charpter": [{"price": 100}, {"price": 200}, {"price": 300}],
            },
            [],
        ),
        (
            Root().Search(Predicate(Name("price") == 100)),
            {
                "price": 200,
                "charpter": [{"price": 100}, {"price": 200}, {"price": 300}],
            },
            [{"price": 100}],
        ),
        (
            Root().Search(Predicate(Name("price") != 100)),
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
    ],
    ids=reprlib.repr,
)
def test_comparison_in_search(expr, data, expect):
    assert_find(expr, data, expect)


@pytest.mark.parametrize(
    "expr,data,expect",
    [
        (Root().Name(), {"boo": [1, 2, 3], "bar": [2, 3, 4]}, [[1, 2, 3], [2, 3, 4]]),
        (Root().Name().Array(0), {"boo": [1, 2, 3], "bar": [2, 3, 4]}, [1, 2]),
        (
            Root().Name().Array(),
            {"boo": [1, 2, 3], "bar": [2, 3, 4]},
            [1, 2, 3, 2, 3, 4],
        ),
        (
            Brace(Root().Name()).Array(0),
            {"boo": [1, 2, 3], "bar": [2, 3, 4]},
            [[1, 2, 3]],
        ),
        (
            Brace(Root().Name().Array()).Array(0),
            {"boo": [1, 2, 3], "bar": [2, 3, 4]},
            [1],
        ),
        (
            Root().Predicate(Contains(Self(), "is")),
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
            Root().Predicate(Contains(Self(), Value("is"))),
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
    ids=reprlib.repr,
)
def test_others(expr, data, expect):
    assert_find(expr, data, expect)


def test_get_expression(expr, expect):
    assert expr.get_expression() == expect


test_get_expression = pytest.mark.parametrize(
    "expr,expect",
    [
        (Name("abc").Name("def"), "abc.def"),
        (Name("abc").Name().Name("ghi"), "abc.*.ghi"),
        (Name("abc").Array(1), "abc[1]"),
        (Name("abc").Array(), "abc[*]"),
        (Name("abc").Array(Slice()), "abc[:]"),
        (Name("abc").Array(Slice(1)), "abc[1:]"),
        (Name("abc").Array(Slice(None, 1)), "abc[:1]"),
        (Name("abc").Array(Slice(1, -1)), "abc[1:-1]"),
        (Name("abc").Array(Slice(1, -1, 2)), "abc[1:-1:2]"),
        (Name("abc").Array(Slice(step=2)), "abc[::2]"),
        (Root().Array(), "$[*]"),
        (Root().Name(), "$.*"),
        (Brace(Root().Name("abc")).Array(1), "($.abc)[1]"),
        (Root().Search(Name("abc")).Array(1), "$..abc[1]"),
        (Root().Search(Array()), "$..[*]"),
        (Root().Predicate(Name("abc").GreaterThan(1)), "$[abc > 1]"),
        (Root().Predicate(Name("abc").GreaterEqual(1)), "$[abc >= 1]"),
        (Root().Predicate(Name("abc").Equal(1)), "$[abc = 1]"),
        (Root().Predicate(Name("abc").NotEqual(1)), "$[abc != 1]"),
        (Root().Predicate(Name("abc").LessEqual(1)), "$[abc <= 1]"),
        (Root().Predicate(Name("abc").LessThan(1)), "$[abc < 1]"),
        (Root().Predicate(Self().Name("abc").LessThan(1)), "$[@.abc < 1]"),
        (
            Name("list").Predicate(Name("abc") < Root().Name("abc")),
            "list[abc < $.abc]",
        ),
        (
            Name("list").Predicate(Name("abc").And(Root().Name("abc"))),
            "list[abc and $.abc]",
        ),
        (
            Name("list").Predicate(Name("abc").Or(Root().Name("abc"))),
            "list[abc or $.abc]",
        ),
        (
            Name("list").Predicate(Name("abc").Or(Root().Name("abc")).Or(Name("def"))),
            "list[abc or $.abc or def]",
        ),
        (Root().Predicate(Name("name") == "name"), '$[name = "name"]'),
        (Root().Predicate(Key() == "bookA"), '$[key() = "bookA"]'),
        (
            Root().Predicate(Contains(Key(), "book")),
            '$[contains(key(), "book")]',
        ),
        (
            Root().Predicate(Not(Contains(Key(), "book"))),
            '$[not(contains(key(), "book"))]',
        ),
        (Value(1), "1"),
        (Value(1.1), "1.1"),
        (Value("boo"), '"boo"'),
        (Value(None), "null"),
        (Value(True), "true"),
        (Value(False), "false"),
        (Value(1).LessThan(Value(2)), "1 < 2"),
    ],
    ids=reprlib.repr,
)(test_get_expression)


def test_get_parent_object():
    root = {"a": 1}

    class TestName1(Name):
        def find(self, element):
            with pytest.raises(LookupError):
                var_parent.get()

            assert element == root
            return super().find(element)

    assert TestName1("a").find(root) == [1]

    root_2 = {"a": {"b": 1}}

    class TestName2(Name):
        def find(self, element):
            assert var_parent.get() == root_2
            assert element == {"b": 1}
            return super().find(element)

    assert Name("a").chain(TestName2("b")).find(root_2) == [1]


def test_get_parent_array():
    root = [{"a": 1}, {"a": 2}]

    class TestName(Name):
        def find(self, element):
            assert var_parent.get() == root
            assert element in root
            return super().find(element)

    assert Array().chain(TestName("a")).find(root) == [1, 2]


def test_get_parent_while_searching():
    root = {"a": {"b": {"c": 1}}}

    parents = []
    history = []

    class TestName(Name):
        def find(self, element):
            parents.append(var_parent.get())
            history.append(element)
            return super().find(element)

    assert Root().Search(TestName("c")).find(root) == [1]
    assert parents == [root, root, root["a"], root["a"]["b"]]
    assert history == [root, root["a"], root["a"]["b"], 1]
