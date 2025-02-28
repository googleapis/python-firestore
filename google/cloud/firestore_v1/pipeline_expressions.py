from typing import Any, Iterable, List, Mapping, Union, Generic, TypeVar
from enum import Enum
from enum import auto
import datetime
from dataclasses import dataclass
from google.cloud.firestore_v1.types.document import Value

CONSTANT_ELEMENTS = Union[str, int, float, bool, datetime.datetime, bytes, tuple[float, float], None]
CONSTANT_TYPES = Union[CONSTANT_ELEMENTS, list[Union[CONSTANT_ELEMENTS, list, dict]], dict[str, Union[CONSTANT_ELEMENTS, list, dict]]]

class Ordering:

    class Direction(Enum):
        ASCENDING = auto()
        DESCENDING = auto()

    def __init__(self, expr, order_dir: Direction | str):
        self.expr = expr if isinstance(expr, Expr) else Field.of(expr)
        self.order_dir = Ordering.Direction[order_dir] if isinstance(order_dir, str) else order_dir

    def __repr__(self):
        if self.order_dir is Ordering.Direction.ASCENDING:
            order_str = ".ascending()"
        else:
            order_str = ".descending()"
        return f"{self.expr!r}{order_str}"

    def _to_pb(self) -> Value:
        return Value(
            map_value={"fields":
                {
                    "direction": Value(string_value=self.order_dir.name),
                    "expression": self.expr._to_pb()
                }
            }
        )

@dataclass
class SampleOptions:
    class Mode(Enum):
        DOCUMENTS = "documents"
        PERCENTAGE = "percent"

    n: int
    mode: Mode

    def __post_init__(self):
        self.mode = SampleOptions.Mode(self.mode) if isinstance(self.mode, str) else self.mode

