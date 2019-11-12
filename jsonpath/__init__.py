# Local Folder
from .core import (
    Array,
    Brace,
    Expr,
    ExprMeta,
    Name,
    Root,
    Search,
    Self,
    Slice,
    chain,
    recusive_find,
)
from .sly import JSONPathLexer, JSONPathParser


def parse(expr):
    return JSONPathParser().parse(JSONPathLexer().tokenize(expr))


__all__ = (
    "Array",
    "Expr",
    "Slice",
    "ExprMeta",
    "Root",
    "Name",
    "JSONPathLexer",
    "JSONPathParser",
    "parse",
    "Search",
    "Self",
    "Brace",
    "chain",
    "recusive_find",
)
