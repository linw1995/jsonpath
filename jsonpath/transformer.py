# Standard Library
from typing import Iterable, List, Optional, Union

# Third Party Library
from typing_extensions import Literal

# Local Folder
from .core import (
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
)
from .lark import Transformer, v_args


T_OPERATOR = Literal["<=", ">=", "<", ">", "!=", "="]
T_VALUE = Union[int, float, str, Literal[None], Literal[True], Literal[False]]
T_ARG = Union[Expr, T_VALUE]
T_NO_ARG = Iterable
T_ARGS = Union[T_NO_ARG, List[T_ARG]]


@v_args(inline=True)
class JSONPathTransformer(Transformer[Expr]):
    """
    Transform JSONPath expression AST parsed by lark-parser into an executable object.
    """

    INT = int

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

    def name(self, string: str) -> Name:
        return Name(string)

    def self(self) -> Self:
        return Self()

    def root(self) -> Root:
        return Root()

    def value(self, value: T_VALUE) -> T_VALUE:
        return value

    def comparison_expr(
        self, left: Expr, operator: T_OPERATOR, right: Union[Expr, T_VALUE]
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

        return left.chain(rv)

    def chained_path_with_star(
        self, prev_path: Expr, dot: Literal["."], star: Literal["*"]
    ) -> Name:
        return prev_path.chain(Name())

    def chained_path_with_name(
        self, prev_path: Expr, dot: Literal["."], string: str
    ) -> Name:
        return prev_path.chain(Name(string))

    def predicate(self, expr: Expr) -> Predicate:
        return Predicate(expr)

    def get_item(self, idx: int) -> Array:
        return Array(idx)

    def two_fields_slice(
        self,
        first_field: Optional[int],
        colon_1: Literal[":"],
        second_field: Optional[int],
    ) -> Slice:
        return Slice(start=first_field, stop=second_field)

    def three_fields_slice(
        self,
        first_field: Optional[int],
        colon_1: Literal[":"],
        second_field: Optional[int],
        colon_2: Literal[":"],
        third_field: Optional[int],
    ) -> Slice:
        return Slice(start=first_field, stop=second_field, step=third_field)

    def get_partial_items(self, slice_: Slice) -> Array:
        return Array(slice_)

    def get_all_items(self, star: Literal["*"]) -> Array:
        return Array()

    def get_item_from_path(self, prev_path: Expr, get_item: Array) -> Array:
        return prev_path.chain(get_item)

    def filter_from_path(self, prev_path: Expr, filter_: Array) -> Array:
        return prev_path.chain(filter_)

    def get_item_from_search(
        self, prev_path: Expr, double_dot: Literal[".."], get_item: Array
    ) -> Search:
        return prev_path.chain(Search(get_item))

    def filter_from_search(
        self, prev_path: Expr, double_dot: Literal[".."], predicate: Array
    ) -> Search:
        return prev_path.chain(Search(predicate))

    def search_with_name(
        self, prev_path: Expr, double_dot: Literal[".."], string: str
    ) -> Search:
        return prev_path.chain(Search(Name(string)))

    def funccall(self, name: str, args: T_ARGS = tuple()) -> Function:
        if name == "key":
            return Key(*args)
        elif name == "contains":
            return Contains(*args)
        elif name == "not":
            return Not(*args)
        else:
            raise JSONPathUndefinedFunctionError(
                f"Function {name!r} not exists"
            )

    def multi_args(self, args: List[T_ARG], single_arg: T_ARG) -> List[T_ARG]:
        args.append(single_arg)
        return args

    def single_arg(self, arg: T_ARG) -> List[T_ARG]:
        return [arg]

    def braced_mixed_path(self, mixed_path: Expr) -> Brace:
        return Brace(mixed_path)

    def and_mixed_expr(
        self, left_expr: Expr, and_: Literal["and"], right_expr: Expr
    ) -> And:
        return left_expr.chain(And(right_expr))

    def or_mixed_expr(
        self, left_expr: Expr, or_: Literal["or"], right_expr: Expr
    ) -> Or:
        return left_expr.chain(Or(right_expr))

    def braced_mixed_expr(self, mixed_expr: Expr) -> Brace:
        return Brace(mixed_expr)

    def start(self, expr: Expr) -> Expr:
        return expr
