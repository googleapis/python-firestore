# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations
from typing import (
    Any,
    Generic,
    TypeVar,
    List,
    Dict,
    Sequence,
)
from abc import ABC
from abc import abstractmethod
from enum import Enum
import datetime
from google.cloud.firestore_v1.types.document import Value
from google.cloud.firestore_v1.types.query import StructuredQuery as Query_pb
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1._helpers import GeoPoint
from google.cloud.firestore_v1._helpers import encode_value
from google.cloud.firestore_v1._helpers import decode_value

CONSTANT_TYPE = TypeVar(
    "CONSTANT_TYPE",
    str,
    int,
    float,
    bool,
    datetime.datetime,
    bytes,
    GeoPoint,
    Vector,
    list,
    Dict[str, Any],
    None,
)


class Ordering:
    """Represents the direction for sorting results in a pipeline."""

    class Direction(Enum):
        ASCENDING = "ascending"
        DESCENDING = "descending"

    def __init__(self, expr, order_dir: Direction | str = Direction.ASCENDING):
        """
        Initializes an Ordering instance
        Args:
            expr (Expr | str): The expression or field path string to sort by.
                If a string is provided, it's treated as a field path.
            order_dir (Direction | str): The direction to sort in.
                Defaults to ascending
        """
        self.expr = expr if isinstance(expr, Expr) else Field.of(expr)
        self.order_dir = (
            Ordering.Direction[order_dir.upper()]
            if isinstance(order_dir, str)
            else order_dir
        )

    def __repr__(self):
        if self.order_dir is Ordering.Direction.ASCENDING:
            order_str = ".ascending()"
        else:
            order_str = ".descending()"
        return f"{self.expr!r}{order_str}"

    def _to_pb(self) -> Value:
        return Value(
            map_value={
                "fields": {
                    "direction": Value(string_value=self.order_dir.value),
                    "expression": self.expr._to_pb(),
                }
            }
        )


