"""
=====================================================
:mod:`parser` -- Translate expression into executable
=====================================================
"""

# Local Folder
from .core import Expr, JSONPathSyntaxError, JSONPathUndefinedFunctionError
from .lark import UnexpectedToken, VisitError
from .transformer import JSONPathTransformer

transformer = JSONPathTransformer(visit_tokens=True)
try:
    # Local Folder
    from .lark import Lark

    parser = Lark.open_from_package(
        __name__,
        "grammar.lark",
        parser="lalr",
        maybe_placeholders=True,
    )

except NameError:
    # Local Folder
    from .lark import Lark_StandAlone

    parser = Lark_StandAlone()


def parse(expr: str) -> Expr:
    """
    Transform JSONPath expression into an executable object.

    >>> parse("$.a").find({"a": 1})
    [1]

    :param expr: JSONPath expression
    :type expr: str

    :returns: An executable object.
    :rtype: :class:`jsonpath.core.Expr`
    :raises ~jsonpath.core.JSONPathError: \
        Transform JSONPath expression error.
    """
    try:
        tree = parser.parse(expr)
    except UnexpectedToken as exc:
        raise JSONPathSyntaxError(expr) from exc

    try:
        return transformer.transform(tree)
    except VisitError as exc:
        if isinstance(exc.orig_exc, JSONPathUndefinedFunctionError):
            raise exc.orig_exc

        raise
