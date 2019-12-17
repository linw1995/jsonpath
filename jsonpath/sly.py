# Standard Library
from contextvars import ContextVar
from typing import Any, Callable, Dict, List, NoReturn, Tuple, Union

# Third Party Library
from sly import Lexer, Parser
from sly.lex import Token
from sly.yacc import YaccProduction
from typing_extensions import Literal

# Local Folder
from .core import (
    And,
    Array,
    Brace,
    Compare,
    Contains,
    Equal,
    Expr,
    Function,
    GreaterEqual,
    GreaterThan,
    JSONPathSyntaxError,
    Key,
    LessEqual,
    LessThan,
    Name,
    Not,
    NotEqual,
    Or,
    Root,
    Search,
    Self,
    Slice,
)


LiteralTrue = Literal[True]
LiteralFalse = Literal[False]


class JSONPathLexer(Lexer):
    tokens = {
        "STRING",
        "TRUE",
        "FALSE",
        "NULL",
        "ID",
        "FLOAT",
        "DOT",
        "STAR",
        "INT",
        "ROOT",
        "COLON",
        "DOUBLEDOT",
        "AT",
        "LT",
        "LE",
        "EQ",
        "GE",
        "GT",
        "NE",
        "AND",
        "OR",
    }
    literals = {"$", ".", "*", "[", "]", ":", "(", ")", "@", ","}
    ignore = " \t"

    TRUE = "true"
    FALSE = "false"
    NULL = "null"
    AND = "and"
    OR = "or"
    ID = r"[a-zA-Z_][a-zA-Z0-9_\-]*"
    FLOAT = r"-?\d+\.\d+"
    DOUBLEDOT = r"\.\."
    DOT = r"\."
    STAR = r"\*"
    INT = r"-?\d+"
    ROOT = r"\$"
    COLON = r":"
    AT = r"@"
    NE = r"!="
    GE = r">="
    LE = r"<="
    EQ = r"="
    LT = r"<"
    GT = r">"

    STRING = "|".join(
        [
            r"""`([^`\\]|\\.)*?`""",
            r"""'([^'\\]|\\.)*?'""",
            r'''"([^"\\]|\\.)*?"''',
        ]
    )


class JSONPathParser(Parser):
    _built = False

    @classmethod
    def _build(
        cls,
        definitions: List[
            Tuple[str, Callable[["JSONPathParser", YaccProduction], Any]]
        ],
    ) -> None:
        pass

    @classmethod
    def build(cls) -> None:
        if cls._built:
            return

        delattr(cls, "_build")
        super()._build(reversed(list(cls.rules.items())))
        cls._built = True

    rules: Dict[str, Callable[["JSONPathParser", YaccProduction], Any]] = {}

    @classmethod
    def rule(
        cls, *rules: str, name: str = None
    ) -> Callable[
        [Callable[["JSONPathParser", YaccProduction], Any]],
        Callable[["JSONPathParser", YaccProduction], Any],
    ]:
        assert rules

        def wrapper(
            func: Callable[[JSONPathParser, YaccProduction], Any]
        ) -> Callable[[JSONPathParser, YaccProduction], Any]:
            nonlocal name
            if name is None:
                name = func.__name__

            func.__name__ = name
            func.rules = rules  # type: ignore
            if name in cls.rules:
                func.next_func = cls.rules[name]  # type: ignore

            cls.rules[name] = func
            return func

        return wrapper

    tokens = JSONPathLexer.tokens

    precedence = [
        ("left", "NE", "GE", "LE", "EQ", "LT", "GT"),
        ("left", "AND", "OR"),
        ("left", "DOUBLEDOT", "DOT"),
    ]

    start = "expr"

    def error(self, t: Token) -> NoReturn:
        expr = var_expr.get()
        raise JSONPathSyntaxError(expr)


@JSONPathParser.rule("INT")
def integer(parser: JSONPathParser, p: YaccProduction) -> int:
    return int(p[0])


@JSONPathParser.rule("")
def empty(parser: JSONPathParser, p: YaccProduction) -> None:
    return None


@JSONPathParser.rule("empty", "integer")
def empty_or_integer(
    parser: JSONPathParser, p: YaccProduction
) -> Union[None, int]:
    return p[0]


@JSONPathParser.rule(
    "empty_or_integer COLON empty_or_integer",
    "empty_or_integer COLON empty_or_integer COLON empty_or_integer",
)
def slice(parser: JSONPathParser, p: YaccProduction) -> Slice:
    rv: Slice
    if len(p) == 3:
        rv = Slice(p[0], p[2])
    elif len(p) == 5:
        rv = Slice(p[0], p[2], p[4])

    return rv


@JSONPathParser.rule("FLOAT", name="float")
def float_(parser: JSONPathParser, p: YaccProduction) -> float:
    return float(p[0])


@JSONPathParser.rule("float", "integer")
def number(parser: JSONPathParser, p: YaccProduction) -> Union[int, float]:
    return p[0]


@JSONPathParser.rule("TRUE")
def true(parser: JSONPathParser, p: YaccProduction) -> LiteralTrue:
    return True


@JSONPathParser.rule("FALSE")
def false(parser: JSONPathParser, p: YaccProduction) -> LiteralFalse:
    return False


@JSONPathParser.rule("NULL")
def null(parser: JSONPathParser, p: YaccProduction) -> None:
    return None


@JSONPathParser.rule("STRING")
def string(parser: JSONPathParser, p: YaccProduction) -> str:
    return p[0][1:-1]