class Expr:
    """Represents an expression that can be evaluated to a value within the
    execution of a pipeline.
    """

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def _to_pb(self) -> Value:
        raise NotImplementedError

    @staticmethod
    def _cast_to_expr_or_convert_to_constant(o: Any) -> "Expr":
        return o if isinstance(o, Expr) else Constant(o)

    def add(self, other: Any) -> "Add":
        return Add(self, self._cast_to_expr_or_convert_to_constant(other))

    def subtract(self, other: Any) -> "Subtract":
        return Subtract(self, self._cast_to_expr_or_convert_to_constant(other))

    def multiply(self, other: Any) -> "Multiply":
        return Multiply(self, self._cast_to_expr_or_convert_to_constant(other))

    def divide(self, other: Any) -> "Divide":
        return Divide(self, self._cast_to_expr_or_convert_to_constant(other))

    def mod(self, other: Any) -> "Mod":
        return Mod(self, self._cast_to_expr_or_convert_to_constant(other))

    def logical_max(self, other: Any) -> "LogicalMax":
        return LogicalMax(self, self._cast_to_expr_or_convert_to_constant(other))

    def logical_min(self, other: Any) -> "LogicalMin":
        return LogicalMin(self, self._cast_to_expr_or_convert_to_constant(other))

    def eq(self, other: Any) -> "Eq":
        return Eq(self, self._cast_to_expr_or_convert_to_constant(other))

    def neq(self, other: Any) -> "Neq":
        return Neq(self, self._cast_to_expr_or_convert_to_constant(other))

    def gt(self, other: Any) -> "Gt":
        return Gt(self, self._cast_to_expr_or_convert_to_constant(other))

    def gte(self, other: Any) -> "Gte":
        return Gte(self, self._cast_to_expr_or_convert_to_constant(other))

    def lt(self, other: Any) -> "Lt":
        return Lt(self, self._cast_to_expr_or_convert_to_constant(other))

    def lte(self, other: Any) -> "Lte":
        return Lte(self, self._cast_to_expr_or_convert_to_constant(other))

    def in_(self, *others: Any) -> "In":
        return In(self, ListOfExprs([self._cast_to_expr_or_convert_to_constant(o) for o in others]))

    def not_in(self, *others: Any) -> "Not":
        return Not(self.in_(*others))

    def array_concat(self, array: List[Any]) -> "ArrayConcat":
        return ArrayConcat(self, ListOfExprs([self._cast_to_expr_or_convert_to_constant(o) for o in array]))

    def array_contains(self, element: Any) -> "ArrayContains":
        return ArrayContains(self, self._cast_to_expr_or_convert_to_constant(element))

    def array_contains_all(self, elements: List[Any]) -> "ArrayContainsAll":
        return ArrayContainsAll(self, ListOfExprs([self._cast_to_expr_or_convert_to_constant(e) for e in elements]))

    def array_contains_any(self, elements: List[Any]) -> "ArrayContainsAny":
        return ArrayContainsAny(self, ListOfExprs([self._cast_to_expr_or_convert_to_constant(e) for e in elements]))

    def array_length(self) -> "ArrayLength":
        return ArrayLength(self)

    def array_reverse(self) -> "ArrayReverse":
        return ArrayReverse(self)

    def is_nan(self) -> "IsNaN":
        return IsNaN(self)

    def exists(self) -> "Exists":
        return Exists(self)

    def sum(self) -> "Sum":
        return Sum(self, False)

    def avg(self) -> "Avg":
        return Avg(self, False)

    def count(self) -> "Count":
        return Count(self)

    def min(self) -> "Min":
        return Min(self, False)

    def max(self) -> "Max":
        return Max(self, False)

    def char_length(self) -> "CharLength":
        return CharLength(self)

    def byte_length(self) -> "ByteLength":
        return ByteLength(self)

    def like(self, pattern: Any) -> "Like":
        return Like(self, self._cast_to_expr_or_convert_to_constant(pattern))

    def regex_contains(self, regex: Any) -> "RegexContains":
        return RegexContains(self, self._cast_to_expr_or_convert_to_constant(regex))

    def regex_matches(self, regex: Any) -> "RegexMatch":
        return RegexMatch(self, self._cast_to_expr_or_convert_to_constant(regex))

    def str_contains(self, substring: Any) -> "StrContains":
        return StrContains(self, self._cast_to_expr_or_convert_to_constant(substring))

    def starts_with(self, prefix: Any) -> "StartsWith":
        return StartsWith(self, self._cast_to_expr_or_convert_to_constant(prefix))

    def ends_with(self, postfix: Any) -> "EndsWith":
        return EndsWith(self, self._cast_to_expr_or_convert_to_constant(postfix))

    def str_concat(self, *elements: Any) -> "StrConcat":
        return StrConcat(*[self._cast_to_expr_or_convert_to_constant(el) for el in elements])

    def to_lower(self) -> "ToLower":
        return ToLower(self)

    def to_upper(self) -> "ToUpper":
        return ToUpper(self)

    def trim(self) -> "Trim":
        return Trim(self)

    def reverse(self) -> "Reverse":
        return Reverse(self)

    def replace_first(self, find: Any, replace: Any) -> "ReplaceFirst":
        return ReplaceFirst(self, self._cast_to_expr_or_convert_to_constant(find), self._cast_to_expr_or_convert_to_constant(replace))

    def replace_all(self, find: Any, replace: Any) -> "ReplaceAll":
        return ReplaceAll(self, self._cast_to_expr_or_convert_to_constant(find), self._cast_to_expr_or_convert_to_constant(replace))

    def map_get(self, key: str) -> "MapGet":
        return MapGet(self, key)

    def cosine_distance(self, other: Any) -> "CosineDistance":
        return CosineDistance(self, self._cast_to_expr_or_convert_to_constant(other))

    def euclidean_distance(self, other: Any) -> "EuclideanDistance":
        return EuclideanDistance(self, self._cast_to_expr_or_convert_to_constant(other))

    def dot_product(self, other: Any) -> "DotProduct":
        return DotProduct(self, self._cast_to_expr_or_convert_to_constant(other))

    def vector_length(self) -> "VectorLength":
        return VectorLength(self)

    def timestamp_to_unix_micros(self) -> "TimestampToUnixMicros":
        return TimestampToUnixMicros(self)

    def unix_micros_to_timestamp(self) -> "UnixMicrosToTimestamp":
        return UnixMicrosToTimestamp(self)

    def timestamp_to_unix_millis(self) -> "TimestampToUnixMillis":
        return TimestampToUnixMillis(self)

    def unix_millis_to_timestamp(self) -> "UnixMillisToTimestamp":
        return UnixMillisToTimestamp(self)

    def timestamp_to_unix_seconds(self) -> "TimestampToUnixSeconds":
        return TimestampToUnixSeconds(self)

    def unix_seconds_to_timestamp(self) -> "UnixSecondsToTimestamp":
        return UnixSecondsToTimestamp(self)

    def timestamp_add(self, unit: Any, amount: Any) -> "TimestampAdd":
        return TimestampAdd(self, self._cast_to_expr_or_convert_to_constant(unit), self._cast_to_expr_or_convert_to_constant(amount))

    def timestamp_sub(self, unit: Any, amount: Any) -> "TimestampSub":
        return TimestampSub(self, self._cast_to_expr_or_convert_to_constant(unit), self._cast_to_expr_or_convert_to_constant(amount))

    def ascending(self) -> Ordering:
        return Ordering.ascending(self)

    def descending(self) -> Ordering:
        return Ordering.descending(self)

    def as_(self, alias: str) -> "ExprWithAlias":
        return ExprWithAlias(self, alias)


