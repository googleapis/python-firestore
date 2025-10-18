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

    class expose_as_static:
        """
        Decorator to mark instance methods to be exposed as static methods as well as instance
        methods.

        When called statically, the first argument is converted to a Field expression if needed.

        Example:
            >>> Field.of("test").add(5)
            >>> Function.add("test", 5)
        """

        def __init__(self, instance_func):
            self.instance_func = instance_func

        def static_func(self, first_arg, *other_args, **kwargs):
            first_expr = Field.of(first_arg) if not isinstance(first_arg, Expr) else first_arg
            return self.instance_func(first_expr, *other_args, **kwargs)

        def __get__(self, instance, owner):
            if instance is None:
                return self.static_func.__get__(instance, owner)
            else:
                return self.instance_func.__get__(instance, owner)

    @staticmethod
    def array(elements: list[Expr | CONSTANT_TYPE]) -> "Expr":
        """Creates an expression that creates a Firestore array value from an input list.

        Example:
            >>> Expr.array(["bar", Field.of("baz")])

        Args:
            elements: THe input list to evaluate in the expression

        Returns:
            A new `Expr` representing the array function.
        """
        return Array([Expr._cast_to_expr_or_convert_to_constant(e) for e in elements])

    @staticmethod
    def map(elements: dict[str, Expr | CONSTANT_TYPE]) -> "Expr":
        """Creates an expression that creates a Firestore map value from an input dict.

        Example:
            >>> Expr.map({"foo": "bar", "baz": Field.of("baz")})

        Args:
            elements: THe input dict to evaluate in the expression

        Returns:
            A new `Expr` representing the map function.
        """
        return Map({Constant.of(k): Expr._cast_to_expr_or_convert_to_constant(v) for k, v in elements.items()})

    @staticmethod
    def conditional(conditional: BooleanExpr, then_expr: Expr, else_expr: Expr) -> "Expr":
        """
        Creates a conditional expression that evaluates to a 'then' expression if a condition is true
        and an 'else' expression if the condition is false.

        Example:
            >>> # If 'age' is greater than 18, return "Adult"; otherwise, return "Minor".
            >>> Expr.conditional(Field.of("age").greater_than(18), Constant.of("Adult"), Constant.of("Minor"));

        Args:
            conditional: The condition to evaluate.
            then_expr: The expression to return if the condition is true.
            else_expr: The expression to return if the condition is false

        Returns:
            A new `Expr` representing the conditional expression.
        """
        return Conditional(conditional, then_expr, else_expr)

    @expose_as_static
    def add(self, other: Expr | float) -> "Expr":
        """Creates an expression that adds this expression to another expression or constant.

        Example:
            >>> # Add the value of the 'quantity' field and the 'reserve' field.
            >>> Field.of("quantity").add(Field.of("reserve"))
            >>> # Add 5 to the value of the 'age' field
            >>> Field.of("age").add(5)

        Args:
            other: The expression or constant value to add to this expression.

        Returns:
            A new `Expr` representing the addition operation.
        """
        return Add(self, self._cast_to_expr_or_convert_to_constant(other))

    @expose_as_static
    def subtract(self, other: Expr | float) -> "Expr":
        """Creates an expression that subtracts another expression or constant from this expression.

        Example:
            >>> # Subtract the 'discount' field from the 'price' field
            >>> Field.of("price").subtract(Field.of("discount"))
            >>> # Subtract 20 from the value of the 'total' field
            >>> Field.of("total").subtract(20)

        Args:
            other: The expression or constant value to subtract from this expression.

        Returns:
            A new `Expr` representing the subtraction operation.
        """
        return Subtract(self, self._cast_to_expr_or_convert_to_constant(other))

    @expose_as_static
    def multiply(self, other: Expr | float) -> "Expr":
        """Creates an expression that multiplies this expression by another expression or constant.

        Example:
            >>> # Multiply the 'quantity' field by the 'price' field
            >>> Field.of("quantity").multiply(Field.of("price"))
            >>> # Multiply the 'value' field by 2
            >>> Field.of("value").multiply(2)

        Args:
            other: The expression or constant value to multiply by.

        Returns:
            A new `Expr` representing the multiplication operation.
        """
        return Multiply(self, self._cast_to_expr_or_convert_to_constant(other))

    @expose_as_static
    def divide(self, other: Expr | float) -> "Expr":
        """Creates an expression that divides this expression by another expression or constant.

        Example:
            >>> # Divide the 'total' field by the 'count' field
            >>> Field.of("total").divide(Field.of("count"))
            >>> # Divide the 'value' field by 10
            >>> Field.of("value").divide(10)

        Args:
            other: The expression or constant value to divide by.

        Returns:
            A new `Expr` representing the division operation.
        """
        return Divide(self, self._cast_to_expr_or_convert_to_constant(other))

    @expose_as_static
    def mod(self, other: Expr | float) -> "Expr":
        """Creates an expression that calculates the modulo (remainder) to another expression or constant.

        Example:
            >>> # Calculate the remainder of dividing the 'value' field by field 'divisor'.
            >>> Field.of("value").mod(Field.of("divisor"))
            >>> # Calculate the remainder of dividing the 'value' field by 5.
            >>> Field.of("value").mod(5)

        Args:
            other: The divisor expression or constant.

        Returns:
            A new `Expr` representing the modulo operation.
        """
        return Mod(self, self._cast_to_expr_or_convert_to_constant(other))

    @expose_as_static
    def abs(self) -> "Abs":
        """Creates an expression that calculates the absolute value of this expression.

        Example:
            >>> # Get the absolute value of the 'change' field.
            >>> Field.of("change").abs()

        Returns:
            A new `Expr` representing the absolute value.
        """
        return Abs(self)

    @expose_as_static
    def ceil(self) -> "Ceil":
        """Creates an expression that calculates the ceiling of this expression.

        Example:
            >>> # Get the ceiling of the 'value' field.
            >>> Field.of("value").ceil()

        Returns:
            A new `Expr` representing the ceiling value.
        """
        return Ceil(self)

    @expose_as_static
    def exp(self) -> "Exp":
        """Creates an expression that computes e to the power of this expression.

        Example:
            >>> # Compute e to the power of the 'value' field
            >>> Field.of("value").exp()

        Returns:
            A new `Expr` representing the exponential value.
        """
        return Exp(self)

    @expose_as_static
    def floor(self) -> "Floor":
        """Creates an expression that calculates the floor of this expression.

        Example:
            >>> # Get the floor of the 'value' field.
            >>> Field.of("value").floor()

        Returns:
            A new `Expr` representing the floor value.
        """
        return Floor(self)

    @expose_as_static
    def ln(self) -> "Ln":
        """Creates an expression that calculates the natural logarithm of this expression.

        Example:
            >>> # Get the natural logarithm of the 'value' field.
            >>> Field.of("value").ln()

        Returns:
            A new `Expr` representing the natural logarithm.
        """
        return Ln(self)

    @expose_as_static
    def log(self, base: Expr | float) -> "Log":
        """Creates an expression that calculates the logarithm of this expression with a given base.

        Example:
            >>> # Get the logarithm of 'value' with base 2.
            >>> Field.of("value").log(2)
            >>> # Get the logarithm of 'value' with base from 'base_field'.
            >>> Field.of("value").log(Field.of("base_field"))

        Args:
            base: The base of the logarithm.

        Returns:
            A new `Expr` representing the logarithm.
        """
        return Log(self, self._cast_to_expr_or_convert_to_constant(base))

    @expose_as_static
    def pow(self, exponent: Expr | float) -> "Pow":
        """Creates an expression that calculates this expression raised to the power of the exponent.

        Example:
            >>> # Raise 'base_val' to the power of 2.
            >>> Field.of("base_val").pow(2)
            >>> # Raise 'base_val' to the power of 'exponent_val'.
            >>> Field.of("base_val").pow(Field.of("exponent_val"))

        Args:
            exponent: The exponent.

        Returns:
            A new `Expr` representing the power operation.
        """
        return Pow(self, self._cast_to_expr_or_convert_to_constant(exponent))

    @expose_as_static
    def round(self) -> "Round":
        """Creates an expression that rounds this expression to the nearest integer.

        Example:
            >>> # Round the 'value' field.
            >>> Field.of("value").round()

        Returns:
            A new `Expr` representing the rounded value.
        """
        return Round(self)

    @expose_as_static
    def sqrt(self) -> "Sqrt":
        """Creates an expression that calculates the square root of this expression.

        Example:
            >>> # Get the square root of the 'area' field.
            >>> Field.of("area").sqrt()

        Returns:
            A new `Expr` representing the square root.
        """
        return Sqrt(self)

    @expose_as_static
    def logical_maximum(self, other: Expr | CONSTANT_TYPE) -> "Expr":
        """Creates an expression that returns the larger value between this expression
        and another expression or constant, based on Firestore's value type ordering.

        Firestore's value type ordering is described here:
        https://cloud.google.com/firestore/docs/concepts/data-types#value_type_ordering

        Example:
            >>> # Returns the larger value between the 'discount' field and the 'cap' field.
            >>> Field.of("discount").logical_maximum(Field.of("cap"))
            >>> # Returns the larger value between the 'value' field and 10.
            >>> Field.of("value").logical_maximum(10)

        Args:
            other: The other expression or constant value to compare with.

        Returns:
            A new `Expr` representing the logical maximum operation.
        """
        return LogicalMaximum(self, self._cast_to_expr_or_convert_to_constant(other))

    @expose_as_static
    def logical_minimum(self, other: Expr | CONSTANT_TYPE) -> "Expr":
        """Creates an expression that returns the smaller value between this expression
        and another expression or constant, based on Firestore's value type ordering.

        Firestore's value type ordering is described here:
        https://cloud.google.com/firestore/docs/concepts/data-types#value_type_ordering

        Example:
            >>> # Returns the smaller value between the 'discount' field and the 'floor' field.
            >>> Field.of("discount").logical_minimum(Field.of("floor"))
            >>> # Returns the smaller value between the 'value' field and 10.
            >>> Field.of("value").logical_minimum(10)

        Args:
            other: The other expression or constant value to compare with.

        Returns:
            A new `Expr` representing the logical minimum operation.
        """
        return LogicalMinimum(self, self._cast_to_expr_or_convert_to_constant(other))

    @expose_as_static
    def equal(self, other: Expr | CONSTANT_TYPE) -> "BooleanExpr":
        """Creates an expression that checks if this expression is equal to another
        expression or constant value.

        Example:
            >>> # Check if the 'age' field is equal to 21
            >>> Field.of("age").equal(21)
            >>> # Check if the 'city' field is equal to "London"
            >>> Field.of("city").equal("London")

        Args:
            other: The expression or constant value to compare for equality.

        Returns:
            A new `Expr` representing the equality comparison.
        """
        return Equal(self, self._cast_to_expr_or_convert_to_constant(other))

    @expose_as_static
    def not_equal(self, other: Expr | CONSTANT_TYPE) -> "BooleanExpr":
        """Creates an expression that checks if this expression is not equal to another
        expression or constant value.

        Example:
            >>> # Check if the 'status' field is not equal to "completed"
            >>> Field.of("status").not_equal("completed")
            >>> # Check if the 'country' field is not equal to "USA"
            >>> Field.of("country").not_equal("USA")

        Args:
            other: The expression or constant value to compare for inequality.

        Returns:
            A new `Expr` representing the inequality comparison.
        """
        return NotEqual(self, self._cast_to_expr_or_convert_to_constant(other))

    @expose_as_static
    def greater_than(self, other: Expr | CONSTANT_TYPE) -> "BooleanExpr":
        """Creates an expression that checks if this expression is greater than another
        expression or constant value.

        Example:
            >>> # Check if the 'age' field is greater than the 'limit' field
            >>> Field.of("age").greater_than(Field.of("limit"))
            >>> # Check if the 'price' field is greater than 100
            >>> Field.of("price").greater_than(100)

        Args:
            other: The expression or constant value to compare for greater than.

        Returns:
            A new `Expr` representing the greater than comparison.
        """
        return GreaterThan(self, self._cast_to_expr_or_convert_to_constant(other))

    @expose_as_static
    def greater_than_or_equal(self, other: Expr | CONSTANT_TYPE) -> "BooleanExpr":
        """Creates an expression that checks if this expression is greater than or equal
        to another expression or constant value.

        Example:
            >>> # Check if the 'quantity' field is greater than or equal to field 'requirement' plus 1
            >>> Field.of("quantity").greater_than_or_equal(Field.of('requirement').add(1))
            >>> # Check if the 'score' field is greater than or equal to 80
            >>> Field.of("score").greater_than_or_equal(80)

        Args:
            other: The expression or constant value to compare for greater than or equal to.

        Returns:
            A new `Expr` representing the greater than or equal to comparison.
        """
        return GreaterThanOrEqual(
            self, self._cast_to_expr_or_convert_to_constant(other)
        )

    @expose_as_static
    def less_than(self, other: Expr | CONSTANT_TYPE) -> "BooleanExpr":
        """Creates an expression that checks if this expression is less than another
        expression or constant value.

        Example:
            >>> # Check if the 'age' field is less than 'limit'
            >>> Field.of("age").less_than(Field.of('limit'))
            >>> # Check if the 'price' field is less than 50
            >>> Field.of("price").less_than(50)

        Args:
            other: The expression or constant value to compare for less than.

        Returns:
            A new `Expr` representing the less than comparison.
        """
        return LessThan(self, self._cast_to_expr_or_convert_to_constant(other))

    @expose_as_static
    def less_than_or_equal(self, other: Expr | CONSTANT_TYPE) -> "BooleanExpr":
        """Creates an expression that checks if this expression is less than or equal to
        another expression or constant value.

        Example:
            >>> # Check if the 'quantity' field is less than or equal to 20
            >>> Field.of("quantity").less_than_or_equal(Constant.of(20))
            >>> # Check if the 'score' field is less than or equal to 70
            >>> Field.of("score").less_than_or_equal(70)

        Args:
            other: The expression or constant value to compare for less than or equal to.

        Returns:
            A new `Expr` representing the less than or equal to comparison.
        """
        return LessThanOrEqual(self, self._cast_to_expr_or_convert_to_constant(other))

    @expose_as_static
    def equal_any(self, array: Sequence[Expr | CONSTANT_TYPE]) -> "BooleanExpr":
        """Creates an expression that checks if this expression is equal to any of the
        provided values or expressions.

        Example:
            >>> # Check if the 'category' field is either "Electronics" or value of field 'primaryType'
            >>> Field.of("category").equal_any(["Electronics", Field.of("primaryType")])

        Args:
            array: The values or expressions to check against.

        Returns:
            A new `Expr` representing the 'IN' comparison.
        """
        return EqualAny(self, [self._cast_to_expr_or_convert_to_constant(v) for v in array])

    @expose_as_static
    def not_equal_any(self, array: Sequence[Expr | CONSTANT_TYPE]) -> "BooleanExpr":
        """Creates an expression that checks if this expression is not equal to any of the
        provided values or expressions.

        Example:
            >>> # Check if the 'status' field is neither "pending" nor "cancelled"
            >>> Field.of("status").not_equal_any(["pending", "cancelled"])

        Args:
            array: The values or expressions to check against.

        Returns:
            A new `Expr` representing the 'NOT IN' comparison.
        """
        return NotEqualAny(self, [self._cast_to_expr_or_convert_to_constant(v) for v in array])

    @expose_as_static
    def array_get(self, index: Expr | int) -> "Expr":
        """Creates an expression that indexes into an array from the beginning or end
        and returns the element. If the index exceeds the array length, an error is
        returned. A negative index, starts from the end.

        Example:
            >>> # Return the value in the tags field array at index specified by field 'favoriteTag'.
            >>> Field.of("tags").array_get(Field.of("favoriteTag"))

        Args:
            index: The index of the element to return.

        Returns:
            A new `Expr` representing the operation.
        """
        return ArrayGet(self, self._cast_to_expr_or_convert_to_constant(index))

    @expose_as_static
    def array_concat(self, array: Sequence[Expr | CONSTANT_TYPE]) -> "Expr":
        """Creates an expression that concatenates an array expression with another array.

        Example:
            >>> # Combine the 'tags' array with a new array and an array field
            >>> Field.of("tags").array_concat(["newTag1", "newTag2", Field.of("otherTag")])

        Args:
            array: The list of constants or expressions to concat with.

        Returns:
            A new `Expr` representing the concatenated array.
        """
        return ArrayConcat(
            self, [self._cast_to_expr_or_convert_to_constant(o) for o in array]
        )

    @expose_as_static
    def array_contains(self, element: Expr | CONSTANT_TYPE) -> "BooleanExpr":
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

    @expose_as_static
    def array_contains_all(
        self, elements: Sequence[Expr | CONSTANT_TYPE]
    ) -> "BooleanExpr":
        """Creates an expression that checks if an array contains all the specified elements.

        Example:
            >>> # Check if the 'tags' array contains both "news" and "sports"
            >>> Field.of("tags").array_contains_all(["news", "sports"])
            >>> # Check if the 'tags' array contains both of the values from field 'tag1' and "tag2"
            >>> Field.of("tags").array_contains_all([Field.of("tag1"), "tag2"])

        Args:
            elements: The list of elements (expressions or constants) to check for in the array.

        Returns:
            A new `Expr` representing the 'array_contains_all' comparison.
        """
        return ArrayContainsAll(
            self, [self._cast_to_expr_or_convert_to_constant(e) for e in elements]
        )

    @expose_as_static
    def array_contains_any(
        self, elements: Sequence[Expr | CONSTANT_TYPE]
    ) -> "BooleanExpr":
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

    @expose_as_static
    def array_length(self) -> "Expr":
        """Creates an expression that calculates the length of an array.

        Example:
            >>> # Get the number of items in the 'cart' array
            >>> Field.of("cart").array_length()

        Returns:
            A new `Expr` representing the length of the array.
        """
        return ArrayLength(self)

    @expose_as_static
    def array_reverse(self) -> "Expr":
        """Creates an expression that returns the reversed content of an array.

        Example:
            >>> # Get the 'preferences' array in reversed order.
            >>> Field.of("preferences").array_reverse()

        Returns:
            A new `Expr` representing the reversed array.
        """
        return ArrayReverse(self)

    @expose_as_static
    def is_nan(self) -> "BooleanExpr":
        """Creates an expression that checks if this expression evaluates to 'NaN' (Not a Number).

        Example:
            >>> # Check if the result of a calculation is NaN
            >>> Field.of("value").divide(0).is_nan()

        Returns:
            A new `Expr` representing the 'isNaN' check.
        """
        return IsNaN(self)

    @expose_as_static
    def exists(self) -> "BooleanExpr":
        """Creates an expression that checks if a field exists in the document.

        Example:
            >>> # Check if the document has a field named "phoneNumber"
            >>> Field.of("phoneNumber").exists()

        Returns:
            A new `Expr` representing the 'exists' check.
        """
        return Exists(self)

    @expose_as_static
    def sum(self) -> "Expr":
        """Creates an aggregation that calculates the sum of a numeric field across multiple stage inputs.

        Example:
            >>> # Calculate the total revenue from a set of orders
            >>> Field.of("orderAmount").sum().as_("totalRevenue")

        Returns:
            A new `AggregateFunction` representing the 'sum' aggregation.
        """
        return Sum(self)

    @expose_as_static
    def average(self) -> "Expr":
        """Creates an aggregation that calculates the average (mean) of a numeric field across multiple
        stage inputs.

        Example:
            >>> # Calculate the average age of users
            >>> Field.of("age").average().as_("averageAge")

        Returns:
            A new `AggregateFunction` representing the 'avg' aggregation.
        """
        return Average(self)


    def count(self) -> "Expr":
        """Creates an aggregation that counts the number of stage inputs with valid evaluations of the
        expression or field.

        Example:
            >>> # Count the total number of products
            >>> Field.of("productId").count().as_("totalProducts")

        Returns:
            A new `AggregateFunction` representing the 'count' aggregation.
        """
        return Count(self)

    @expose_as_static
    def minimum(self) -> "Expr":
        """Creates an aggregation that finds the minimum value of a field across multiple stage inputs.

        Example:
            >>> # Find the lowest price of all products
            >>> Field.of("price").minimum().as_("lowestPrice")

        Returns:
            A new `AggregateFunction` representing the 'minimum' aggregation.
        """
        return Minimum(self)

    @expose_as_static
    def maximum(self) -> "Expr":
        """Creates an aggregation that finds the maximum value of a field across multiple stage inputs.

        Example:
            >>> # Find the highest score in a leaderboard
            >>> Field.of("score").maximum().as_("highestScore")

        Returns:
            A new `AggregateFunction` representing the 'maximum' aggregation.
        """
        return Maximum(self)

    @expose_as_static
    def char_length(self) -> "Expr":
        """Creates an expression that calculates the character length of a string.

        Example:
            >>> # Get the character length of the 'name' field
            >>> Field.of("name").char_length()

        Returns:
            A new `Expr` representing the length of the string.
        """
        return CharLength(self)

    @expose_as_static
    def byte_length(self) -> "Expr":
        """Creates an expression that calculates the byte length of a string in its UTF-8 form.

        Example:
            >>> # Get the byte length of the 'name' field
            >>> Field.of("name").byte_length()

        Returns:
            A new `Expr` representing the byte length of the string.
        """
        return ByteLength(self)

    @expose_as_static
    def like(self, pattern: Expr | str) -> "BooleanExpr":
        """Creates an expression that performs a case-sensitive string comparison.

        Example:
            >>> # Check if the 'title' field contains the word "guide" (case-sensitive)
            >>> Field.of("title").like("%guide%")
            >>> # Check if the 'title' field matches the pattern specified in field 'pattern'.
            >>> Field.of("title").like(Field.of("pattern"))

        Args:
            pattern: The pattern (string or expression) to search for. You can use "%" as a wildcard character.

        Returns:
            A new `Expr` representing the 'like' comparison.
        """
        return Like(self, self._cast_to_expr_or_convert_to_constant(pattern))

    @expose_as_static
    def regex_contains(self, regex: Expr | str) -> "BooleanExpr":
        """Creates an expression that checks if a string contains a specified regular expression as a
        substring.

        Example:
            >>> # Check if the 'description' field contains "example" (case-insensitive)
            >>> Field.of("description").regex_contains("(?i)example")
            >>> # Check if the 'description' field contains the regular expression stored in field 'regex'
            >>> Field.of("description").regex_contains(Field.of("regex"))

        Args:
            regex: The regular expression (string or expression) to use for the search.

        Returns:
            A new `Expr` representing the 'contains' comparison.
        """
        return RegexContains(self, self._cast_to_expr_or_convert_to_constant(regex))

    @expose_as_static
    def regex_matches(self, regex: Expr | str) -> "BooleanExpr":
        """Creates an expression that checks if a string matches a specified regular expression.

        Example:
            >>> # Check if the 'email' field matches a valid email pattern
            >>> Field.of("email").regex_matches("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}")
            >>> # Check if the 'email' field matches a regular expression stored in field 'regex'
            >>> Field.of("email").regex_matches(Field.of("regex"))

        Args:
            regex: The regular expression (string or expression) to use for the match.

        Returns:
            A new `Expr` representing the regular expression match.
        """
        return RegexMatch(self, self._cast_to_expr_or_convert_to_constant(regex))

    @expose_as_static
    def string_contains(self, substring: Expr | str) -> "BooleanExpr":
        """Creates an expression that checks if this string expression contains a specified substring.

        Example:
            >>> # Check if the 'description' field contains "example".
            >>> Field.of("description").string_contains("example")
            >>> # Check if the 'description' field contains the value of the 'keyword' field.
            >>> Field.of("description").string_contains(Field.of("keyword"))

        Args:
            substring: The substring (string or expression) to use for the search.

        Returns:
            A new `Expr` representing the 'contains' comparison.
        """
        return StringContains(
            self, self._cast_to_expr_or_convert_to_constant(substring)
        )

    @expose_as_static
    def starts_with(self, prefix: Expr | str) -> "BooleanExpr":
        """Creates an expression that checks if a string starts with a given prefix.

        Example:
            >>> # Check if the 'name' field starts with "Mr."
            >>> Field.of("name").starts_with("Mr.")
            >>> # Check if the 'fullName' field starts with the value of the 'firstName' field
            >>> Field.of("fullName").starts_with(Field.of("firstName"))

        Args:
            prefix: The prefix (string or expression) to check for.

        Returns:
            A new `Expr` representing the 'starts with' comparison.
        """
        return StartsWith(self, self._cast_to_expr_or_convert_to_constant(prefix))

    @expose_as_static
    def ends_with(self, postfix: Expr | str) -> "BooleanExpr":
        """Creates an expression that checks if a string ends with a given postfix.

        Example:
            >>> # Check if the 'filename' field ends with ".txt"
            >>> Field.of("filename").ends_with(".txt")
            >>> # Check if the 'url' field ends with the value of the 'extension' field
            >>> Field.of("url").ends_with(Field.of("extension"))

        Args:
            postfix: The postfix (string or expression) to check for.

        Returns:
            A new `Expr` representing the 'ends with' comparison.
        """
        return EndsWith(self, self._cast_to_expr_or_convert_to_constant(postfix))

    @expose_as_static
    def string_concat(self, *elements: Expr | CONSTANT_TYPE) -> "Expr":
        """Creates an expression that concatenates string expressions, fields or constants together.

        Example:
            >>> # Combine the 'firstName', " ", and 'lastName' fields into a single string
            >>> Field.of("firstName").string_concat(" ", Field.of("lastName"))

        Args:
            *elements: The expressions or constants (typically strings) to concatenate.

        Returns:
            A new `Expr` representing the concatenated string.
        """
        return StringConcat(
            self, *[self._cast_to_expr_or_convert_to_constant(el) for el in elements]
        )

    @expose_as_static
    def to_lower(self) -> "Expr":
        """Creates an expression that converts a string to lowercase.

        Example:
            >>> # Convert the 'name' field to lowercase
            >>> Field.of("name").to_lower()

        Returns:
            A new `Expr` representing the lowercase string.
        """
        return ToLower(self)

    @expose_as_static
    def to_upper(self) -> "Expr":
        """Creates an expression that converts a string to uppercase.

        Example:
            >>> # Convert the 'title' field to uppercase
            >>> Field.of("title").to_upper()

        Returns:
            A new `Expr` representing the uppercase string.
        """
        return ToUpper(self)

    @expose_as_static
    def trim(self) -> "Expr":
        """Creates an expression that removes leading and trailing whitespace from a string.

        Example:
            >>> # Trim whitespace from the 'userInput' field
            >>> Field.of("userInput").trim()

        Returns:
            A new `Expr` representing the trimmed string.
        """
        return Trim(self)

    @expose_as_static
    def reverse(self) -> "Expr":
        """Creates an expression that reverses a string.

        Example:
            >>> # Reverse the 'userInput' field
            >>> Field.of("userInput").reverse()

        Returns:
            A new `Expr` representing the reversed string.
        """
        return Reverse(self)

    @expose_as_static
    def map_get(self, key: str) -> "Expr":
        """Accesses a value from the map produced by evaluating this expression.

        Example:
            >>> Expr.map({"city": "London"}).map_get("city")
            >>> Field.of("address").map_get("city")

        Args:
            key: The key to access in the map.

        Returns:
            A new `Expr` representing the value associated with the given key in the map.
        """
        return MapGet(self, Constant.of(key))

    @expose_as_static
    def map_remove(self, key: str) -> "Expr":
        """Remove a key from a the map produced by evaluating this expression.

        Example:
            >>> Expr.map({"city": "London"}).map_remove("city")
            >>> Field.of("address").map_remove("city")

        Args:
            key: The key to ewmove in the map.

        Returns:
            A new `Expr` representing the map_remove operation.
        """
        return MapRemove(self, Constant.of(key))

    @expose_as_static
    def map_merge(self, *other_maps: Expr | dict[str, Expr | CONSTANT_TYPE])-> "Expr":
        """Creates an expression that merges one or more dicts into a single map.

        Example:
            >>> Field.of("settings").map_merge({"enabled":True}, Function.conditional(Field.of('isAdmin'), {"admin":True}, {}})
            >>> Expr.map({"city": "London"}).map_merge({"country": "UK"}, {"isCapital": True})

        Args:
            *other_maps: Sequence of maps to merge into the resulting map.

        Returns:
            A new `Expr` representing the value associated with the given key in the map.
        """
        map_list = []
        for map in other_maps:
            map_list.append(map if isinstance(map, Expr) else Expr.map(map))
        return MapMerge(self, *map_list)


    @expose_as_static
    def cosine_distance(self, other: Expr | list[float] | Vector) -> "Expr":
        """Calculates the cosine distance between two vectors.

        Example:
            >>> # Calculate the cosine distance between the 'userVector' field and the 'itemVector' field
            >>> Field.of("userVector").cosine_distance(Field.of("itemVector"))
            >>> # Calculate the Cosine distance between the 'location' field and a target location
            >>> Field.of("location").cosine_distance([37.7749, -122.4194])

        Args:
            other: The other vector (represented as an Expr, list of floats, or Vector) to compare against.

        Returns:
            A new `Expr` representing the cosine distance between the two vectors.
        """
        return CosineDistance(self, self._cast_to_expr_or_convert_to_constant(other))

    @expose_as_static
    def euclidean_distance(self, other: Expr | list[float] | Vector) -> "Expr":
        """Calculates the Euclidean distance between two vectors.

        Example:
            >>> # Calculate the Euclidean distance between the 'location' field and a target location
            >>> Field.of("location").euclidean_distance([37.7749, -122.4194])
            >>> # Calculate the Euclidean distance between two vector fields: 'pointA' and 'pointB'
            >>> Field.of("pointA").euclidean_distance(Field.of("pointB"))

        Args:
            other: The other vector (represented as an Expr, list of floats, or Vector) to compare against.

        Returns:
            A new `Expr` representing the Euclidean distance between the two vectors.
        """
        return EuclideanDistance(self, self._cast_to_expr_or_convert_to_constant(other))

    @expose_as_static
    def dot_product(self, other: Expr | list[float] | Vector) -> "Expr":
        """Calculates the dot product between two vectors.

        Example:
            >>> # Calculate the dot product between a feature vector and a target vector
            >>> Field.of("features").dot_product([0.5, 0.8, 0.2])
            >>> # Calculate the dot product between two document vectors: 'docVector1' and 'docVector2'
            >>> Field.of("docVector1").dot_product(Field.of("docVector2"))

        Args:
            other: The other vector (represented as an Expr, list of floats, or Vector) to calculate dot product with.

        Returns:
            A new `Expr` representing the dot product between the two vectors.
        """
        return DotProduct(self, self._cast_to_expr_or_convert_to_constant(other))

    @expose_as_static
    def vector_length(self) -> "Expr":
        """Creates an expression that calculates the length (dimension) of a Firestore Vector.

        Example:
            >>> # Get the vector length (dimension) of the field 'embedding'.
            >>> Field.of("embedding").vector_length()

        Returns:
            A new `Expr` representing the length of the vector.
        """
        return VectorLength(self)

    @expose_as_static
    def timestamp_to_unix_micros(self) -> "Expr":
        """Creates an expression that converts a timestamp to the number of microseconds since the epoch
        (1970-01-01 00:00:00 UTC).

        Truncates higher levels of precision by rounding down to the beginning of the microsecond.

        Example:
            >>> # Convert the 'timestamp' field to microseconds since the epoch.
            >>> Field.of("timestamp").timestamp_to_unix_micros()

        Returns:
            A new `Expr` representing the number of microseconds since the epoch.
        """
        return TimestampToUnixMicros(self)

    @expose_as_static
    def unix_micros_to_timestamp(self) -> "Expr":
        """Creates an expression that converts a number of microseconds since the epoch (1970-01-01
        00:00:00 UTC) to a timestamp.

        Example:
            >>> # Convert the 'microseconds' field to a timestamp.
            >>> Field.of("microseconds").unix_micros_to_timestamp()

        Returns:
            A new `Expr` representing the timestamp.
        """
        return UnixMicrosToTimestamp(self)

    @expose_as_static
    def timestamp_to_unix_millis(self) -> "Expr":
        """Creates an expression that converts a timestamp to the number of milliseconds since the epoch
        (1970-01-01 00:00:00 UTC).

        Truncates higher levels of precision by rounding down to the beginning of the millisecond.

        Example:
            >>> # Convert the 'timestamp' field to milliseconds since the epoch.
            >>> Field.of("timestamp").timestamp_to_unix_millis()

        Returns:
            A new `Expr` representing the number of milliseconds since the epoch.
        """
        return TimestampToUnixMillis(self)

    @expose_as_static
    def unix_millis_to_timestamp(self) -> "Expr":
        """Creates an expression that converts a number of milliseconds since the epoch (1970-01-01
        00:00:00 UTC) to a timestamp.

        Example:
            >>> # Convert the 'milliseconds' field to a timestamp.
            >>> Field.of("milliseconds").unix_millis_to_timestamp()

        Returns:
            A new `Expr` representing the timestamp.
        """
        return UnixMillisToTimestamp(self)

    @expose_as_static
    def timestamp_to_unix_seconds(self) -> "Expr":
        """Creates an expression that converts a timestamp to the number of seconds since the epoch
        (1970-01-01 00:00:00 UTC).

        Truncates higher levels of precision by rounding down to the beginning of the second.

        Example:
            >>> # Convert the 'timestamp' field to seconds since the epoch.
            >>> Field.of("timestamp").timestamp_to_unix_seconds()

        Returns:
            A new `Expr` representing the number of seconds since the epoch.
        """
        return TimestampToUnixSeconds(self)

    @expose_as_static
    def unix_seconds_to_timestamp(self) -> "Expr":
        """Creates an expression that converts a number of seconds since the epoch (1970-01-01 00:00:00
        UTC) to a timestamp.

        Example:
            >>> # Convert the 'seconds' field to a timestamp.
            >>> Field.of("seconds").unix_seconds_to_timestamp()

        Returns:
            A new `Expr` representing the timestamp.
        """
        return UnixSecondsToTimestamp(self)

    @expose_as_static
    def timestamp_add(self, unit: Expr | str, amount: Expr | float) -> "Expr":
        """Creates an expression that adds a specified amount of time to this timestamp expression.

        Example:
            >>> # Add a duration specified by the 'unit' and 'amount' fields to the 'timestamp' field.
            >>> Field.of("timestamp").timestamp_add(Field.of("unit"), Field.of("amount"))
            >>> # Add 1.5 days to the 'timestamp' field.
            >>> Field.of("timestamp").timestamp_add("day", 1.5)

        Args:
            unit: The expression or string evaluating to the unit of time to add, must be one of
                  'microsecond', 'millisecond', 'second', 'minute', 'hour', 'day'.
            amount: The expression or float representing the amount of time to add.

        Returns:
            A new `Expr` representing the resulting timestamp.
        """
        return TimestampAdd(
            self,
            self._cast_to_expr_or_convert_to_constant(unit),
            self._cast_to_expr_or_convert_to_constant(amount),
        )

    @expose_as_static
    def timestamp_subtract(self, unit: Expr | str, amount: Expr | float) -> "Expr":
        """Creates an expression that subtracts a specified amount of time from this timestamp expression.

        Example:
            >>> # Subtract a duration specified by the 'unit' and 'amount' fields from the 'timestamp' field.
            >>> Field.of("timestamp").timestamp_subtract(Field.of("unit"), Field.of("amount"))
            >>> # Subtract 2.5 hours from the 'timestamp' field.
            >>> Field.of("timestamp").timestamp_subtract("hour", 2.5)

        Args:
            unit: The expression or string evaluating to the unit of time to subtract, must be one of
                  'microsecond', 'millisecond', 'second', 'minute', 'hour', 'day'.
            amount: The expression or float representing the amount of time to subtract.

        Returns:
            A new `Expr` representing the resulting timestamp.
        """
        return TimestampSubtract(
            self,
            self._cast_to_expr_or_convert_to_constant(unit),
            self._cast_to_expr_or_convert_to_constant(amount),
        )

    def ascending(self) -> Ordering:
        """Creates an `Ordering` that sorts documents in ascending order based on this expression.

        Example:
            >>> # Sort documents by the 'name' field in ascending order
            >>> client.pipeline().collection("users").sort(Field.of("name").ascending())

        Returns:
            A new `Ordering` for ascending sorting.
        """
        return Ordering(self, Ordering.Direction.ASCENDING)

    def descending(self) -> Ordering:
        """Creates an `Ordering` that sorts documents in descending order based on this expression.

        Example:
            >>> # Sort documents by the 'createdAt' field in descending order
            >>> client.pipeline().collection("users").sort(Field.of("createdAt").descending())

        Returns:
            A new `Ordering` for descending sorting.
        """
        return Ordering(self, Ordering.Direction.DESCENDING)

    def as_(self, alias: str) -> "AliasedExpr":
        """Assigns an alias to this expression.

        Aliases are useful for renaming fields in the output of a stage or for giving meaningful
        names to calculated values.

        Example:
            >>> # Calculate the total price and assign it the alias "totalPrice" and add it to the output.
            >>> client.pipeline().collection("items").add_fields(
            ...     Field.of("price").multiply(Field.of("quantity")).as_("totalPrice")
            ... )

        Args:
            alias: The alias to assign to this expression.

        Returns:
            A new `Selectable` (typically an `AliasedExpr`) that wraps this
            expression and associates it with the provided alias.
        """
        return AliasedExpr(self, alias)


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

    def __hash__(self):
        return hash(self.value)

    def _to_pb(self) -> Value:
        return encode_value(self.value)