class Expr(ABC):
    """Represents an expression that can be evaluated to a value within the
    execution of a pipeline.

    Expressions are the building blocks for creating complex queries and
    transformations in Firestore pipelines. They can represent:

    - **Field references:** Access values from document fields.
    - **Literals:** Represent constant values (strings, numbers, booleans).
    - **Function calls:** Apply functions to one or more expressions.
    - **Aggregations:** Calculate aggregate values (e.g., sum, average) over a set of documents.

    The `Expr` class provides a fluent API for building expressions. You can chain
    together method calls to create complex expressions.
    """

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @abstractmethod
    def _to_pb(self) -> Value:
        raise NotImplementedError

    @staticmethod
    def _cast_to_expr_or_convert_to_constant(o: Any) -> "Expr":
        return o if isinstance(o, Expr) else Constant(o)

    def eq(self, other: Expr | CONSTANT_TYPE) -> "Eq":
        """Creates an expression that checks if this expression is equal to another
        expression or constant value.
        Example:
            >>> # Check if the 'age' field is equal to 21
            >>> Field.of("age").eq(21)
            >>> # Check if the 'city' field is equal to "London"
            >>> Field.of("city").eq("London")
        Args:
            other: The expression or constant value to compare for equality.
        Returns:
            A new `Expr` representing the equality comparison.
        """
        return Eq(self, self._cast_to_expr_or_convert_to_constant(other))

    def neq(self, other: Expr | CONSTANT_TYPE) -> "Neq":
        """Creates an expression that checks if this expression is not equal to another
        expression or constant value.
        Example:
            >>> # Check if the 'status' field is not equal to "completed"
            >>> Field.of("status").neq("completed")
            >>> # Check if the 'country' field is not equal to "USA"
            >>> Field.of("country").neq("USA")
        Args:
            other: The expression or constant value to compare for inequality.
        Returns:
            A new `Expr` representing the inequality comparison.
        """
        return Neq(self, self._cast_to_expr_or_convert_to_constant(other))

    def gt(self, other: Expr | CONSTANT_TYPE) -> "Gt":
        """Creates an expression that checks if this expression is greater than another
        expression or constant value.
        Example:
            >>> # Check if the 'age' field is greater than the 'limit' field
            >>> Field.of("age").gt(Field.of("limit"))
            >>> # Check if the 'price' field is greater than 100
            >>> Field.of("price").gt(100)
        Args:
            other: The expression or constant value to compare for greater than.
        Returns:
            A new `Expr` representing the greater than comparison.
        """
        return Gt(self, self._cast_to_expr_or_convert_to_constant(other))

    def gte(self, other: Expr | CONSTANT_TYPE) -> "Gte":
        """Creates an expression that checks if this expression is greater than or equal
        to another expression or constant value.
        Example:
            >>> # Check if the 'quantity' field is greater than or equal to field 'requirement' plus 1
            >>> Field.of("quantity").gte(Field.of('requirement').add(1))
            >>> # Check if the 'score' field is greater than or equal to 80
            >>> Field.of("score").gte(80)
        Args:
            other: The expression or constant value to compare for greater than or equal to.
        Returns:
            A new `Expr` representing the greater than or equal to comparison.
        """
        return Gte(self, self._cast_to_expr_or_convert_to_constant(other))

    def lt(self, other: Expr | CONSTANT_TYPE) -> "Lt":
        """Creates an expression that checks if this expression is less than another
        expression or constant value.
        Example:
            >>> # Check if the 'age' field is less than 'limit'
            >>> Field.of("age").lt(Field.of('limit'))
            >>> # Check if the 'price' field is less than 50
            >>> Field.of("price").lt(50)
        Args:
            other: The expression or constant value to compare for less than.
        Returns:
            A new `Expr` representing the less than comparison.
        """
        return Lt(self, self._cast_to_expr_or_convert_to_constant(other))

    def lte(self, other: Expr | CONSTANT_TYPE) -> "Lte":
        """Creates an expression that checks if this expression is less than or equal to
        another expression or constant value.
        Example:
            >>> # Check if the 'quantity' field is less than or equal to 20
            >>> Field.of("quantity").lte(Constant.of(20))
            >>> # Check if the 'score' field is less than or equal to 70
            >>> Field.of("score").lte(70)
        Args:
            other: The expression or constant value to compare for less than or equal to.
        Returns:
            A new `Expr` representing the less than or equal to comparison.
        """
        return Lte(self, self._cast_to_expr_or_convert_to_constant(other))

    def in_any(self, array: List[Expr | CONSTANT_TYPE]) -> "In":
        """Creates an expression that checks if this expression is equal to any of the
        provided values or expressions.
        Example:
            >>> # Check if the 'category' field is either "Electronics" or value of field 'primaryType'
            >>> Field.of("category").in_any(["Electronics", Field.of("primaryType")])
        Args:
            array: The values or expressions to check against.
        Returns:
            A new `Expr` representing the 'IN' comparison.
        """
        return In(self, [self._cast_to_expr_or_convert_to_constant(v) for v in array])

    def not_in_any(self, array: List[Expr | CONSTANT_TYPE]) -> "Not":
        """Creates an expression that checks if this expression is not equal to any of the
        provided values or expressions.
        Example:
            >>> # Check if the 'status' field is neither "pending" nor "cancelled"
            >>> Field.of("status").not_in_any(["pending", "cancelled"])
        Args:
            *others: The values or expressions to check against.
        Returns:
            A new `Expr` representing the 'NOT IN' comparison.
        """
        return Not(self.in_any(array))

    def array_contains(self, element: Expr | CONSTANT_TYPE) -> "ArrayContains":
        """Creates an expression that checks if an array contains a specific element or value.
        Example:
            >>> # Check if the 'sizes' array contains the value from the 'selectedSize' field
            >>> Field.of("sizes").array_contains(Field.of("selectedSize"))
            >>> # Check if the 'colors' array contains "red"
            >>> Field.of("colors").array_contains("red")
        Args:
            element: The element (expression or constant) to search for in the array.
        Returns:
            A new `Expr` representing the 'array_contains' comparison.
        """
        return ArrayContains(self, self._cast_to_expr_or_convert_to_constant(element))

    def array_contains_any(
        self, elements: List[Expr | CONSTANT_TYPE]
    ) -> "ArrayContainsAny":
        """Creates an expression that checks if an array contains any of the specified elements.
        Example:
            >>> # Check if the 'categories' array contains either values from field "cate1" or "cate2"
            >>> Field.of("categories").array_contains_any([Field.of("cate1"), Field.of("cate2")])
            >>> # Check if the 'groups' array contains either the value from the 'userGroup' field
            >>> # or the value "guest"
            >>> Field.of("groups").array_contains_any([Field.of("userGroup"), "guest"])
        Args:
            elements: The list of elements (expressions or constants) to check for in the array.
        Returns:
            A new `Expr` representing the 'array_contains_any' comparison.
        """
        return ArrayContainsAny(
            self, [self._cast_to_expr_or_convert_to_constant(e) for e in elements]
        )

    def is_nan(self) -> "IsNaN":
        """Creates an expression that checks if this expression evaluates to 'NaN' (Not a Number).
        Example:
            >>> # Check if the result of a calculation is NaN
            >>> Field.of("value").divide(0).is_nan()
        Returns:
            A new `Expr` representing the 'isNaN' check.
        """
        return IsNaN(self)

    def exists(self) -> "Exists":
        """Creates an expression that checks if a field exists in the document.
        Example:
            >>> # Check if the document has a field named "phoneNumber"
            >>> Field.of("phoneNumber").exists()
        Returns:
            A new `Expr` representing the 'exists' check.
        """
        return Exists(self)


