# Standard Library
from typing import Any, Iterable, List, Optional, Union

# Third Party Library
from typing_extensions import Literal

# Local Folder
from .core import (
    T_VALUE,
    And,
    Array,
    Brace,
    Compare,
    Contains,
    Equal,
    Expr,
    Function,
    GreaterEqual,
    GreaterThan,
    JSONPathUndefinedFunctionError,
    Key,
    LessEqual,
    LessThan,
    Name,
    Not,
    NotEqual,
    Or,
    Predicate,
    Root,
    Search,
    Self,
    Slice,
    Value,
)
from .lark import Token, Transformer, v_args

T_OPERATOR = Literal["<=", ">=", "<", ">", "!=", "="]
T_ARG = Union[Expr, T_VALUE]
T_NO_ARG = Iterable[Any]
T_ARGS = Union[T_NO_ARG, List[T_ARG]]


@v_args(inline=True)
class JSONPathTransformer(Transformer[Token, Expr]):
    """
    Transform JSONPath expression AST parsed by lark into an executable object.
    """

    INT = int

    def cdr(self, *args: Any) -> Any:
        return args[1]

    def true(self) -> Literal[True]:
        return True

    def false(self) -> Literal[False]:
        return False

    def null(self) -> Literal[None]:
        return None

    def NUMBER(self, number: str) -> Union[int, float]:
        if "." in number:
            return float(number)
        else:
            return int(number)

    def STRING(self, quoted_string: str) -> str:
        return quoted_string[1:-1]

    def identifier(self, string: str) -> Name:
        return Name(string)

    def STAR(self, star_: Literal["*"]) -> None:
        return None

    def self(self) -> Self:
        return Self()

    def root(self) -> Root:
        return Root()

    def value(self, value: T_VALUE) -> Value:
        return Value(value)

    def comparison_expr(
        self,
        left: Expr,
        operator: T_OPERATOR,
        right: Expr,
    ) -> Compare:
        rv: Compare
        if operator == "<":
            rv = LessThan(right)
        elif operator == "<=":
            rv = LessEqual(right)
        elif operator == "=":
            rv = Equal(right)
        elif operator == ">=":
            rv = GreaterEqual(right)
        elif operator == ">":
            rv = GreaterThan(right)
        elif operator == "!=":
            rv = NotEqual(right)
        else:
            raise AssertionError(f"Opertor {operator!r} is not supported")

        return left.chain(rv)

    def first_path(self, expr_or_str: Union[Expr, str]) -> Expr:
        if isinstance(expr_or_str, str):
            return Name(expr_or_str)
        return expr_or_str

    chain_with_identifier = cdr

    def search(self, double_dot_: Literal[".."], expr: Expr) -> Search:
        return Search(expr)

    search_with_identifier = search
    search_with_predicate = search

    def chain_with_star(self, dot_: Literal["."], star_: Literal["*"]) -> Name:
        return Name()

    def path_with_action(self, prev_path: Expr, action: Expr) -> Expr:
        return prev_path.chain(action)

    def predicate(self, expr: Union[Expr, None]) -> Union[Array, Predicate]:
        if isinstance(expr, Value):
            assert isinstance(expr.value, int)
            return Array(expr.value)
        elif isinstance(expr, Slice):
            return Array(expr)
        elif expr is None:
            # STAR token
            return Array()
        else:
            return Predicate(expr)

    def two_fields_slice(
        self,
        first_field: Optional[Expr],
        colon_1: Literal[":"],
        second_field: Optional[Expr],
    ) -> Slice:
        return Slice(start=first_field, stop=second_field)

    def three_fields_slice(
        self,
        first_field: Optional[Expr],
        colon_1: Literal[":"],
        second_field: Optional[Expr],
        colon_2: Literal[":"],
        third_field: Optional[Expr],
    ) -> Slice:
        return Slice(start=first_field, stop=second_field, step=third_field)

    def func_call(self, name: str, args: T_ARGS = tuple()) -> Function:
        if name == "key":
            return Key(*args)
        elif name == "contains":
            return Contains(*args)
        elif name == "not":
            return Not(*args)
        else:
            raise JSONPathUndefinedFunctionError(f"Function {name!r} not exists")

    def multi_args(self, args: List[T_ARG], single_arg: T_ARG) -> List[T_ARG]:
        args.append(single_arg)
        return args

    def single_arg(self, arg: T_ARG) -> List[T_ARG]:
        return [arg]

    def parenthesized_expr(self, expr: Expr) -> Brace:
        return Brace(expr)

    def and_expr(self, left_expr: Expr, and_: Literal["and"], right_expr: Expr) -> And:
        return left_expr.chain(And(right_expr))

    def or_expr(self, left_expr: Expr, or_: Literal["or"], right_expr: Expr) -> Or:
        return left_expr.chain(Or(right_expr))

    def start(self, expr: Expr) -> Expr:
        return expr