class Constant(Expr):
    def __init__(self, value: CONSTANT_TYPES=None):
        self.value = value

    @staticmethod
    def of(value:CONSTANT_TYPES):
        return Constant(value)

    def __repr__(self):
        return f"Constant.of({self.value!r})"

    def _to_pb(self):
        if self.value is None:
            return Value(null_value=0)
        elif isinstance(self.value, bool):
            return Value(boolean_value=self.value)
        elif isinstance(self.value, int):
            return Value(integer_value=self.value)
        elif isinstance(self.value, float):
            return Value(double_value=self.value)
        elif isinstance(self.value, datetime.datetime):
            return Value(timestamp_value=self.value.timestamp())
        elif isinstance(self.value, str):
            return Value(string_value=self.value)
        elif isinstance(self.value, bytes):
            return Value(bytes_value=self.value)
        elif isinstance(self.value, tuple) and len(self.value) == 2 and isinstance(self.value[0], float) and isinstance(self.value[1], float):
            return Value(geo_point_value=self.value)
        elif isinstance(self.value, list):
            return Value(array_value={"values":[Constant(v)._to_pb() for v in self.value]})
        elif isinstance(self.value, dict):
            return Value(map_value={"fields": {k: Constant(v)._to_pb() for k, v in self.value.items()}})
        else:
            raise ValueError(f"Unsupported type: {type(self.value)}")


class ListOfExprs(Expr):
    def __init__(self, exprs: List[Expr]):
        self.exprs: list[Expr] = [Field.of(e) if isinstance(e, str) else e for e in exprs]

    def _to_pb(self):
        return Value(array_value={"values": [e._to_pb() for e in self.exprs]})


class Function(Expr):
    """A type of Expression that takes in inputs and gives outputs."""

    def __init__(self, name: str, params: List[Expr]):
        self.name = name
        self.params = [Field.of(p) if isinstance(p, str) else p for p in params]

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join([repr(p) for p in self.params])})"

    def _to_pb(self):
        return Value(
            function_value={
                "name": self.name, "args": [p._to_pb() for p in self.params]
            }
        )

class Divide(Function):
    def __init__(self, left: Expr, right: Expr):
        super().__init__("divide", [left, right])


class DotProduct(Function):
    def __init__(self, vector1: Expr, vector2: Expr):
        vector1 = Constant(vector1) if isinstance(vector1, list) else vector1
        vector2 = Constant(vector2) if isinstance(vector2, list) else vector2
        super().__init__("dot_product", [vector1, vector2])


class EuclideanDistance(Function):
    def __init__(self, vector1: Expr, vector2: Expr):
        vector1 = Constant(vector1) if isinstance(vector1, list) else vector1
        vector2 = Constant(vector2) if isinstance(vector2, list) else vector2
        super().__init__("euclidean_distance", [vector1, vector2])


class LogicalMax(Function):
    def __init__(self, left: Expr, right: Expr):
        super().__init__("logical_max", [left, right])


class LogicalMin(Function):
    def __init__(self, left: Expr, right: Expr):
        super().__init__("logical_min", [left, right])


class MapGet(Function):
    def __init__(self, map_: Expr, key: str):
        super().__init__("map_get", [map_, Constant(key)])


class Mod(Function):
    def __init__(self, left: Expr, right: Expr):
        super().__init__("mod", [left, right])


class Multiply(Function):
    def __init__(self, left: Expr, right: Expr):
        super().__init__("multiply", [left, right])


class Parent(Function):
    def __init__(self, value: Expr):
        super().__init__("parent", [value])


class ReplaceAll(Function):
    def __init__(self, value: Expr, pattern: Expr, replacement: Expr):
        super().__init__("replace_all", [value, pattern, replacement])