class Constant(Expr, Generic[CONSTANT_TYPE]):
    """Represents a constant literal value in an expression."""

    def __init__(self, value: CONSTANT_TYPE):
        self.value: CONSTANT_TYPE = value

    def __eq__(self, other):
        if not isinstance(other, Constant):
            return other == self.value
        else:
            return other.value == self.value

    @staticmethod
    def of(value: CONSTANT_TYPE) -> Constant[CONSTANT_TYPE]:
        """Creates a constant expression from a Python value."""
        return Constant(value)

    def __repr__(self):
        return f"Constant.of({self.value!r})"

    def _to_pb(self) -> Value:
        return encode_value(self.value)


class ListOfExprs(Expr):
    """Represents a list of expressions, typically used as an argument to functions like 'in' or array functions."""

    def __init__(self, exprs: List[Expr]):
        self.exprs: list[Expr] = exprs

    def __eq__(self, other):
        if not isinstance(other, ListOfExprs):
            return False
        else:
            return other.exprs == self.exprs

    def __repr__(self):
        return f"{self.__class__.__name__}({self.exprs})"

    def _to_pb(self):
        return Value(array_value={"values": [e._to_pb() for e in self.exprs]})


class Function(Expr):
    """A base class for expressions that represent function calls."""

    def __init__(self, name: str, params: Sequence[Expr]):
        self.name = name
        self.params = list(params)

    def __eq__(self, other):
        if not isinstance(other, Function):
            return False
        else:
            return other.name == self.name and other.params == self.params

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join([repr(p) for p in self.params])})"

    def _to_pb(self):
        return Value(
            function_value={
                "name": self.name,
                "args": [p._to_pb() for p in self.params],
            }
        )