class ListOfExprs(Expr):
    """Represents a list of expressions, typically used as an argument to functions like 'in' or array functions."""

    def __init__(self, exprs: Sequence[Expr]):
        self.exprs: list[Expr] = list(exprs)

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


class Divide(Function):
    """Represents the division function."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("divide", [left, right])


class DotProduct(Function):
    """Represents the vector dot product function."""

    def __init__(self, vector1: Expr, vector2: Expr):
        super().__init__("dot_product", [vector1, vector2])


class EuclideanDistance(Function):
    """Represents the vector Euclidean distance function."""

    def __init__(self, vector1: Expr, vector2: Expr):
        super().__init__("euclidean_distance", [vector1, vector2])


class LogicalMaximum(Function):
    """
    Returns the larger value between this expression and another expression or constant,
    based on Firestore's value type ordering.
    """

    def __init__(self, left: Expr, right: Expr):
        super().__init__("max", [left, right])


class LogicalMinimum(Function):
    """
    Returns the smaller value between this expression and another expression or constant,
    based on Firestore's value type ordering.
    """

    def __init__(self, left: Expr, right: Expr):
        super().__init__("min", [left, right])


class Map(Function):
    """Creates an expression that creates a Firestore map value from an input dict."""

    def __init__(self, elements: dict[Constant[str], Expr]):
        element_list = []
        for k,v in elements.items():
            element_list.append(k)
            element_list.append(v)
        super().__init__("map", element_list)

    def __repr__(self):
        d = {a:b for a, b in zip(self.params[::2], self.params[1::2])}
        return f"Map({d})"


class MapGet(Function):
    """Creates an expression that accesses a map value by key."""

    def __init__(self, map_: Expr, key: Constant[str]):
        super().__init__("map_get", [map_, key])


class MapMerge(Function):
    """Creates an expression that merges multiple map values."""

    def __init__(self, *maps: Expr):
        super().__init__("map_merge", [*maps])


class MapRemove(Function):
    """Creates an expression that removes a key from a map."""

    def __init__(self, map_: Expr, key: Constant[str]):
        super().__init__("map_remove", [map_, key])



class Mod(Function):
    """Represents the modulo function."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("mod", [left, right])