class ReplaceFirst(Function):
    def __init__(self, value: Expr, pattern: Expr, replacement: Expr):
        super().__init__("replace_first", [value, pattern, replacement])


class Reverse(Function):
    def __init__(self, expr: Expr):
        super().__init__("reverse", [expr])


class StrConcat(Function):
    def __init__(self, *exprs: Expr):
        super().__init__("str_concat", exprs)


class Subtract(Function):
    def __init__(self, left: Expr, right: Expr):
        super().__init__("subtract", [left, right])


class TimestampAdd(Function):
    def __init__(self, timestamp: Expr, unit: Expr, amount: Expr):
        super().__init__("timestamp_add", [timestamp, unit, amount])


class TimestampSub(Function):
    def __init__(self, timestamp: Expr, unit: Expr, amount: Expr):
        super().__init__("timestamp_sub", [timestamp, unit, amount])


class TimestampToUnixMicros(Function):
    def __init__(self, input: Expr):
        super().__init__("timestamp_to_unix_micros", [input])


class TimestampToUnixMillis(Function):
    def __init__(self, input: Expr):
        super().__init__("timestamp_to_unix_millis", [input])


class TimestampToUnixSeconds(Function):
    def __init__(self, input: Expr):
        super().__init__("timestamp_to_unix_seconds", [input])


class ToLower(Function):
    def __init__(self, value: Expr):
        super().__init__("to_lower", [value])


class ToUpper(Function):
    def __init__(self, value: Expr):
        super().__init__("to_upper", [value])


class Trim(Function):
    def __init__(self, expr: Expr):
        super().__init__("trim", [expr])


class UnixMicrosToTimestamp(Function):
    def __init__(self, input: Expr):
        super().__init__("unix_micros_to_timestamp", [input])


class UnixMillisToTimestamp(Function):
    def __init__(self, input: Expr):
        super().__init__("unix_millis_to_timestamp", [input])


class UnixSecondsToTimestamp(Function):
    def __init__(self, input: Expr):
        super().__init__("unix_seconds_to_timestamp", [input])


class VectorLength(Function):
    def __init__(self, array: Expr):
        super().__init__("vector_length", [array])


class Add(Function):
    def __init__(self, left: Expr, right: Expr):
        super().__init__("add", [left, right])


class ArrayConcat(Function):
    def __init__(self, array: Expr, rest: List[Expr]):
        super().__init__("array_concat", [array] + rest)


class ArrayElement(Function):
    def __init__(self):
        super().__init__("array_element", [])


class ArrayFilter(Function):
    def __init__(self, array: Expr, filter: "FilterCondition"):
        super().__init__("array_filter", [array, filter])


class ArrayLength(Function):
    def __init__(self, array: Expr):
        super().__init__("array_length", [array])


class ArrayReverse(Function):
    def __init__(self, array: Expr):
        super().__init__("array_reverse", [array])


class ArrayTransform(Function):
    def __init__(self, array: Expr, transform: Function):
        super().__init__("array_transform", [array, transform])


class ByteLength(Function):
    def __init__(self, expr: Expr):
        super().__init__("byte_length", [expr])


class CharLength(Function):
    def __init__(self, expr: Expr):
        super().__init__("char_length", [expr])


class CollectionId(Function):
    def __init__(self, value: Expr):
        super().__init__("collection_id", [value])


class CosineDistance(Function):
    def __init__(self, vector1: Expr, vector2: Expr):
        vector1 = Constant(vector1) if isinstance(vector1, list) else vector1
        vector2 = Constant(vector2) if isinstance(vector2, list) else vector2
        super().__init__("cosine_distance", [vector1, vector2])


class Accumulator(Function):
    """A type of expression that takes in many, and results in one value."""


class Max(Accumulator):
    def __init__(self, value: Expr, distinct: bool=False):
        super().__init__("max", [value])


class Min(Accumulator):
    def __init__(self, value: Expr, distinct: bool=False):
        super().__init__("min", [value])


class Sum(Accumulator):
    def __init__(self, value: Expr, distinct: bool=False):
        super().__init__("sum", [value])


class Avg(Accumulator):
    def __init__(self, value: Expr, distinct: bool=False):
        super().__init__("avg", [value])


class Count(Accumulator):
    def __init__(self, value: Expr = None):
        super().__init__("count", [value] if value else [])


class CountIf(Function):
    def __init__(self, value: Expr, distinct: bool=False):
        super().__init__("countif", [value] if value else [])


