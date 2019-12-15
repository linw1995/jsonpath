# Standard Library
import weakref

from abc import abstractmethod
from contextvars import ContextVar
from typing import Any, Dict, List, Optional, Tuple, Iterable, Union, Callable
from weakref import ReferenceType


class JSONPathError(Exception):
    pass


class JSONPathSyntaxError(JSONPathError, SyntaxError):
    def __init__(self, expr: str):
        self.expr = expr
        super().__init__(str(self))

    def __str__(self) -> str:
        return f"{self.expr!r} is not a valid JSONPath expression."

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expr!r})"


class JSONPathFindError(JSONPathError):
    pass


class ExprMeta(type):
    _exprs: Dict[str, "ExprMeta"] = {}

    def __init__(cls, name: str, bases: Tuple[type], attr_dict: Dict[str, Any]):
        super().__init__(name, bases, attr_dict)
        cls._exprs[name] = cls

        actual_find = cls.find

        def begin_to_find(self: "Expr", element: Any) -> List[Any]:
            if var_finding.get():
                try:
                    return actual_find(self, element)
                except JSONPathFindError:
                    if self.ref_begin is None:
                        raise

                    return []

            expr: Optional[Expr]
            if self.ref_begin is None:
                expr = self
            else:
                expr = self.ref_begin()

            assert expr

            rv: List[Any] = []
            token_root = None
            try:
                var_root.get()
            except LookupError:
                token_root = var_root.set(element)

            token_finding = var_finding.set(True)
            try:
                dfs_find(expr, [element], rv)
                return rv
            finally:
                var_finding.reset(token_finding)
                if token_root:
                    var_root.reset(token_root)

        cls.find = begin_to_find


