# Local Folder
from .core import Array, Expr, ExprMeta, Name, Root
from .sly import JSONPathLexer, JSONPathParser


def parse(expr):
    return JSONPathParser().parse(JSONPathLexer().tokenize(expr))


__all__ = (
    "Array",
    "Expr",
    "ExprMeta",
    "Root",
    "Name",
    "JSONPathLexer",
    "JSONPathParser",
    "parse",
)
