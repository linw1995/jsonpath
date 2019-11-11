# Standard Library
import weakref

from abc import abstractmethod
from contextvars import ContextVar
from typing import Any, Dict, Optional, Tuple
from weakref import ReferenceType


var_root = ContextVar("root")
var_finding = ContextVar("finding", default=False)


class FindError(Exception):
    pass


def chain(pre, current):
    if pre.ref_begin is None:
        pre.ref_begin = weakref.ref(pre)

    current.ref_begin = pre.ref_begin
    current.left = pre
    pre.ref_right = weakref.ref(current)


class ExprMeta(type):
    _exprs = {}

    def __init__(cls, name: str, bases: Tuple[type], attr_dict: Dict[str, Any]):
        super().__init__(name, bases, attr_dict)
        cls._exprs[name] = cls

        actual_find = cls.find

        def recusive_find(expr, elements, rv):
            if expr is None:
                rv.extend(elements)
            else:
                for element in elements:
                    try:
                        recusive_find(
                            expr.ref_right() if expr.ref_right else None,
                            expr.find(element),
                            rv,
                        )
                    except FindError:
                        pass

        def begin_to_find(self, element):
            if var_finding.get():
                try:
                    return actual_find(self, element)
                except FindError:
                    if self.ref_begin is None:
                        raise

                    return []

            if self.ref_begin is None:
                expr = self
            else:
                expr = self.ref_begin()

            rv = []
            token_root = var_root.set(element)
            token_finding = var_finding.set(True)
            try:
                recusive_find(expr, [element], rv)
                return rv
            finally:
                var_finding.reset(token_finding)
                var_root.reset(token_root)

        cls.find = begin_to_find


class Expr(metaclass=ExprMeta):
    def __init__(self) -> None:
        self.left: Optional[Expr] = None
        self.ref_right: Optional[ReferenceType[Expr]] = None
        self.ref_begin: Optional[ReferenceType[Expr]] = None

    @abstractmethod
    def find(self, element):
        raise NotImplementedError

    def __getattr__(self, name):
        if name not in Expr._exprs:
            raise AttributeError

        expr_cls = Expr._exprs[name]

        def _expr_cls(*args, **kwargs):
            expr = expr_cls(*args, **kwargs)
            chain(pre=self, current=expr)
            return expr

        return _expr_cls


class Root(Expr):
    def find(self, element):
        return [var_root.get(element)]


class Name(Expr):
    def __init__(self, name=None):
        super().__init__()
        self.name = name

    def find(self, element):
        if not isinstance(element, dict):
            raise FindError()

        if self.name is None:
            return list(element.values())

        if self.name not in element:
            raise FindError()

        return [element[self.name]]


class Array(Expr):
    def __init__(self, idx):
        super().__init__()
        self.idx = idx

    def find(self, element):
        if isinstance(self.idx, int):
            if isinstance(element, list) and self.idx < len(element):
                return [element[self.idx]]
        elif isinstance(self.idx, Slice):
            return self.idx.find(element)

        raise FindError()


class Slice(Expr):
    def __init__(self, start=None, end=None, step=1):
        super().__init__()
        self.start = start
        self.end = end
        self.step = step

    def find(self, element):
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

        raise FindError()


class Brace(Expr):
    def __init__(self, expr: Expr):
        super().__init__()
        self.expr = expr

    def find(self, element):
        if isinstance(self.expr, Expr):
            token = var_finding.set(False)
            try:
                return [self.expr.find(element)]
            finally:
                var_finding.reset(token)

        raise FindError()


__all__ = ("Expr", "ExprMeta", "Name", "Root", "Array", "Slice")