class Multiply(Function):
    """Represents the multiplication function."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("multiply", [left, right])


class Parent(Function):
    """Represents getting the parent document reference."""

    def __init__(self, value: Expr):
        super().__init__("parent", [value])


class Reverse(Function):
    """Represents reversing a string."""

    def __init__(self, expr: Expr):
        super().__init__("reverse", [expr])


class StringConcat(Function):
    """Represents concatenating multiple strings."""

    def __init__(self, *exprs: Expr):
        super().__init__("string_concat", exprs)


class Subtract(Function):
    """Represents the subtraction function."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("subtract", [left, right])


class TimestampAdd(Function):
    """Represents adding a duration to a timestamp."""

    def __init__(self, timestamp: Expr, unit: Expr, amount: Expr):
        super().__init__("timestamp_add", [timestamp, unit, amount])


class Abs(Function):
    """Represents the absolute value function."""

    def __init__(self, value: Expr):
        super().__init__("abs", [value])


class Ceil(Function):
    """Represents the ceiling function."""

    def __init__(self, value: Expr):
        super().__init__("ceil", [value])


class Exp(Function):
    """Represents the exponential function."""

    def __init__(self, value: Expr):
        super().__init__("exp", [value])


class Floor(Function):
    """Represents the floor function."""

    def __init__(self, value: Expr):
        super().__init__("floor", [value])


