# Third Party Library
from sly import Lexer, Parser
from sly.yacc import YaccProduction

# Local Folder
from .core import Array, Name, Root


class JSONPathLexer(Lexer):
    tokens = {"ID", "DOT", "STAR", "INT", "ROOT"}
    literals = {"$", ".", "*", "[", "]"}

    ID = r"[a-zA-Z_][a-zA-Z0-9_\-]*"
    DOT = r"\."
    STAR = r"\*"
    INT = r"-?\d+"
    ROOT = r"\$"


class JSONPathParser(Parser):
    tokens = JSONPathLexer.tokens

    precedence = [("left", "DOT")]

    @_("expr DOT expr")  # noqa: F8
    def expr(self, p: YaccProduction):
        p[2].left = p[0]
        return p[2]

    @_("expr '[' idx ']'")  # noqa: F8
    def expr(self, p: YaccProduction):  # noqa: F8
        rv = Array(p[2])
        rv.left = p[0]
        return rv

    @_("ROOT")  # noqa: F8
    def expr(self, p: YaccProduction):  # noqa: F8
        return Root()

    @_("STAR")  # noqa: F8
    def expr(self, p: YaccProduction):  # noqa: F8
        return Name()

    @_("ID")  # noqa: F8
    def expr(self, p: YaccProduction):  # noqa: F8
        return Name(p.ID)

    @_("INT")  # noqa: F8
    def idx(self, p: YaccProduction):
        return int(p[0])


__all__ = ("JSONPathLexer", "JSONPathParser")
