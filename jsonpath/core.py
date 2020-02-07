# Standard Library
import functools
import json
import weakref

from abc import abstractmethod
from contextvars import ContextVar
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)
from weakref import ReferenceType


var_root: ContextVar[Any] = ContextVar("root")
T_SELF_VALUE = Union[Tuple[int, Any], Tuple[str, Any]]
var_self: ContextVar[T_SELF_VALUE] = ContextVar("self")
var_finding: ContextVar[bool] = ContextVar("finding", default=False)

T = TypeVar("T", bound="Expr")


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


class JSONPathUndefinedFunctionError(JSONPathError):
    pass


class JSONPathFindError(JSONPathError):
    pass


def _dfs_find(
    expr: Optional["Expr"], elements: List[Any], rv: List[Any]
) -> None:
    """
    use DFS to find all target elements.
    the next expr finds in the result found by the current expr.
    """
    if expr is None:
        rv.extend(elements)
    else:
        for element in elements:
            try:
                _dfs_find(
                    expr.get_next(), expr.find(element), rv,
                )
            except JSONPathFindError:
                pass


class ExprMeta(type):
    _classes: Dict[str, "ExprMeta"] = {}

    def __new__(
        metacls, name: str, bases: Tuple[type], attr_dict: Dict[str, Any]
    ) -> "ExprMeta":

        if "find" not in attr_dict:
            cls = super().__new__(metacls, name, bases, attr_dict)
            cls = cast(ExprMeta, cls)
            metacls._classes[name] = cls
            return cls

        actual_find = attr_dict["find"]

        @functools.wraps(actual_find)
        def find(self: "Expr", element: Any) -> List[Any]:
            if var_finding.get():
                # the chained expr in the finding process
                try:
                    return actual_find(self, element)
                except JSONPathFindError:
                    if self.ref_begin is None:
                        raise

                    return []

            # the chained expr begins to find
            begin = self.get_begin()

            rv: List[Any] = []
            token_root = None
            try:
                var_root.get()
            except LookupError:
                # set the root element when the chained expr begins to find.
                # the partial exprs of the nested expr
                # can execute find method many times
                # but only the first times finding can set the root element.
                token_root = var_root.set(element)

            token_finding = var_finding.set(True)
            try:
                _dfs_find(begin, [element], rv)
                return rv
            finally:
                var_finding.reset(token_finding)
                if token_root:
                    var_root.reset(token_root)

        attr_dict["find"] = find
        cls = super().__new__(metacls, name, bases, attr_dict)
        cls = cast(ExprMeta, cls)
        metacls._classes[name] = cls
        return cls


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
        expr: Optional[Expr] = self.get_begin()
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

    def get_begin(self) -> "Expr":
        if self.ref_begin is None:
            # the unchained expr's ref_begin is None
            return self
        else:
            begin = self.ref_begin()
            assert begin, "the chained expr must have a beginning expr"
            return begin

    def get_next(self) -> Optional["Expr"]:
        return self.ref_right() if self.ref_right else None

    def chain(self, next_expr: T) -> T:
        if self.ref_begin is None:
            # the unchained expr become the first expr in chain
            self.ref_begin = weakref.ref(self)

        next_expr.ref_begin = self.ref_begin
        # it return next expr,
        # so need to keep the current expr's ref into next expr's left.
        # keeping the next expr's weak ref into current expr's ref_right
        # helps to find target elements in sequential.
        next_expr.left = self
        self.ref_right = weakref.ref(next_expr)
        return next_expr

    def __getattr__(self, name: str) -> Callable[..., "Expr"]:
        """
        create expr in a serial of chain class creations like Root().Name("*").
        """
        if name not in Expr._classes:
            raise AttributeError

        cls = Expr._classes[name]

        def cls_(*args: Any, **kwargs: Any) -> Expr:
            expr = cls(*args, **kwargs)
            return self.chain(next_expr=expr)

        return cls_

    def __lt__(self, value: Any) -> "Expr":
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