class Selectable(Expr):
    """Points at something in the database?"""

    def _to_map(self):
        raise NotImplementedError


T = TypeVar('T', bound=Expr)
class ExprWithAlias(Selectable, Generic[T]):
    def __init__(self, expr: T, alias: str):
        self.expr = expr
        self.alias = alias

    def _to_map(self):
        return self.alias, self.expr._to_pb()

    def __repr__(self):
        return f"{self.expr}.as('{self.alias}')"

    def _to_pb(self):
        return Value(
            map_value={"fields": {self.alias: self.expr._to_pb()}}
        )


class Field(Selectable):
    DOCUMENT_ID = "__name__"

    def __init__(self, path: str):
        self.path = path

    @staticmethod
    def of(path: str):
        return Field(path)

    def _to_map(self):
        return self.path, self._to_pb()

    def __repr__(self):
        return f"Field.of({self.path!r})"

    def _to_pb(self):
        return Value(field_reference_value=self.path)


class FilterCondition(Function):
    """Filters the given data in some way."""


class And(FilterCondition):
    def __init__(self, *conditions: "FilterCondition"):
        super().__init__("and", conditions)


class ArrayContains(FilterCondition):
    def __init__(self, array: Expr, element: Expr):
        super().__init__(
            "array_contains", [array, element if element else Constant(None)]
        )


class ArrayContainsAll(FilterCondition):
    def __init__(self, array: Expr, elements: List[Expr]):
        super().__init__("array_contains_all", [array, ListOfExprs(elements)])


class ArrayContainsAny(FilterCondition):
    def __init__(self, array: Expr, elements: List[Expr]):
        super().__init__("array_contains_any", [array, ListOfExprs(elements)])


class EndsWith(FilterCondition):
    def __init__(self, expr: Expr, postfix: Expr):
        super().__init__("ends_with", [expr, postfix])


class Eq(FilterCondition):
    def __init__(self, left: Expr, right: Expr):
        super().__init__("eq", [left, right if right else Constant(None)])


class Exists(FilterCondition):
    def __init__(self, expr: Expr):
        super().__init__("exists", [expr])


class Gt(FilterCondition):
    def __init__(self, left: Expr, right: Expr):
        super().__init__("gt", [left, right if right else Constant(None)])


class Gte(FilterCondition):
    def __init__(self, left: Expr, right: Expr):
        super().__init__("gte", [left, right if right else Constant(None)])


class If(FilterCondition):
    def __init__(self, condition: "FilterCondition", true_expr: Expr, false_expr: Expr):
        super().__init__(
            "if", [condition, true_expr, false_expr if false_expr else Constant(None)]
        )


class In(FilterCondition):
    def __init__(self, left: Expr, others: List[Expr]):
        super().__init__("in", [left, ListOfExprs(others)])


class IsNaN(FilterCondition):
    def __init__(self, value: Expr):
        super().__init__("is_nan", [value])


class Like(FilterCondition):
    def __init__(self, expr: Expr, pattern: Expr):
        super().__init__("like", [expr, pattern])


class Lt(FilterCondition):
    def __init__(self, left: Expr, right: Expr):
        super().__init__("lt", [left, right if right else Constant(None)])


class Lte(FilterCondition):
    def __init__(self, left: Expr, right: Expr):
        super().__init__("lte", [left, right if right else Constant(None)])


class Neq(FilterCondition):
    def __init__(self, left: Expr, right: Expr):
        super().__init__("neq", [left, right if right else Constant(None)])


class Not(FilterCondition):
    def __init__(self, condition: Expr):
        super().__init__("not", [condition])


class Or(FilterCondition):
    def __init__(self, *conditions: "FilterCondition"):
        super().__init__("or", conditions)


class RegexContains(FilterCondition):
    def __init__(self, expr: Expr, regex: Expr):
        super().__init__("regex_contains", [expr, regex])


class RegexMatch(FilterCondition):
    def __init__(self, expr: Expr, regex: Expr):
        super().__init__("regex_match", [expr, regex])


class StartsWith(FilterCondition):
    def __init__(self, expr: Expr, prefix: Expr):
        super().__init__("starts_with", [expr, prefix])


class StrContains(FilterCondition):
    def __init__(self, expr: Expr, substring: Expr):
        super().__init__("str_contains", [expr, substring])


class Xor(FilterCondition):
    def __init__(self, conditions: List["FilterCondition"]):
        super().__init__("xor", conditions)
