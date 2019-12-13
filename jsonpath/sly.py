# Standard Library
from contextvars import ContextVar

# Third Party Library
from sly import Lexer, Parser
from sly.yacc import YaccProduction

# Local Folder
from .core import (
    And,
    Array,
    Brace,
    Contains,
    Equal,
    Expr,
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
    chain,
)


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
    def _build(cls, definitions):
        pass

    @classmethod
    def build(cls):
        if cls._built:
            return

        delattr(cls, "_build")
        super()._build(reversed(list(cls.rules.items())))
        cls._built = True

    rules = {}

    @classmethod
    def rule(cls, *rules, name=None):
        assert rules

        def wrapper(func):
            nonlocal name
            if name is None:
                name = func.__name__

            func.__name__ = name
            func.rules = rules
            if name in cls.rules:
                func.next_func = cls.rules[name]

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

    def error(self, t):
        expr = var_expr.get()
        raise JSONPathSyntaxError(expr)


@JSONPathParser.rule("INT")
def integer(parser: JSONPathParser, p: YaccProduction):
    return int(p[0])


@JSONPathParser.rule("")
def empty(parser: JSONPathParser, p: YaccProduction):
    return None


@JSONPathParser.rule("empty", "integer")
def empty_or_integer(parser: JSONPathParser, p: YaccProduction):
    return p[0]


@JSONPathParser.rule(
    "empty_or_integer COLON empty_or_integer",
    "empty_or_integer COLON empty_or_integer COLON empty_or_integer",
)
def slice(parser: JSONPathParser, p: YaccProduction):
    if len(p) == 3:
        return Slice(p[0], p[2])
    elif len(p) == 5:
        return Slice(p[0], p[2], p[4])


@JSONPathParser.rule("FLOAT", name="float")
def float_(parser: JSONPathParser, p: YaccProduction):
    return float(p[0])


@JSONPathParser.rule("float", "integer")
def number(parser: JSONPathParser, p: YaccProduction):
    return p[0]


@JSONPathParser.rule("TRUE")
def true(parser: JSONPathParser, p: YaccProduction):
    return True


@JSONPathParser.rule("FALSE")
def false(parser: JSONPathParser, p: YaccProduction):
    return False


@JSONPathParser.rule("NULL")
def null(parser: JSONPathParser, p: YaccProduction):
    return None


@JSONPathParser.rule("STRING")
def string(parser: JSONPathParser, p: YaccProduction):
    return p[0][1:-1]


@JSONPathParser.rule("number", "true", "false", "null", "string")
def value(parser: JSONPathParser, p: YaccProduction):
    return p[0]


@JSONPathParser.rule("ID", "string", name="expr")
def name_expr(parser: JSONPathParser, p: YaccProduction):
    return Name(p[0])


@JSONPathParser.rule("ROOT", name="expr")
def root_expr(parser: JSONPathParser, p: YaccProduction):
    return Root()


@JSONPathParser.rule("STAR", name="expr")
def star_expr(parser: JSONPathParser, p: YaccProduction):
    return Name()


@JSONPathParser.rule("AT", name="expr")
def self_expr(parser: JSONPathParser, p: YaccProduction):
    return Self()


@JSONPathParser.rule("expr", "value")
def expr_or_value(parser: JSONPathParser, p: YaccProduction):
    return p[0]


@JSONPathParser.rule(
    "expr LT expr_or_value",
    "expr GT expr_or_value",
    "expr LE expr_or_value",
    "expr GE expr_or_value",
    "expr NE expr_or_value",
    "expr EQ expr_or_value",
)
def comparison(parser: JSONPathParser, p: YaccProduction):
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

    chain(pre=p[0], current=rv)
    return rv


@JSONPathParser.rule("comparison", "expr_or_value")
def comparison_or_expr_or_value(parser: JSONPathParser, p: YaccProduction):
    return p[0]


@JSONPathParser.rule(
    "comparison_or_expr_or_value AND comparison_or_expr_or_value",
    "comparison_or_expr_or_value OR comparison_or_expr_or_value",
    name="comparison",
)
def boolean_op_expr(parser: JSONPathParser, p: YaccProduction):
    if p[1] == "and":
        rv = And(p[2])
    elif p[1] == "or":
        rv = Or(p[2])

    chain(p[0], rv)
    return rv


@JSONPathParser.rule(
    "expr DOUBLEDOT '[' integer ']'",
    "expr DOUBLEDOT '[' slice ']'",
    "expr DOUBLEDOT '[' STAR ']'",
    "expr DOUBLEDOT '[' comparison ']'",
    "expr DOUBLEDOT '[' expr ']'",
    name="expr",
)
def conditional_search_expr(parser: JSONPathParser, p: YaccProduction):
    if isinstance(p[3], (Expr, int)):
        arr = Array(p[3])
    elif p[3] == "*":
        arr = Array()
    else:
        assert 0

    search = Search(arr)
    chain(pre=p[0], current=search)
    return search


@JSONPathParser.rule("expr DOUBLEDOT expr", name="expr")
def search_expr(parser: JSONPathParser, p: YaccProduction):
    search = Search(p[2])
    chain(pre=p[0], current=search)
    return search


@JSONPathParser.rule(
    "expr '[' integer ']'",
    "expr '[' slice ']'",
    "expr '[' STAR ']'",
    "expr '[' comparison ']'",
    "expr '[' expr ']'",
    name="expr",
)
def conditional_expr(parser: JSONPathParser, p: YaccProduction):
    if isinstance(p[2], (Expr, int)):
        rv = Array(p[2])
    elif p[2] == "*":
        rv = Array()
    else:
        assert 0

    chain(pre=p[0], current=rv)
    return rv


@JSONPathParser.rule("expr DOT expr", name="expr")
def chained_expr(parser: JSONPathParser, p: YaccProduction):
    chain(pre=p[0], current=p[2])
    return p[2]


@JSONPathParser.rule("'(' expr ')'", "'(' comparison ')'", name="expr")
def braced_expr(parser: JSONPathParser, p: YaccProduction):
    return Brace(p[1])


@JSONPathParser.rule("empty", name="args")
def no_args(parser: JSONPathParser, p: YaccProduction):
    return []


@JSONPathParser.rule("comparison_or_expr_or_value", name="args")
def arg(parser: JSONPathParser, p: YaccProduction):
    return [p.comparison_or_expr_or_value]


@JSONPathParser.rule("args ',' comparison_or_expr_or_value")
def args(parser: JSONPathParser, p: YaccProduction):
    return p.args + [p.comparison_or_expr_or_value]


@JSONPathParser.rule("ID '(' args ')'", name="expr")
def function(parser: JSONPathParser, p: YaccProduction):
    if p.ID == "key":
        return Key(*p.args)
    elif p.ID == "contains":
        return Contains(*p.args)
    elif p.ID == "not":
        return Not(*p.args)
    else:
        raise SyntaxError(f"Function {p.ID} not exists")


var_expr = ContextVar("expr")


def parse(expr):
    JSONPathParser.build()
    var_expr.set(expr)
    return JSONPathParser().parse(JSONPathLexer().tokenize(expr))


__all__ = ("JSONPathLexer", "JSONPathParser", "parse")