class Root(Expr):
    def _get_partial_expression(self) -> str:
        return "$"

    def find(self, element: Any) -> List[Any]:
        return [var_root.get()]


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
            return self._filtering_find(element)

        raise JSONPathFindError

    def _filtering_find(self, element: Any) -> List[Any]:
        assert isinstance(self.idx, Expr)
        filtered_items = []
        items: Union[Iterable[Tuple[int, Any]], Iterable[Tuple[str, Any]]]
        if isinstance(element, list):
            items = enumerate(element)
        elif isinstance(element, dict):
            items = element.items()
        else:
            raise JSONPathFindError

        for item in items:
            # save the current item into var_self for Self()
            token_self = var_self.set(item)
            # set var_finding False to
            # start new finding process for the nested expr: self.idx
            token_finding = var_finding.set(False)
            _, value = item
            try:
                rv = self.idx.find(value)
                if rv and rv[0]:
                    filtered_items.append(value)
            finally:
                var_finding.reset(token_finding)
                var_self.reset(token_self)
        return filtered_items


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
        assert isinstance(
            expr, Expr
        ), '"expr" parameter must be an instance of the "Expr" class.'
        self._expr = expr

    def _get_partial_expression(self) -> str:
        return f"({self._expr!s})"

    def find(self, element: Any) -> List[Any]:
        # set var_finding False to
        # start new finding process for the nested expr: self.expr
        token = var_finding.set(False)
        try:
            return [self._expr.find(element)]
        finally:
            var_finding.reset(token)


def _recursive_find(expr: Expr, element: Any, rv: List[Any]) -> None:
    """
    recursive find in every node.
    """
    try:
        find_rv = expr.find(element)
        rv.extend(find_rv)
    except JSONPathFindError:
        pass
    if isinstance(element, list):
        for item in element:
            _recursive_find(expr, item, rv)
    elif isinstance(element, dict):
        for item in element.values():
            _recursive_find(expr, item, rv)


class Search(Expr):
    def __init__(self, expr: Expr) -> None:
        super().__init__()
        assert isinstance(
            expr, Expr
        ), '"expr" parameter must be an instance of the "Expr" class.'
        self._expr = expr

    def _get_partial_expression(self) -> str:
        return f"..{self._expr!s}"

    def find(self, element: Any) -> List[Any]:
        rv: List[Any] = []
        if isinstance(self._expr, Array) and isinstance(self._expr.idx, Expr):
            # filtering find needs to begin on the current element
            _recursive_find(self._expr, [element], rv)
        else:
            _recursive_find(self._expr, element, rv)
        return rv


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
            return json.dumps(self.target)

    def get_target_value(self) -> Any:
        if isinstance(self.target, Expr):
            try:
                # set var_finding False to
                # start new finding process for the nested expr: self.target
                token = var_finding.set(False)
                # multiple exprs begins on self-value in filtering find,
                # except the self.target expr starts with root-value.
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


def _get_expression(target: Any) -> str:
    if isinstance(target, Expr):
        return target.get_expression()
    else:
        return json.dumps(target)


class Function(Expr):
    def __init__(self, *args: Any) -> None:
        super().__init__()
        self.args = args

    @abstractmethod
    def find(self, element: Any) -> List[Any]:
        raise NotImplementedError


class Key(Function):
    def __init__(self, *args: List[Any]) -> None:
        super().__init__(*args)
        assert not self.args

    def _get_partial_expression(self) -> str:
        return "key()"

    def find(self, element: Any) -> List[Union[int, str]]:
        # Key.find only executed in the predicate.
        # So Array.find being executed first that set the var_self
        key, _ = var_self.get()
        return [key]


class Contains(Function):
    def __init__(self, expr: Expr, target: Any, *args: List[Any]) -> None:
        super().__init__(expr, target, *args)
        assert isinstance(
            expr, Expr
        ), '"expr" parameter must be an instance of the "Expr" class.'
        assert not args
        self._expr = expr
        self._target = target

    def _get_partial_expression(self) -> str:
        args_list = (
            f"{_get_expression(self._expr)}, {_get_expression(self._target)}"
        )
        return f"contains({args_list})"

    def find(self, element: Any) -> List[bool]:
        rv = self._expr.find(element)
        if not rv:
            return []
        root_arg = rv[0]
        target_arg = self._target
        if isinstance(target_arg, Expr):
            # set var_finding False to
            # start new finding process for the nested expr: target_arg
            token = var_finding.set(False)
            try:
                rv = self._target.find(element)
            finally:
                var_finding.reset(token)

            if not rv:
                return []

            # use the first value of results as target
            target_arg = rv[0]

        return [target_arg in root_arg]


class Not(Function):
    def __init__(self, expr: Expr, *args: List[Any]) -> None:
        super().__init__(expr, *args)
        assert not args
        assert isinstance(
            expr, Expr
        ), '"expr" parameter must be an instance of the "Expr" class.'
        self._expr = expr

    def _get_partial_expression(self) -> str:
        return f"not({self._expr!s})"

    def find(self, element: Any) -> List[bool]:
        # set var_finding False to
        # start new finding process for the nested expr: target
        token = var_finding.set(False)
        try:
            rv = self._expr.find(element)
        finally:
            var_finding.reset(token)

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