class Selectable(Expr):
    """Base class for expressions that can be selected or aliased in projection stages."""

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        else:
            return other._to_map() == self._to_map()

    @abstractmethod
    def _to_map(self) -> tuple[str, Value]:
        """
        Returns a str: Value representation of the Selectable
        """
        raise NotImplementedError

    @classmethod
    def _value_from_selectables(cls, *selectables: Selectable) -> Value:
        """
        Returns a Value representing a map of Selectables
        """
        return Value(
            map_value={
                "fields": {m[0]: m[1] for m in [s._to_map() for s in selectables]}
            }
        )


class Field(Selectable):
    """Represents a reference to a field within a document."""

    DOCUMENT_ID = "__name__"

    def __init__(self, path: str):
        """Initializes a Field reference.
        Args:
            path: The dot-separated path to the field (e.g., "address.city").
                  Use Field.DOCUMENT_ID for the document ID.
        """
        self.path = path

    @staticmethod
    def of(path: str):
        """Creates a Field reference.
        Args:
            path: The dot-separated path to the field (e.g., "address.city").
                  Use Field.DOCUMENT_ID for the document ID.
        Returns:
            A new Field instance.
        """
        return Field(path)

    def _to_map(self):
        return self.path, self._to_pb()

    def __repr__(self):
        return f"Field.of({self.path!r})"

    def _to_pb(self):
        return Value(field_reference_value=self.path)


class FilterCondition(Function):
    """Filters the given data in some way."""

    def __init__(
        self,
        *args,
        use_infix_repr: bool = True,
        infix_name_override: str | None = None,
        **kwargs,
    ):
        self._use_infix_repr = use_infix_repr
        self._infix_name_override = infix_name_override
        super().__init__(*args, **kwargs)

    def __repr__(self):
        """
        Most FilterConditions can be triggered infix. Eg: Field.of('age').gte(18).

        Display them this way in the repr string where possible
        """
        if self._use_infix_repr:
            infix_name = self._infix_name_override or self.name
            if len(self.params) == 1:
                return f"{self.params[0]!r}.{infix_name}()"
            elif len(self.params) == 2:
                return f"{self.params[0]!r}.{infix_name}({self.params[1]!r})"
        return super().__repr__()

    @staticmethod
    def _from_query_filter_pb(filter_pb, client):
        if isinstance(filter_pb, Query_pb.CompositeFilter):
            sub_filters = [
                FilterCondition._from_query_filter_pb(f, client)
                for f in filter_pb.filters
            ]
            if filter_pb.op == Query_pb.CompositeFilter.Operator.OR:
                return Or(*sub_filters)
            elif filter_pb.op == Query_pb.CompositeFilter.Operator.AND:
                return And(*sub_filters)
            else:
                raise TypeError(
                    f"Unexpected CompositeFilter operator type: {filter_pb.op}"
                )
        elif isinstance(filter_pb, Query_pb.UnaryFilter):
            field = Field.of(filter_pb.field.field_path)
            if filter_pb.op == Query_pb.UnaryFilter.Operator.IS_NAN:
                return And(field.exists(), field.is_nan())
            elif filter_pb.op == Query_pb.UnaryFilter.Operator.IS_NOT_NAN:
                return And(field.exists(), Not(field.is_nan()))
            elif filter_pb.op == Query_pb.UnaryFilter.Operator.IS_NULL:
                return And(field.exists(), field.eq(None))
            elif filter_pb.op == Query_pb.UnaryFilter.Operator.IS_NOT_NULL:
                return And(field.exists(), Not(field.eq(None)))
            else:
                raise TypeError(f"Unexpected UnaryFilter operator type: {filter_pb.op}")
        elif isinstance(filter_pb, Query_pb.FieldFilter):
            field = Field.of(filter_pb.field.field_path)
            value = decode_value(filter_pb.value, client)
            if filter_pb.op == Query_pb.FieldFilter.Operator.LESS_THAN:
                return And(field.exists(), field.lt(value))
            elif filter_pb.op == Query_pb.FieldFilter.Operator.LESS_THAN_OR_EQUAL:
                return And(field.exists(), field.lte(value))
            elif filter_pb.op == Query_pb.FieldFilter.Operator.GREATER_THAN:
                return And(field.exists(), field.gt(value))
            elif filter_pb.op == Query_pb.FieldFilter.Operator.GREATER_THAN_OR_EQUAL:
                return And(field.exists(), field.gte(value))
            elif filter_pb.op == Query_pb.FieldFilter.Operator.EQUAL:
                return And(field.exists(), field.eq(value))
            elif filter_pb.op == Query_pb.FieldFilter.Operator.NOT_EQUAL:
                return And(field.exists(), field.neq(value))
            if filter_pb.op == Query_pb.FieldFilter.Operator.ARRAY_CONTAINS:
                return And(field.exists(), field.array_contains(value))
            elif filter_pb.op == Query_pb.FieldFilter.Operator.ARRAY_CONTAINS_ANY:
                return And(field.exists(), field.array_contains_any(value))
            elif filter_pb.op == Query_pb.FieldFilter.Operator.IN:
                return And(field.exists(), field.in_any(value))
            elif filter_pb.op == Query_pb.FieldFilter.Operator.NOT_IN:
                return And(field.exists(), field.not_in_any(value))
            else:
                raise TypeError(f"Unexpected FieldFilter operator type: {filter_pb.op}")
        elif isinstance(filter_pb, Query_pb.Filter):
            # unwrap oneof
            f = (
                filter_pb.composite_filter
                or filter_pb.field_filter
                or filter_pb.unary_filter
            )
            return FilterCondition._from_query_filter_pb(f, client)
        else:
            raise TypeError(f"Unexpected filter type: {type(filter_pb)}")