class Ln(Function):
    """Represents the natural logarithm function."""

    def __init__(self, value: Expr):
        super().__init__("ln", [value])


class Log(Function):
    """Represents the logarithm function."""

    def __init__(self, value: Expr, base: Expr):
        super().__init__("log", [value, base])


class Pow(Function):
    """Represents the power function."""

    def __init__(self, base: Expr, exponent: Expr):
        super().__init__("pow", [base, exponent])


class Round(Function):
    """Represents the round function."""

    def __init__(self, value: Expr):
        super().__init__("round", [value])


class Sqrt(Function):
    """Represents the square root function."""

    def __init__(self, value: Expr):
        super().__init__("sqrt", [value])


class TimestampSubtract(Function):
    """Represents subtracting a duration from a timestamp."""

    def __init__(self, timestamp: Expr, unit: Expr, amount: Expr):
        super().__init__("timestamp_subtract", [timestamp, unit, amount])


class TimestampToUnixMicros(Function):
    """Represents converting a timestamp to microseconds since epoch."""

    def __init__(self, input: Expr):
        super().__init__("timestamp_to_unix_micros", [input])


class TimestampToUnixMillis(Function):
    """Represents converting a timestamp to milliseconds since epoch."""

    def __init__(self, input: Expr):
        super().__init__("timestamp_to_unix_millis", [input])