@JSONPathParser.rule("number", "true", "false", "null", "string")
def value(
    parser: JSONPathParser, p: YaccProduction
) -> Union[int, float, bool, None]:
    return p[0]


@JSONPathParser.rule("ID", "string", name="expr")
def name_expr(parser: JSONPathParser, p: YaccProduction) -> Name:
    return Name(p[0])


@JSONPathParser.rule("ROOT", name="expr")
def root_expr(parser: JSONPathParser, p: YaccProduction) -> Root:
    return Root()


@JSONPathParser.rule("STAR", name="expr")
def star_expr(parser: JSONPathParser, p: YaccProduction) -> Name:
    return Name()


@JSONPathParser.rule("AT", name="expr")
def self_expr(parser: JSONPathParser, p: YaccProduction) -> Self:
    return Self()


@JSONPathParser.rule("expr", "value")
def expr_or_value(
    parser: JSONPathParser, p: YaccProduction
) -> Union[Expr, int, float, bool, None]:
    return p[0]


@JSONPathParser.rule(
    "expr LT expr_or_value",
    "expr GT expr_or_value",
    "expr LE expr_or_value",
    "expr GE expr_or_value",
    "expr NE expr_or_value",
    "expr EQ expr_or_value",
)
def comparison(parser: JSONPathParser, p: YaccProduction) -> Compare:
    rv: Compare
    if p[1] == "<":
        rv = LessThan(p[2])
    elif p[1] == "<=":
        rv = LessEqual(p[2])
    elif p[1] == "=":
        rv = Equal(p[2])
    elif p[1] == ">=":
        rv = GreaterEqual(p[2])
    elif p[1] == ">":
        rv = GreaterThan(p[2])
    elif p[1] == "!=":
        rv = NotEqual(p[2])

    return p[0].chain(rv)


@JSONPathParser.rule("comparison", "expr_or_value")
def comparison_or_expr_or_value(
    parser: JSONPathParser, p: YaccProduction
) -> Union[Expr, int, float, bool, None]:
    return p[0]


@JSONPathParser.rule(
    "comparison_or_expr_or_value AND comparison_or_expr_or_value",
    "comparison_or_expr_or_value OR comparison_or_expr_or_value",
    name="comparison",
)
def boolean_op_expr(parser: JSONPathParser, p: YaccProduction) -> Compare:
    rv: Compare
    if p[1] == "and":
        rv = And(p[2])
    elif p[1] == "or":
        rv = Or(p[2])

    return p[0].chain(rv)


@JSONPathParser.rule(
    "expr DOUBLEDOT '[' integer ']'",
    "expr DOUBLEDOT '[' slice ']'",
    "expr DOUBLEDOT '[' STAR ']'",
    "expr DOUBLEDOT '[' comparison ']'",
    "expr DOUBLEDOT '[' expr ']'",
    name="expr",
)
def conditional_search_expr(
    parser: JSONPathParser, p: YaccProduction
) -> Search:
    if isinstance(p[3], (Expr, int)):
        arr = Array(p[3])
    elif p[3] == "*":
        arr = Array()
    else:
        assert 0

    search = Search(arr)
    return p[0].chain(search)


@JSONPathParser.rule("expr DOUBLEDOT expr", name="expr")
def search_expr(parser: JSONPathParser, p: YaccProduction) -> Search:
    search = Search(p[2])
    return p[0].chain(search)


@JSONPathParser.rule(
    "expr '[' integer ']'",
    "expr '[' slice ']'",
    "expr '[' STAR ']'",
    "expr '[' comparison ']'",
    "expr '[' expr ']'",
    name="expr",
)
def conditional_expr(parser: JSONPathParser, p: YaccProduction) -> Array:
    if isinstance(p[2], (Expr, int)):
        rv = Array(p[2])
    elif p[2] == "*":
        rv = Array()
    else:
        assert 0

    return p[0].chain(rv)


@JSONPathParser.rule("expr DOT expr", name="expr")
def chained_expr(parser: JSONPathParser, p: YaccProduction) -> Expr:
    return p[0].chain(p[2])


@JSONPathParser.rule("'(' expr ')'", "'(' comparison ')'", name="expr")
def braced_expr(parser: JSONPathParser, p: YaccProduction) -> Brace:
    return Brace(p[1])


@JSONPathParser.rule("empty", name="args")
def no_args(
    parser: JSONPathParser, p: YaccProduction
) -> List[Union[Expr, int, float, bool, None]]:
    return []


@JSONPathParser.rule("comparison_or_expr_or_value", name="args")
def arg(
    parser: JSONPathParser, p: YaccProduction
) -> List[Union[Expr, int, float, bool, None]]:
    return [p.comparison_or_expr_or_value]


@JSONPathParser.rule("args ',' comparison_or_expr_or_value")
def args(
    parser: JSONPathParser, p: YaccProduction
) -> List[Union[Expr, int, float, bool, None]]:
    return p.args + [p.comparison_or_expr_or_value]


@JSONPathParser.rule("ID '(' args ')'", name="expr")
def function(parser: JSONPathParser, p: YaccProduction) -> Function:
    if p.ID == "key":
        return Key(*p.args)
    elif p.ID == "contains":
        return Contains(*p.args)
    elif p.ID == "not":
        return Not(*p.args)
    else:
        raise SyntaxError(f"Function {p.ID} not exists")


var_expr: ContextVar[str] = ContextVar("expr")


def parse(expr: str) -> Expr:
    JSONPathParser.build()
    var_expr.set(expr)
    return JSONPathParser().parse(JSONPathLexer().tokenize(expr))


__all__ = ("JSONPathLexer", "JSONPathParser", "parse")
