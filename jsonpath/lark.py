try:
    from lark import Transformer, v_args, Lark
    from lark.exceptions import UnexpectedToken, VisitError

except ImportError:
    from .lark_parser import (
        Transformer,
        v_args,
        Lark,
        UnexpectedToken,
        VisitError,
        DATA,
        Lark_StandAlone,
    )


__all__ = (
    "Transformer",
    "v_args",
    "Lark",
    "Lark_StandAlone",
    "DATA",
    "UnexpectedToken",
    "VisitError",
)