class And(FilterCondition):
    def __init__(self, *conditions: "FilterCondition"):
        super().__init__("and", conditions, use_infix_repr=False)


class ArrayContains(FilterCondition):
    def __init__(self, array: Expr, element: Expr):
        super().__init__(
            "array_contains", [array, element if element else Constant(None)]
        )


class ArrayContainsAny(FilterCondition):
    """Represents checking if an array contains any of the specified elements."""

    def __init__(self, array: Expr, elements: List[Expr]):
        super().__init__("array_contains_any", [array, ListOfExprs(elements)])


class Eq(FilterCondition):
    """Represents the equality comparison."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("eq", [left, right if right else Constant(None)])


class Exists(FilterCondition):
    """Represents checking if a field exists."""

    def __init__(self, expr: Expr):
        super().__init__("exists", [expr])


class Gt(FilterCondition):
    """Represents the greater than comparison."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("gt", [left, right if right else Constant(None)])


class Gte(FilterCondition):
    """Represents the greater than or equal to comparison."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("gte", [left, right if right else Constant(None)])


class In(FilterCondition):
    """Represents checking if an expression's value is within a list of values."""

    def __init__(self, left: Expr, others: List[Expr]):
        super().__init__(
            "in", [left, ListOfExprs(others)], infix_name_override="in_any"
        )


class IsNaN(FilterCondition):
    """Represents checking if a numeric value is NaN."""

    def __init__(self, value: Expr):
        super().__init__("is_nan", [value])


class Lt(FilterCondition):
    """Represents the less than comparison."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("lt", [left, right if right else Constant(None)])


class Lte(FilterCondition):
    """Represents the less than or equal to comparison."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("lte", [left, right if right else Constant(None)])


class Neq(FilterCondition):
    """Represents the inequality comparison."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("neq", [left, right if right else Constant(None)])


class Not(FilterCondition):
    """Represents the logical NOT of a filter condition."""

    def __init__(self, condition: Expr):
        super().__init__("not", [condition], use_infix_repr=False)


class Or(FilterCondition):
    """Represents the logical OR of multiple filter conditions."""

    def __init__(self, *conditions: "FilterCondition"):
        super().__init__("or", conditions, use_infix_repr=False)