class TimestampToUnixSeconds(Function):
    """Represents converting a timestamp to seconds since epoch."""

    def __init__(self, input: Expr):
        super().__init__("timestamp_to_unix_seconds", [input])


class ToLower(Function):
    """Represents converting a string to lowercase."""

    def __init__(self, value: Expr):
        super().__init__("to_lower", [value])


class ToUpper(Function):
    """Represents converting a string to uppercase."""

    def __init__(self, value: Expr):
        super().__init__("to_upper", [value])


class Trim(Function):
    """Represents trimming whitespace from a string."""

    def __init__(self, expr: Expr):
        super().__init__("trim", [expr])


class UnixMicrosToTimestamp(Function):
    """Represents converting microseconds since epoch to a timestamp."""

    def __init__(self, input: Expr):
        super().__init__("unix_micros_to_timestamp", [input])


class UnixMillisToTimestamp(Function):
    """Represents converting milliseconds since epoch to a timestamp."""

    def __init__(self, input: Expr):
        super().__init__("unix_millis_to_timestamp", [input])


class UnixSecondsToTimestamp(Function):
    """Represents converting seconds since epoch to a timestamp."""

    def __init__(self, input: Expr):
        super().__init__("unix_seconds_to_timestamp", [input])


class VectorLength(Function):
    """Represents getting the length (dimension) of a vector."""

    def __init__(self, array: Expr):
        super().__init__("vector_length", [array])


