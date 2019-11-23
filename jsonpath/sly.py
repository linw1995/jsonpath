# Third Party Library
from sly import Lexer, Parser
from sly.yacc import YaccProduction

# Local Folder
from .core import (
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
    NotEqual,
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
    }
    literals = {"$", ".", "*", "[", "]", ":", "(", ")", "@", ","}
    ignore = " \t"

    TRUE = "true"
    FALSE = "false"
    NULL = "null"
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
    tokens = JSONPathLexer.tokens

    precedence = [("left", "DOUBLEDOT"), ("left", "DOT")]

    @_("expr DOUBLEDOT expr")  # noqa: F8
    def expr(self, p: YaccProduction):  # noqa: F8
        search = Search(p[2])
        chain(pre=p[0], current=search)
        return search

    @_("expr DOUBLEDOT '[' integer ']'")  # noqa: F8
    @_("expr DOUBLEDOT '[' slice ']'")  # noqa: F8
    @_("expr DOUBLEDOT '[' STAR ']'")  # noqa: F8
    @_("expr DOUBLEDOT '[' comparison ']'")  # noqa: F8
    @_("expr DOUBLEDOT '[' expr ']'")  # noqa: F8
    def expr(self, p: YaccProduction):  # noqa: F8
        if isinstance(p[3], (Expr, int)):
            arr = Array(p[3])
        elif p[3] == "*":
            arr = Array()
        else:
            assert 0

        search = Search(arr)
        chain(pre=p[0], current=search)
        return search

    @_("expr DOT expr")  # noqa: F8
    def expr(self, p: YaccProduction):  # noqa: F8
        chain(pre=p[0], current=p[2])
        return p[2]

    @_("expr '[' integer ']'")  # noqa: F8
    @_("expr '[' slice ']'")  # noqa: F8
    @_("expr '[' STAR ']'")  # noqa: F8
    @_("expr '[' comparison ']'")  # noqa: F8
    @_("expr '[' expr ']'")  # noqa: F8
    def expr(self, p: YaccProduction):  # noqa: F8
        if isinstance(p[2], (Expr, int)):
            rv = Array(p[2])
        elif p[2] == "*":
            rv = Array()
        else:
            assert 0

        chain(pre=p[0], current=rv)
        return rv

    @_("float")  # noqa: F8
    @_("integer")  # noqa: F8
    def number(self, p: YaccProduction):
        return p[0]

    @_("false")  # noqa: F8
    @_("true")  # noqa: F8
    @_("null")  # noqa: F8
    @_("number")  # noqa: F8
    @_("string")  # noqa: F8
    @_("expr")  # noqa: F8
    def expr_or_value(self, p: YaccProduction):
        return p[0]

    @_("expr LT expr_or_value")  # noqa: F8
    @_("expr GT expr_or_value")  # noqa: F8
    @_("expr LE expr_or_value")  # noqa: F8
    @_("expr GE expr_or_value")  # noqa: F8
    @_("expr NE expr_or_value")  # noqa: F8
    @_("expr EQ expr_or_value")  # noqa: F8
    def comparison(self, p: YaccProduction):  # noqa: F8
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

    @_("INT")  # noqa: F8
    def integer(self, p: YaccProduction):
        return int(p[0])

    @_("FLOAT")  # noqa: F8
    def float(self, p: YaccProduction):
        return float(p[0])

    @_("TRUE")  # noqa: F8
    def true(self, p: YaccProduction):
        return True

    @_("FALSE")  # noqa: F8
    def false(self, p: YaccProduction):
        return False

    @_("NULL")  # noqa: F8
    def null(self, p: YaccProduction):
        return None

    @_("")  # noqa: F8
    def empty(self, p: YaccProduction):
        return None

    @_("empty")  # noqa: F8
    @_("integer")  # noqa: F8
    def maybe_integer(self, p: YaccProduction):
        return p[0]

    @_("maybe_integer COLON maybe_integer")  # noqa: F8
    @_("maybe_integer COLON maybe_integer COLON maybe_integer")  # noqa: F8
    def slice(self, p: YaccProduction):
        if len(p) == 3:
            return Slice(p[0], p[2])
        elif len(p) == 5:
            return Slice(p[0], p[2], p[4])

    @_("'(' expr ')'")  # noqa: F8
    def expr(self, p: YaccProduction):  # noqa: F8
        return Brace(p.expr)

    @_("ROOT")  # noqa: F8
    def expr(self, p: YaccProduction):  # noqa: F8
        return Root()

    @_("STAR")  # noqa: F8
    def expr(self, p: YaccProduction):  # noqa: F8
        return Name()

    @_("AT")  # noqa: F8
    def expr(self, p: YaccProduction):  # noqa: F8
        return Self()

    @_("string")  # noqa: F8
    @_("ID")  # noqa: F8
    def expr(self, p: YaccProduction):  # noqa: F8
        return Name(p[0])

    @_("STRING")  # noqa: F8
    def string(self, p: YaccProduction):
        return p[0][1:-1]

    @_("")  # noqa: F8
    def expr_list(self, p):  # noqa: F8
        return []

    @_("expr")  # noqa: F8
    def expr_list(self, p):  # noqa: F8
        return [p.expr]

    @_("expr_list ',' expr_or_value")  # noqa: F8
    def expr_list(self, p):  # noqa: F8
        return p.expr_list + [p.expr_or_value]

    @_("ID '(' expr_list ')'")  # noqa: F8
    def expr(self, p: YaccProduction):  # noqa: F8
        if p.ID == "key":
            return Key(*p.expr_list)
        elif p.ID == "contains":
            return Contains(*p.expr_list)
        else:
            raise SyntaxError(f"Function {p.ID} not exists")

    def error(self, t):
        raise JSONPathSyntaxError


__all__ = ("JSONPathLexer", "JSONPathParser")
