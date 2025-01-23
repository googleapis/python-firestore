from typing import Any, Iterable, List, Mapping


class Expr:
    """Represents an expression that can be evaluated to a value within the
    execution of a pipeline.
    """


class Constant(Expr):
    def __init__(self, value: Any):
        self.value = value


class ListOfExprs(Expr):
    def __init__(self, exprs: List[Expr]):
        self.exprs = exprs


class Function(Expr):
    """A type of Expression that takes in inputs and gives outputs."""

    def __init__(self, name: str, params: List[Expr]):
        self.name = name
        self.params = params


class Divide(Function):
    def __init__(self, left: Expr, right: Expr):
        super().__init__("divide", [left, right])


class DotProduct(Function):
    def __init__(self, vector1: Expr, vector2: Expr):
        super().__init__("dot_product", [vector1, vector2])


class EuclideanDistance(Function):
    def __init__(self, vector1: Expr, vector2: Expr):
        super().__init__("euclidean_distance", [vector1, vector2])


class LogicalMax(Function):
    def __init__(self, left: Expr, right: Expr):
        super().__init__("logical_max", [left, right])


class LogicalMin(Function):
    def __init__(self, left: Expr, right: Expr):
        super().__init__("logical_min", [left, right])


class MapGet(Function):
    def __init__(self, map: Expr, name: str):
        super().__init__("map_get", [map, Constant(name)])


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
    def __init__(self, value: Expr, find: Expr, replacement: Expr):
        super().__init__("replace_all", [value, find, replacement])


class ReplaceFirst(Function):
    def __init__(self, value: Expr, find: Expr, replacement: Expr):
        super().__init__("replace_first", [value, find, replacement])


class Reverse(Function):
    def __init__(self, expr: Expr):
        super().__init__("reverse", [expr])


class StrConcat(Function):
    def __init__(self, first: Expr, exprs: List[Expr]):
        super().__init__("str_concat", [first] + exprs)


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
    def __init__(self, expr: Expr):
        super().__init__("to_lower", [expr])


class ToUpper(Function):
    def __init__(self, expr: Expr):
        super().__init__("to_upper", [expr])


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
        super().__init__("cosine_distance", [vector1, vector2])


class Accumulator(Function):
    """A type of expression that takes in many, and results in one value."""


class Max(Accumulator):
    def __init__(self, value: Expr, distinct: bool):
        super().__init__("max", [value])


class Min(Accumulator):
    def __init__(self, value: Expr, distinct: bool):
        super().__init__("min", [value])


class Sum(Accumulator):
    def __init__(self, value: Expr, distinct: bool):
        super().__init__("sum", [value])


class Avg(Accumulator):
    def __init__(self, value: Expr, distinct: bool):
        super(Function, self).__init__("avg", [value])


class Count(Accumulator):
    def __init__(self, value: Expr = None):
        super(Function, self).__init__("count", [value] if value else [])


class CountIf(Function):
    def __init__(self, value: Expr, distinct: bool):
        super(Function, self).__init__("countif", [value] if value else [])


class Selectable:
    """Points at something in the database?"""


class AccumulatorTarget(Selectable):
    def __init__(self, accumulator: Accumulator, field_name: str, distinct: bool):
        self.accumulator = accumulator
        self.field_name = field_name
        self.distinct = distinct


class ExprWithAlias(Expr, Selectable):
    def __init__(self, expr: Expr, alias: str):
        self.expr = expr
        self.alias = alias


class Field(Expr, Selectable):
    DOCUMENT_ID = "__name__"

    def __init__(self, path: str):
        self.path = path


class FilterCondition(Function):
    """Filters the given data in some way."""


class And(FilterCondition):
    def __init__(self, conditions: List["FilterCondition"]):
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


class IsNan(FilterCondition):
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
    def __init__(self, conditions: List["FilterCondition"]):
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
