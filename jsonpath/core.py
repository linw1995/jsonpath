# Standard Library
from typing import Any, Dict, Optional, Tuple


class ExprMeta(type):
    _exprs = {}

    def __init__(cls, name: str, bases: Tuple[type], attr_dict: Dict[str, Any]):
        super().__init__(name, bases, attr_dict)
        cls._exprs[name] = cls


class Expr(metaclass=ExprMeta):
    def __init__(self) -> None:
        self.left: Optional[Expr] = None

    def find(self, element: Any) -> Any:
        if self.left is not None:
            element = self.left.find(element)

        return element

    def __getattr__(self, name):
        if name not in Expr._exprs:
            raise AttributeError

        expr_cls = Expr._exprs[name]

        def chain(*args, **kwargs):
            expr = expr_cls(*args, **kwargs)
            expr.left = self
            return expr

        return chain


class Root(Expr):
    def find(self, element):
        element = super().find(element)
        return element


class Name(Expr):
    def __init__(self, name=None):
        super().__init__()
        self.name = name

    def find(self, element):
        element = super().find(element)
        if self.name is None:
            return list(element.values())

        if isinstance(element, list):
            return [
                row[self.name]
                for row in element
                if isinstance(row, dict) and self.name in row
            ]

        return element[self.name]


class Array(Expr):
    def __init__(self, idx):
        self.idx = idx

    def find(self, element):
        element = super().find(element)
        if isinstance(element, list) and self.idx < len(element):
            return element[self.idx]

        return []


__all__ = ("Expr", "ExprMeta", "Name", "Root", "Array")
