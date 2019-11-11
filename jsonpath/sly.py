# Third Party Library
from sly import Lexer, Parser
from sly.yacc import YaccProduction

# Local Folder
from .core import Array, Brace, Name, Root, Slice, chain


class JSONPathLexer(Lexer):
    tokens = {"ID", "DOT", "STAR", "INT", "ROOT", "COLON"}
    literals = {"$", ".", "*", "[", "]", ":", "(", ")"}

    ID = r"[a-zA-Z_][a-zA-Z0-9_\-]*"
    DOT = r"\."
    STAR = r"\*"
    INT = r"-?\d+"
    ROOT = r"\$"
    COLON = r":"


class JSONPathParser(Parser):
    tokens = JSONPathLexer.tokens

    precedence = [("left", "DOT")]

    @_("expr DOT expr")  # noqa: F8
    def expr(self, p: YaccProduction):
        chain(pre=p[0], current=p[2])
        return p[2]

    @_("expr '[' idx ']'")  # noqa: F8
    @_("expr '[' slice ']'")  # noqa: F8
    def expr(self, p: YaccProduction):  # noqa: F8
        rv = Array(p[2])
        chain(pre=p.expr, current=rv)
        return rv

    @_("INT")  # noqa: F8
    def idx(self, p: YaccProduction):
        return int(p[0])

    @_("")  # noqa: F8
    def empty(self, p: YaccProduction):
        pass

    @_("empty")  # noqa: F8
    @_("INT")  # noqa: F8
    def maybe_int(self, p: YaccProduction):
        return int(p[0]) if p[0] else None

    @_("maybe_int COLON maybe_int")  # noqa: F8
    @_("maybe_int COLON maybe_int COLON maybe_int")  # noqa: F8
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

    @_("ID")  # noqa: F8
    def expr(self, p: YaccProduction):  # noqa: F8
        return Name(p.ID)


__all__ = ("JSONPathLexer", "JSONPathParser")