class Add(Function):
    """Represents the addition function."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("add", [left, right])


class Array(Function):
    """Creates an expression that creates a Firestore array value from an input list."""

    def __init__(self, elements: list[Expr]):
        super().__init__("array", elements)

    def __repr__(self):
        return f"Array({self.params})"


class ArrayGet(Function):
    """Creates an expression that indexes into an array from the beginning or end and returns an element."""

    def __init__(self, array: Expr, index: Expr):
        super().__init__("array_get", [array, index])


class ArrayConcat(Function):
    """Represents concatenating multiple arrays."""

    def __init__(self, array: Expr, rest: Sequence[Expr]):
        super().__init__("array_concat", [array] + rest)


class ArrayLength(Function):
    """Represents getting the length of an array."""

    def __init__(self, array: Expr):
        super().__init__("array_length", [array])


class ArrayReverse(Function):
    """Represents reversing the elements of an array."""

    def __init__(self, array: Expr):
        super().__init__("array_reverse", [array])


class ByteLength(Function):
    """Represents getting the byte length of a string (UTF-8)."""

    def __init__(self, expr: Expr):
        super().__init__("byte_length", [expr])


class CharLength(Function):
    """Represents getting the character length of a string."""

    def __init__(self, expr: Expr):
        super().__init__("char_length", [expr])


class CollectionId(Function):
    """Represents getting the collection ID from a document reference."""

    def __init__(self, value: Expr):
        super().__init__("collection_id", [value])


class CosineDistance(Function):
    """Represents the vector cosine distance function."""

    def __init__(self, vector1: Expr, vector2: Expr):
        super().__init__("cosine_distance", [vector1, vector2])


class AggregateFunction(Function):
    """A base class for aggregation functions that operate across multiple inputs."""

    def as_(self, alias: str) -> "AliasedAggregate":
        """Assigns an alias to this expression.

        Aliases are useful for renaming fields in the output of a stage or for giving meaningful
        names to calculated values.

        Args:
            alias: The alias to assign to this expression.

        Returns: A new AliasedAggregate that wraps this expression and associates it with the
            provided alias.
        """
        return AliasedAggregate(self, alias)


class Maximum(AggregateFunction):
    """Finds the maximum value of a field, aggregated across multiple stage inputs."""

    def __init__(self, value: Expr):
        super().__init__("max", [value])


class Minimum(AggregateFunction):
    """Finds the maximum value of a field, aggregated across multiple stage inputs."""

    def __init__(self, value: Expr):
        super().__init__("min", [value])


class Sum(AggregateFunction):
    """Represents the sum aggregation function."""

    def __init__(self, value: Expr):
        super().__init__("sum", [value])


class Average(AggregateFunction):
    """Represents the average aggregation function."""

    def __init__(self, value: Expr):
        super().__init__("average", [value])


class Count(AggregateFunction):
    """Represents an aggregation that counts the total number of inputs."""

    def __init__(self, value: Expr | None = None):
        super().__init__("count", [value] if value else [])


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

    @staticmethod
    def _to_value(field_list: Sequence[Selectable]) -> Value:
        return Value(
            map_value={
                "fields": {m[0]: m[1] for m in [f._to_map() for f in field_list]}
            }
        )


T = TypeVar("T", bound=Expr)


class AliasedExpr(Selectable, Generic[T]):
    """Wraps an expression with an alias."""

    def __init__(self, expr: T, alias: str):
        self.expr = expr
        self.alias = alias

    def _to_map(self):
        return self.alias, self.expr._to_pb()

    def __repr__(self):
        return f"{self.expr}.as_('{self.alias}')"

    def _to_pb(self):
        return Value(map_value={"fields": {self.alias: self.expr._to_pb()}})


class AliasedAggregate:
    """Wraps an aggregate with an alias"""

    def __init__(self, expr: AggregateFunction, alias: str):
        self.expr = expr
        self.alias = alias

    def _to_map(self):
        return self.alias, self.expr._to_pb()

    def __repr__(self):
        return f"{self.expr}.as_('{self.alias}')"

    def _to_pb(self):
        return Value(map_value={"fields": {self.alias: self.expr._to_pb()}})


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


class BooleanExpr(Function):
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
        Most BooleanExprs can be triggered infix. Eg: Field.of('age').greater_than(18).

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
                BooleanExpr._from_query_filter_pb(f, client) for f in filter_pb.filters
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
                return And(field.exists(), field.equal(None))
            elif filter_pb.op == Query_pb.UnaryFilter.Operator.IS_NOT_NULL:
                return And(field.exists(), Not(field.equal(None)))
            else:
                raise TypeError(f"Unexpected UnaryFilter operator type: {filter_pb.op}")
        elif isinstance(filter_pb, Query_pb.FieldFilter):
            field = Field.of(filter_pb.field.field_path)
            value = decode_value(filter_pb.value, client)
            if filter_pb.op == Query_pb.FieldFilter.Operator.LESS_THAN:
                return And(field.exists(), field.less_than(value))
            elif filter_pb.op == Query_pb.FieldFilter.Operator.LESS_THAN_OR_EQUAL:
                return And(field.exists(), field.less_than_or_equal(value))
            elif filter_pb.op == Query_pb.FieldFilter.Operator.GREATER_THAN:
                return And(field.exists(), field.greater_than(value))
            elif filter_pb.op == Query_pb.FieldFilter.Operator.GREATER_THAN_OR_EQUAL:
                return And(field.exists(), field.greater_than_or_equal(value))
            elif filter_pb.op == Query_pb.FieldFilter.Operator.EQUAL:
                return And(field.exists(), field.equal(value))
            elif filter_pb.op == Query_pb.FieldFilter.Operator.NOT_EQUAL:
                return And(field.exists(), field.not_equal(value))
            if filter_pb.op == Query_pb.FieldFilter.Operator.ARRAY_CONTAINS:
                return And(field.exists(), field.array_contains(value))
            elif filter_pb.op == Query_pb.FieldFilter.Operator.ARRAY_CONTAINS_ANY:
                return And(field.exists(), field.array_contains_any(value))
            elif filter_pb.op == Query_pb.FieldFilter.Operator.IN:
                return And(field.exists(), field.equal_any(value))
            elif filter_pb.op == Query_pb.FieldFilter.Operator.NOT_IN:
                return And(field.exists(), field.not_equal_any(value))
            else:
                raise TypeError(f"Unexpected FieldFilter operator type: {filter_pb.op}")
        elif isinstance(filter_pb, Query_pb.Filter):
            # unwrap oneof
            f = (
                filter_pb.composite_filter
                or filter_pb.field_filter
                or filter_pb.unary_filter
            )
            return BooleanExpr._from_query_filter_pb(f, client)
        else:
            raise TypeError(f"Unexpected filter type: {type(filter_pb)}")


class And(BooleanExpr):
    def __init__(self, *conditions: "BooleanExpr"):
        super().__init__("and", conditions, use_infix_repr=False)


class ArrayContains(BooleanExpr):
    def __init__(self, array: Expr, element: Expr):
        super().__init__("array_contains", [array, element])


class ArrayContainsAll(BooleanExpr):
    """Represents checking if an array contains all specified elements."""

    def __init__(self, array: Expr, elements: Sequence[Expr]):
        super().__init__("array_contains_all", [array, ListOfExprs(elements)])


class ArrayContainsAny(BooleanExpr):
    """Represents checking if an array contains any of the specified elements."""

    def __init__(self, array: Expr, elements: Sequence[Expr]):
        super().__init__("array_contains_any", [array, ListOfExprs(elements)])


class EndsWith(BooleanExpr):
    """Represents checking if a string ends with a specific postfix."""

    def __init__(self, expr: Expr, postfix: Expr):
        super().__init__("ends_with", [expr, postfix])


class Equal(BooleanExpr):
    """Represents the equality comparison."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("equal", [left, right])