class Expr(metaclass=ExprMeta):
    def __init__(self) -> None:
        self.left: Optional[Expr] = None
        self.ref_right: Optional[ReferenceType[Expr]] = None
        self.ref_begin: Optional[ReferenceType[Expr]] = None

    def __repr__(self) -> str:
        return f"JSONPath({str(self)!r})"

    def __str__(self) -> str:
        return self.get_expression()

    def get_expression(self) -> str:
        expr: Optional[Expr]
        if self.ref_begin is None:
            expr = self
        else:
            expr = self.ref_begin()

        parts: List[str] = []
        while expr:
            part = expr._get_partial_expression()
            if isinstance(expr, (Array, Search, Compare)):
                if parts:
                    parts[-1] += part
                else:
                    parts.append(part)
            else:
                parts.append(part)

            if expr.ref_right:
                expr = expr.ref_right()
            else:
                expr = None

        return ".".join(parts)

    @abstractmethod
    def _get_partial_expression(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def find(self, element: Any) -> List[Any]:
        raise NotImplementedError

    def __getattr__(
        self, name: str
    ) -> Callable[..., "Expr"]:
        if name not in Expr._exprs:
            raise AttributeError

        expr_cls = Expr._exprs[name]

        def _expr_cls(*args: Any, **kwargs: Any) -> Expr:
            expr = expr_cls(*args, **kwargs)
            chain(pre=self, current=expr)
            return expr

        return _expr_cls

    def __lt__(self, value: Any) -> 'Expr':
        return self.LessThan(value)

    def __le__(self, value: Any) -> "Expr":
        return self.LessEqual(value)

    def __eq__(self, value: Any) -> "Expr":  # type: ignore
        return self.Equal(value)

    def __ge__(self, value: Any) -> "Expr":
        return self.GreaterEqual(value)

    def __gt__(self, value: Any) -> "Expr":
        return self.GreaterThan(value)

    def __ne__(self, value: Any) -> "Expr":  # type: ignore
        return self.NotEqual(value)


var_root: ContextVar[Any] = ContextVar("root")
var_self: ContextVar[Any] = ContextVar("self")
var_finding: ContextVar[bool] = ContextVar("finding", default=False)


def chain(pre: Expr, current: Expr) -> None:
    if pre.ref_begin is None:
        pre.ref_begin = weakref.ref(pre)

    current.ref_begin = pre.ref_begin
    current.left = pre
    pre.ref_right = weakref.ref(current)


def dfs_find(expr: Optional[Expr], elements: List[Any], rv: List[Any]) -> None:
    if expr is None:
        rv.extend(elements)
    else:
        if isinstance(elements, dict):
            elements = elements.values()

        for element in elements:
            try:
                dfs_find(
                    expr.ref_right() if expr.ref_right else None,
                    expr.find(element),
                    rv,
                )
            except JSONPathFindError:
                pass


class Root(Expr):
    def _get_partial_expression(self) -> str:
        return "$"

    def find(self, element: Any) -> List[Any]:
        return [var_root.get(element)]


class Name(Expr):
    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__()
        self.name = name

    def _get_partial_expression(self) -> str:
        if self.name is None:
            return "*"

        return self.name

    def find(self, element: Any) -> List[Any]:
        if not isinstance(element, dict):
            raise JSONPathFindError

        if self.name is None:
            return list(element.values())

        if self.name not in element:
            raise JSONPathFindError

        return [element[self.name]]


class Array(Expr):
    def __init__(
        self, idx: Optional[Union[int, "Slice", "Compare", Expr]] = None
    ) -> None:
        super().__init__()
        self.idx = idx

    def _get_partial_expression(self) -> str:
        if self.idx is None:
            return "[*]"
        else:
            return f"[{self.idx!s}]"

    def find(self, element: Any) -> List[Any]:
        if self.idx is None and isinstance(element, list):
            return element
        elif (
            isinstance(self.idx, int)
            and isinstance(element, list)
            and self.idx < len(element)
        ):
            return [element[self.idx]]
        elif isinstance(self.idx, Slice):
            return self.idx.find(element)
        elif isinstance(self.idx, Expr):
            filtered_items = []
            items: Union[Iterable[Tuple[int, Any]], Iterable[Tuple[str, Any]]]
            if isinstance(element, list):
                items = enumerate(element)
            elif isinstance(element, dict):
                items = element.items()
            else:
                raise JSONPathFindError

            for item in items:
                token_self = var_self.set(item)
                token_finding = var_finding.set(False)
                _, value = item
                try:
                    rv = self.idx.find(value)
                    if any(rv):
                        filtered_items.append(value)
                except JSONPathFindError:
                    pass
                finally:
                    var_finding.reset(token_finding)
                    var_self.reset(token_self)
            return filtered_items

        raise JSONPathFindError


class Slice(Expr):
    def __init__(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        step: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.start = start
        self.end = end
        self.step = step

    def _get_partial_expression(self) -> str:
        parts = []
        if self.start:
            parts.append(str(self.start))
        else:
            parts.append("")

        if self.end:
            parts.append(str(self.end))
        else:
            parts.append("")

        if self.step:
            parts.append(str(self.step))

        return ":".join(parts)

    def find(self, element: List[Any]) -> Any:
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

        raise JSONPathFindError


class Brace(Expr):
    def __init__(self, expr: Expr) -> None:
        super().__init__()
        self.expr = expr

    def _get_partial_expression(self) -> str:
        return f"({self.expr!s})"

    def find(self, element: Any) -> List[Any]:
        if isinstance(self.expr, Expr):
            token = var_finding.set(False)
            try:
                return [self.expr.find(element)]
            finally:
                var_finding.reset(token)

        raise JSONPathFindError


def recusive_find(expr: Expr, element: Any, rv: List[Any]) -> None:
    try:
        find_rv = expr.find(element)
        rv.extend(find_rv)
    except JSONPathFindError:
        pass
    if isinstance(element, list):
        for item in element:
            recusive_find(expr, item, rv)
    elif isinstance(element, dict):
        for item in element.values():
            recusive_find(expr, item, rv)


class Search(Expr):
    def __init__(self, expr: Any) -> None:
        super().__init__()
        self.expr = expr

    def _get_partial_expression(self) -> str:
        return f"..{self.expr!s}"

    def find(self, element: Any) -> List[Any]:
        if isinstance(self.expr, (Name, Array)):
            rv: List[Any] = []
            if isinstance(self.expr, Array) and isinstance(self.expr.idx, Expr):
                recusive_find(self.expr, [element], rv)
            else:
                recusive_find(self.expr, element, rv)
            return rv

        raise RuntimeError


class Self(Expr):
    def _get_partial_expression(self) -> str:
        return "@"

    def find(self, element: Any) -> List[Any]:
        try:
            _, value = var_self.get()
            return [value]
        except LookupError:
            return [element]


class Compare(Expr):
    def __init__(self, target: Any) -> None:
        super().__init__()
        self.target = target

    def _get_target_expression(self) -> str:
        if isinstance(self.target, Expr):
            return self.target.get_expression()
        else:
            return repr(self.target)

    def get_target_value(self) -> Any:
        if isinstance(self.target, Expr):
            try:
                token = var_finding.set(False)
                _, value = var_self.get()
                rv = self.target.find(value)
                if not rv:
                    raise JSONPathFindError

                return rv[0]
            finally:
                var_finding.reset(token)

        else:
            return self.target


class LessThan(Compare):
    def _get_partial_expression(self) -> str:
        return f" < {self._get_target_expression()}"

    def find(self, element: Any) -> List[bool]:
        return [element < self.get_target_value()]


class LessEqual(Compare):
    def _get_partial_expression(self) -> str:
        return f" <= {self._get_target_expression()}"

    def find(self, element: Any) -> List[bool]:
        return [element <= self.get_target_value()]


class Equal(Compare):
    def _get_partial_expression(self) -> str:
        return f" = {self._get_target_expression()}"

    def find(self, element: Any) -> List[bool]:
        return [element == self.get_target_value()]


class GreaterEqual(Compare):
    def _get_partial_expression(self) -> str:
        return f" >= {self._get_target_expression()}"

    def find(self, element: Any) -> List[bool]:
        return [element >= self.get_target_value()]


class GreaterThan(Compare):
    def _get_partial_expression(self) -> str:
        return f" > {self._get_target_expression()}"

    def find(self, element: Any) -> List[bool]:
        return [element > self.get_target_value()]


class NotEqual(Compare):
    def _get_partial_expression(self) -> str:
        return f" != {self._get_target_expression()}"

    def find(self, element: Any) -> List[bool]:
        return [element != self.get_target_value()]


class And(Compare):
    def _get_partial_expression(self) -> str:
        return f" and {self._get_target_expression()}"

    def find(self, element: Any) -> List[bool]:
        return [element and self.get_target_value()]


class Or(Compare):
    def _get_partial_expression(self) -> str:
        return f" or {self._get_target_expression()}"

    def find(self, element: Any) -> List[bool]:
        return [element or self.get_target_value()]


class Function(Expr):
    def __init__(self, *args: Any) -> None:
        super().__init__()
        self.args = args

    @abstractmethod
    def find(self, element: Any) -> List[Any]:
        raise NotImplementedError


class Key(Function):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        assert not self.args

    def _get_partial_expression(self) -> str:
        return "key()"

    def find(self, element: Any) -> List[str]:
        try:
            key, _ = var_self.get()
            return [key]
        except LookupError:
            return []


class Contains(Function):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        assert len(self.args) == 2

    def _get_partial_expression(self) -> str:
        def arg_expression(arg: Any) -> str:
            if isinstance(arg, Expr):
                return arg.get_expression()
            else:
                return repr(arg)

        args_list = (
            f"{arg_expression(self.args[0])}, {arg_expression(self.args[1])}"
        )
        return f"contains({args_list})"

    def find(self, element: Any) -> List[bool]:
        root_arg, target_arg = self.args
        if isinstance(root_arg, Expr):
            rv = root_arg.find(element)
            if not rv:
                return []
            root_arg = rv[0]
        if isinstance(target_arg, Expr):
            token = var_finding.set(False)
            try:
                rv = target_arg.find(element)
            finally:
                var_finding.reset(token)

            if not rv:
                return []

            target_arg = rv[0]

        return [target_arg in root_arg]


class Not(Function):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        assert len(self.args) == 1

    def _get_partial_expression(self) -> str:
        target = self.args[0]
        if isinstance(target, Expr):
            target_expression = target.get_expression()
        else:
            target_expression = repr(target)

        return f"not({target_expression})"

    def find(self, element: Any) -> List[bool]:
        target = self.args[0]
        if isinstance(target, Expr):
            token = var_finding.set(False)
            try:
                rv = target.find(element)
            finally:
                var_finding.reset(token)
        else:
            rv = [target]

        return [not v for v in rv]


__all__ = (
    "Contains",
    "Expr",
    "ExprMeta",
    "Name",
    "Root",
    "Array",
    "Slice",
    "Search",
    "Self",
    "Brace",
    "chain",
    "recusive_find",
    "Compare",
    "LessThan",
    "LessEqual",
    "Equal",
    "GreaterEqual",
    "GreaterThan",
    "NotEqual",
    "Not",
    "Key",
)
