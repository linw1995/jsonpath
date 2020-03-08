"""
===============
:mod:`jsonpath`
===============
A selector expression for extracting data from JSON.
"""
# Local Folder
from .core import (
    Array,
    Brace,
    Compare,
    Contains,
    Equal,
    Expr,
    ExprMeta,
    GreaterEqual,
    GreaterThan,
    JSONPathError,
    JSONPathFindError,
    JSONPathSyntaxError,
    Key,
    LessEqual,
    LessThan,
    Name,
    Not,
    NotEqual,
    Root,
    Search,
    Self,
    Slice,
)
from .parser import parse


__all__ = (
    "Array",
    "Contains",
    "Expr",
    "Slice",
    "ExprMeta",
    "Root",
    "Name",
    "parse",
    "Search",
    "Self",
    "Brace",
    "Compare",
    "LessThan",
    "LessEqual",
    "Equal",
    "GreaterEqual",
    "GreaterThan",
    "NotEqual",
    "Not",
    "Key",
    "JSONPathError",
    "JSONPathSyntaxError",
    "JSONPathFindError",
)