class Exists(BooleanExpr):
    """Represents checking if a field exists."""

    def __init__(self, expr: Expr):
        super().__init__("exists", [expr])


class GreaterThan(BooleanExpr):
    """Represents the greater than comparison."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("greater_than", [left, right])


class GreaterThanOrEqual(BooleanExpr):
    """Represents the greater than or equal to comparison."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("greater_than_or_equal", [left, right])


class Conditional(BooleanExpr):
    """Represents a conditional expression (if-then-else)."""

    def __init__(self, condition: "BooleanExpr", then_expr: Expr, else_expr: Expr):
        super().__init__("conditional", [condition, then_expr, else_expr])


class EqualAny(BooleanExpr):
    """Represents checking if an expression's value is within a list of values."""

    def __init__(self, left: Expr, others: Sequence[Expr]):
        super().__init__("equal_any", [left, ListOfExprs(others)])


class NotEqualAny(BooleanExpr):
    """Represents checking if an expression's value is not within a list of values."""

    def __init__(self, left: Expr, others: Sequence[Expr]):
        super().__init__("not_equal_any", [left, ListOfExprs(others)])


class IsNaN(BooleanExpr):
    """Represents checking if a numeric value is NaN."""

    def __init__(self, value: Expr):
        super().__init__("is_nan", [value])


