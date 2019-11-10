# Standard Library
from contextvars import ContextVar
from typing import Any, Dict, Optional, Tuple


var_root = ContextVar("root")


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
        else:
            var_root.set(element)

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
        super().find(element)
        return var_root.get()


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
        super().__init__()
        self.idx = idx

    def find(self, element):
        element = super().find(element)
        if isinstance(self.idx, int):
            if isinstance(element, list) and self.idx < len(element):
                return element[self.idx]
        elif isinstance(self.idx, Slice):
            return self.idx.find(element)

        return []


class Slice(Expr):
    def __init__(self, start=None, end=None, step=1):
        super().__init__()
        self.start = start
        self.end = end
        self.step = step

    def find(self, element):
        element = super().find(element)
        if isinstance(element, list):
            start = self.start
            end = self.end
            step = self.step
            if start is None:
                start = 0
            if end is None:
                end = len(element)
            if step is None:
                step = 1

            return element[start:end:step]

        return []


__all__ = ("Expr", "ExprMeta", "Name", "Root", "Array", "Slice")