class Like(BooleanExpr):
    """Represents a case-sensitive wildcard string comparison."""

    def __init__(self, expr: Expr, pattern: Expr):
        super().__init__("like", [expr, pattern])


class LessThan(BooleanExpr):
    """Represents the less than comparison."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("less_than", [left, right])


class LessThanOrEqual(BooleanExpr):
    """Represents the less than or equal to comparison."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("less_than_or_equal", [left, right])


class NotEqual(BooleanExpr):
    """Represents the inequality comparison."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("not_equal", [left, right])


class Not(BooleanExpr):
    """Represents the logical NOT of a filter condition."""

    def __init__(self, condition: Expr):
        super().__init__("not", [condition], use_infix_repr=False)


class Or(BooleanExpr):
    """Represents the logical OR of multiple filter conditions."""

    def __init__(self, *conditions: "BooleanExpr"):
        super().__init__("or", conditions)


class RegexContains(BooleanExpr):
    """Represents checking if a string contains a substring matching a regex."""

    def __init__(self, expr: Expr, regex: Expr):
        super().__init__("regex_contains", [expr, regex])


class RegexMatch(BooleanExpr):
    """Represents checking if a string fully matches a regex."""

    def __init__(self, expr: Expr, regex: Expr):
        super().__init__("regex_match", [expr, regex])


class StartsWith(BooleanExpr):
    """Represents checking if a string starts with a specific prefix."""

    def __init__(self, expr: Expr, prefix: Expr):
        super().__init__("starts_with", [expr, prefix])


class StringContains(BooleanExpr):
    """Represents checking if a string contains a specific substring."""

    def __init__(self, expr: Expr, substring: Expr):
        super().__init__("string_contains", [expr, substring])


class Xor(BooleanExpr):
    """Represents the logical XOR of multiple filter conditions."""

    def __init__(self, conditions: Sequence["BooleanExpr"]):
        super().__init__("xor", conditions, use_infix_repr=False)
