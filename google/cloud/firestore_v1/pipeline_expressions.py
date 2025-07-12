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

    def logical_max(self, other: Expr | CONSTANT_TYPE) -> "Expr":
        """Creates an expression that returns the larger value between this expression
        and another expression or constant, based on Firestore's value type ordering.

        Firestore's value type ordering is described here:
        https://cloud.google.com/firestore/docs/concepts/data-types#value_type_ordering

        Example:
            >>> # Returns the larger value between the 'discount' field and the 'cap' field.
            >>> Field.of("discount").logical_max(Field.of("cap"))
            >>> # Returns the larger value between the 'value' field and 10.
            >>> Field.of("value").logical_max(10)

        Args:
            other: The other expression or constant value to compare with.

        Returns:
            A new `Expr` representing the logical max operation.
        """
        return LogicalMax(self, self._cast_to_expr_or_convert_to_constant(other))

    def logical_min(self, other: Expr | CONSTANT_TYPE) -> "Expr":
        """Creates an expression that returns the smaller value between this expression
        and another expression or constant, based on Firestore's value type ordering.

        Firestore's value type ordering is described here:
        https://cloud.google.com/firestore/docs/concepts/data-types#value_type_ordering

        Example:
            >>> # Returns the smaller value between the 'discount' field and the 'floor' field.
            >>> Field.of("discount").logical_min(Field.of("floor"))
            >>> # Returns the smaller value between the 'value' field and 10.
            >>> Field.of("value").logical_min(10)

        Args:
            other: The other expression or constant value to compare with.

        Returns:
            A new `Expr` representing the logical min operation.
        """
        return LogicalMin(self, self._cast_to_expr_or_convert_to_constant(other))

    def eq(self, other: Expr | CONSTANT_TYPE) -> "BooleanExpr":
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

    def neq(self, other: Expr | CONSTANT_TYPE) -> "BooleanExpr":
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

    def gt(self, other: Expr | CONSTANT_TYPE) -> "BooleanExpr":
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

    def gte(self, other: Expr | CONSTANT_TYPE) -> "BooleanExpr":
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

    def lt(self, other: Expr | CONSTANT_TYPE) -> "BooleanExpr":
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

    def lte(self, other: Expr | CONSTANT_TYPE) -> "BooleanExpr":
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

    def in_any(self, array: Sequence[Expr | CONSTANT_TYPE]) -> "BooleanExpr":
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

    def not_in_any(self, array: Sequence[Expr | CONSTANT_TYPE]) -> "BooleanExpr":
        """Creates an expression that checks if this expression is not equal to any of the
        provided values or expressions.

        Example:
            >>> # Check if the 'status' field is neither "pending" nor "cancelled"
            >>> Field.of("status").not_in_any(["pending", "cancelled"])

        Args:
            *array: The values or expressions to check against.

        Returns:
            A new `Expr` representing the 'NOT IN' comparison.
        """
        return Not(self.in_any(array))

    def array_concat(self, array: List[Expr | CONSTANT_TYPE]) -> "Expr":
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

    def array_length(self) -> "Expr":
        """Creates an expression that calculates the length of an array.

        Example:
            >>> # Get the number of items in the 'cart' array
            >>> Field.of("cart").array_length()

        Returns:
            A new `Expr` representing the length of the array.
        """
        return ArrayLength(self)

    def array_reverse(self) -> "Expr":
        """Creates an expression that returns the reversed content of an array.

        Example:
            >>> # Get the 'preferences' array in reversed order.
            >>> Field.of("preferences").array_reverse()

        Returns:
            A new `Expr` representing the reversed array.
        """
        return ArrayReverse(self)

    def is_nan(self) -> "BooleanExpr":
        """Creates an expression that checks if this expression evaluates to 'NaN' (Not a Number).

        Example:
            >>> # Check if the result of a calculation is NaN
            >>> Field.of("value").divide(0).is_nan()

        Returns:
            A new `Expr` representing the 'isNaN' check.
        """
        return IsNaN(self)

    def exists(self) -> "BooleanExpr":
        """Creates an expression that checks if a field exists in the document.

        Example:
            >>> # Check if the document has a field named "phoneNumber"
            >>> Field.of("phoneNumber").exists()

        Returns:
            A new `Expr` representing the 'exists' check.
        """
        return Exists(self)

    def sum(self) -> "Expr":
        """Creates an aggregation that calculates the sum of a numeric field across multiple stage inputs.

        Example:
            >>> # Calculate the total revenue from a set of orders
            >>> Field.of("orderAmount").sum().as_("totalRevenue")

        Returns:
            A new `AggregateFunction` representing the 'sum' aggregation.
        """
        return Sum(self)

    def avg(self) -> "Expr":
        """Creates an aggregation that calculates the average (mean) of a numeric field across multiple
        stage inputs.

        Example:
            >>> # Calculate the average age of users
            >>> Field.of("age").avg().as_("averageAge")

        Returns:
            A new `AggregateFunction` representing the 'avg' aggregation.
        """
        return Avg(self)

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

    def min(self) -> "Expr":
        """Creates an aggregation that finds the minimum value of a field across multiple stage inputs.

        Example:
            >>> # Find the lowest price of all products
            >>> Field.of("price").min().as_("lowestPrice")

        Returns:
            A new `AggregateFunction` representing the 'min' aggregation.
        """
        return Min(self)

    def max(self) -> "Expr":
        """Creates an aggregation that finds the maximum value of a field across multiple stage inputs.

        Example:
            >>> # Find the highest score in a leaderboard
            >>> Field.of("score").max().as_("highestScore")

        Returns:
            A new `AggregateFunction` representing the 'max' aggregation.
        """
        return Max(self)

    def char_length(self) -> "Expr":
        """Creates an expression that calculates the character length of a string.

        Example:
            >>> # Get the character length of the 'name' field
            >>> Field.of("name").char_length()

        Returns:
            A new `Expr` representing the length of the string.
        """
        return CharLength(self)

    def byte_length(self) -> "Expr":
        """Creates an expression that calculates the byte length of a string in its UTF-8 form.

        Example:
            >>> # Get the byte length of the 'name' field
            >>> Field.of("name").byte_length()

        Returns:
            A new `Expr` representing the byte length of the string.
        """
        return ByteLength(self)

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

    def str_contains(self, substring: Expr | str) -> "BooleanExpr":
        """Creates an expression that checks if this string expression contains a specified substring.

        Example:
            >>> # Check if the 'description' field contains "example".
            >>> Field.of("description").str_contains("example")
            >>> # Check if the 'description' field contains the value of the 'keyword' field.
            >>> Field.of("description").str_contains(Field.of("keyword"))

        Args:
            substring: The substring (string or expression) to use for the search.

        Returns:
            A new `Expr` representing the 'contains' comparison.
        """
        return StrContains(self, self._cast_to_expr_or_convert_to_constant(substring))

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

    def str_concat(self, *elements: Expr | CONSTANT_TYPE) -> "Expr":
        """Creates an expression that concatenates string expressions, fields or constants together.

        Example:
            >>> # Combine the 'firstName', " ", and 'lastName' fields into a single string
            >>> Field.of("firstName").str_concat(" ", Field.of("lastName"))

        Args:
            *elements: The expressions or constants (typically strings) to concatenate.

        Returns:
            A new `Expr` representing the concatenated string.
        """
        return StrConcat(
            self, *[self._cast_to_expr_or_convert_to_constant(el) for el in elements]
        )

    def to_lower(self) -> "Expr":
        """Creates an expression that converts a string to lowercase.

        Example:
            >>> # Convert the 'name' field to lowercase
            >>> Field.of("name").to_lower()

        Returns:
            A new `Expr` representing the lowercase string.
        """
        return ToLower(self)

    def to_upper(self) -> "Expr":
        """Creates an expression that converts a string to uppercase.

        Example:
            >>> # Convert the 'title' field to uppercase
            >>> Field.of("title").to_upper()

        Returns:
            A new `Expr` representing the uppercase string.
        """
        return ToUpper(self)

    def trim(self) -> "Expr":
        """Creates an expression that removes leading and trailing whitespace from a string.

        Example:
            >>> # Trim whitespace from the 'userInput' field
            >>> Field.of("userInput").trim()

        Returns:
            A new `Expr` representing the trimmed string.
        """
        return Trim(self)

    def reverse(self) -> "Expr":
        """Creates an expression that reverses a string.

        Example:
            >>> # Reverse the 'userInput' field
            >>> Field.of("userInput").reverse()

        Returns:
            A new `Expr` representing the reversed string.
        """
        return Reverse(self)

    def replace_first(self, find: Expr | str, replace: Expr | str) -> "Expr":
        """Creates an expression that replaces the first occurrence of a substring within a string with
        another substring.

        Example:
            >>> # Replace the first occurrence of "hello" with "hi" in the 'message' field
            >>> Field.of("message").replace_first("hello", "hi")
            >>> # Replace the first occurrence of the value in 'findField' with the value in 'replaceField' in the 'message' field
            >>> Field.of("message").replace_first(Field.of("findField"), Field.of("replaceField"))

        Args:
            find: The substring (string or expression) to search for.
            replace: The substring (string or expression) to replace the first occurrence of 'find' with.

        Returns:
            A new `Expr` representing the string with the first occurrence replaced.
        """
        return ReplaceFirst(
            self,
            self._cast_to_expr_or_convert_to_constant(find),
            self._cast_to_expr_or_convert_to_constant(replace),
        )

    def replace_all(self, find: Expr | str, replace: Expr | str) -> "Expr":
        """Creates an expression that replaces all occurrences of a substring within a string with another
        substring.

        Example:
            >>> # Replace all occurrences of "hello" with "hi" in the 'message' field
            >>> Field.of("message").replace_all("hello", "hi")
            >>> # Replace all occurrences of the value in 'findField' with the value in 'replaceField' in the 'message' field
            >>> Field.of("message").replace_all(Field.of("findField"), Field.of("replaceField"))

        Args:
            find: The substring (string or expression) to search for.
            replace: The substring (string or expression) to replace all occurrences of 'find' with.

        Returns:
            A new `Expr` representing the string with all occurrences replaced.
        """
        return ReplaceAll(
            self,
            self._cast_to_expr_or_convert_to_constant(find),
            self._cast_to_expr_or_convert_to_constant(replace),
        )

    def map_get(self, key: str) -> "Expr":
        """Accesses a value from a map (object) field using the provided key.

        Example:
            >>> # Get the 'city' value from
            >>> # the 'address' map field
            >>> Field.of("address").map_get("city")

        Args:
            key: The key to access in the map.

        Returns:
            A new `Expr` representing the value associated with the given key in the map.
        """
        return MapGet(self, Constant.of(key))

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

    def euclidean_distance(
        self, other: Expr | list[float] | Vector
    ) -> "Expr":
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

    def vector_length(self) -> "Expr":
        """Creates an expression that calculates the length (dimension) of a Firestore Vector.

        Example:
            >>> # Get the vector length (dimension) of the field 'embedding'.
            >>> Field.of("embedding").vector_length()

        Returns:
            A new `Expr` representing the length of the vector.
        """
        return VectorLength(self)

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

    def timestamp_sub(self, unit: Expr | str, amount: Expr | float) -> "Expr":
        """Creates an expression that subtracts a specified amount of time from this timestamp expression.

        Example:
            >>> # Subtract a duration specified by the 'unit' and 'amount' fields from the 'timestamp' field.
            >>> Field.of("timestamp").timestamp_sub(Field.of("unit"), Field.of("amount"))
            >>> # Subtract 2.5 hours from the 'timestamp' field.
            >>> Field.of("timestamp").timestamp_sub("hour", 2.5)

        Args:
            unit: The expression or string evaluating to the unit of time to subtract, must be one of
                  'microsecond', 'millisecond', 'second', 'minute', 'hour', 'day'.
            amount: The expression or float representing the amount of time to subtract.

        Returns:
            A new `Expr` representing the resulting timestamp.
        """
        return TimestampSub(
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

    def add(left: Expr | str, right: Expr | float) -> "Expr":
        """Creates an expression that adds two expressions together.

        Example:
            >>> Function.add("rating", 5)
            >>> Function.add(Field.of("quantity"), Field.of("reserve"))

        Args:
            left: The first expression or field path to add.
            right: The second expression or constant value to add.

        Returns:
            A new `Expr` representing the addition operation.
        """
        left_expr = Field.of(left) if isinstance(left, str) else left
        return Expr.add(left_expr, right)

    def subtract(left: Expr | str, right: Expr | float) -> "Expr":
        """Creates an expression that subtracts another expression or constant from this expression.

        Example:
            >>> Function.subtract("total", 20)
            >>> Function.subtract(Field.of("price"), Field.of("discount"))

        Args:
            left: The expression or field path to subtract from.
            right: The expression or constant value to subtract.

        Returns:
            A new `Expr` representing the subtraction operation.
        """
        left_expr = Field.of(left) if isinstance(left, str) else left
        return Expr.subtract(left_expr, right)

    def multiply(left: Expr | str, right: Expr | float) -> "Expr":
        """Creates an expression that multiplies this expression by another expression or constant.

        Example:
            >>> Function.multiply("value", 2)
            >>> Function.multiply(Field.of("quantity"), Field.of("price"))

        Args:
            left: The expression or field path to multiply.
            right: The expression or constant value to multiply by.

        Returns:
            A new `Expr` representing the multiplication operation.
        """
        left_expr = Field.of(left) if isinstance(left, str) else left
        return Expr.multiply(left_expr, right)

    def divide(left: Expr | str, right: Expr | float) -> "Expr":
        """Creates an expression that divides this expression by another expression or constant.

        Example:
            >>> Function.divide("value", 10)
            >>> Function.divide(Field.of("total"), Field.of("count"))

        Args:
            left: The expression or field path to be divided.
            right: The expression or constant value to divide by.

        Returns:
            A new `Expr` representing the division operation.
        """
        left_expr = Field.of(left) if isinstance(left, str) else left
        return Expr.divide(left_expr, right)

    def mod(left: Expr | str, right: Expr | float) -> "Expr":
        """Creates an expression that calculates the modulo (remainder) to another expression or constant.

        Example:
            >>> Function.mod("value", 5)
            >>> Function.mod(Field.of("value"), Field.of("divisor"))

        Args:
            left: The dividend expression or field path.
            right: The divisor expression or constant.

        Returns:
            A new `Expr` representing the modulo operation.
        """
        left_expr = Field.of(left) if isinstance(left, str) else left
        return Expr.mod(left_expr, right)

    def logical_max(left: Expr | str, right: Expr | CONSTANT_TYPE) -> "Expr":
        """Creates an expression that returns the larger value between this expression
        and another expression or constant, based on Firestore's value type ordering.

        Firestore's value type ordering is described here:
        https://cloud.google.com/firestore/docs/concepts/data-types#value_type_ordering

        Example:
            >>> Function.logical_max("value", 10)
            >>> Function.logical_max(Field.of("discount"), Field.of("cap"))

        Args:
            left: The expression or field path to compare.
            right: The other expression or constant value to compare with.

        Returns:
            A new `Expr` representing the logical max operation.
        """
        left_expr = Field.of(left) if isinstance(left, str) else left
        return Expr.logical_max(left_expr, right)

    def logical_min(left: Expr | str, right: Expr | CONSTANT_TYPE) -> "Expr":
        """Creates an expression that returns the smaller value between this expression
        and another expression or constant, based on Firestore's value type ordering.

        Firestore's value type ordering is described here:
        https://cloud.google.com/firestore/docs/concepts/data-types#value_type_ordering

        Example:
            >>> Function.logical_min("value", 10)
            >>> Function.logical_min(Field.of("discount"), Field.of("floor"))

        Args:
            left: The expression or field path to compare.
            right: The other expression or constant value to compare with.

        Returns:
            A new `Expr` representing the logical min operation.
        """
        left_expr = Field.of(left) if isinstance(left, str) else left
        return Expr.logical_min(left_expr, right)

    def eq(left: Expr | str, right: Expr | CONSTANT_TYPE) -> "BooleanExpr":
        """Creates an expression that checks if this expression is equal to another
        expression or constant value.

        Example:
            >>> Function.eq("city", "London")
            >>> Function.eq(Field.of("age"), 21)

        Args:
            left: The expression or field path to compare.
            right: The expression or constant value to compare for equality.

        Returns:
            A new `Expr` representing the equality comparison.
        """
        left_expr = Field.of(left) if isinstance(left, str) else left
        return Expr.eq(left_expr, right)

    def neq(left: Expr | str, right: Expr | CONSTANT_TYPE) -> "BooleanExpr":
        """Creates an expression that checks if this expression is not equal to another
        expression or constant value.

        Example:
            >>> Function.neq("country", "USA")
            >>> Function.neq(Field.of("status"), "completed")

        Args:
            left: The expression or field path to compare.
            right: The expression or constant value to compare for inequality.

        Returns:
            A new `Expr` representing the inequality comparison.
        """
        left_expr = Field.of(left) if isinstance(left, str) else left
        return Expr.neq(left_expr, right)

    def gt(left: Expr | str, right: Expr | CONSTANT_TYPE) -> "BooleanExpr":
        """Creates an expression that checks if this expression is greater than another
        expression or constant value.

        Example:
            >>> Function.gt("price", 100)
            >>> Function.gt(Field.of("age"), Field.of("limit"))

        Args:
            left: The expression or field path to compare.
            right: The expression or constant value to compare for greater than.

        Returns:
            A new `Expr` representing the greater than comparison.
        """
        left_expr = Field.of(left) if isinstance(left, str) else left
        return Expr.gt(left_expr, right)

    def gte(left: Expr | str, right: Expr | CONSTANT_TYPE) -> "BooleanExpr":
        """Creates an expression that checks if this expression is greater than or equal
        to another expression or constant value.

        Example:
            >>> Function.gte("score", 80)
            >>> Function.gte(Field.of("quantity"), Field.of('requirement').add(1))

        Args:
            left: The expression or field path to compare.
            right: The expression or constant value to compare for greater than or equal to.

        Returns:
            A new `Expr` representing the greater than or equal to comparison.
        """
        left_expr = Field.of(left) if isinstance(left, str) else left
        return Expr.gte(left_expr, right)

    def lt(left: Expr | str, right: Expr | CONSTANT_TYPE) -> "BooleanExpr":
        """Creates an expression that checks if this expression is less than another
        expression or constant value.

        Example:
            >>> Function.lt("price", 50)
            >>> Function.lt(Field.of("age"), Field.of('limit'))

        Args:
            left: The expression or field path to compare.
            right: The expression or constant value to compare for less than.

        Returns:
            A new `Expr` representing the less than comparison.
        """
        left_expr = Field.of(left) if isinstance(left, str) else left
        return Expr.lt(left_expr, right)

    def lte(left: Expr | str, right: Expr | CONSTANT_TYPE) -> "BooleanExpr":
        """Creates an expression that checks if this expression is less than or equal to
        another expression or constant value.

        Example:
            >>> Function.lte("score", 70)
            >>> Function.lte(Field.of("quantity"), Constant.of(20))

        Args:
            left: The expression or field path to compare.
            right: The expression or constant value to compare for less than or equal to.

        Returns:
            A new `Expr` representing the less than or equal to comparison.
        """
        left_expr = Field.of(left) if isinstance(left, str) else left
        return Expr.lte(left_expr, right)

    def in_any(left: Expr | str, array: List[Expr | CONSTANT_TYPE]) -> "BooleanExpr":
        """Creates an expression that checks if this expression is equal to any of the
        provided values or expressions.

        Example:
            >>> Function.in_any("category", ["Electronics", "Apparel"])
            >>> Function.in_any(Field.of("category"), ["Electronics", Field.of("primaryType")])

        Args:
            left: The expression or field path to compare.
            array: The values or expressions to check against.

        Returns:
            A new `Expr` representing the 'IN' comparison.
        """
        left_expr = Field.of(left) if isinstance(left, str) else left
        return Expr.in_any(left_expr, array)

    def not_in_any(left: Expr | str, array: List[Expr | CONSTANT_TYPE]) -> "BooleanExpr":
        """Creates an expression that checks if this expression is not equal to any of the
        provided values or expressions.

        Example:
            >>> Function.not_in_any("status", ["pending", "cancelled"])

        Args:
            left: The expression or field path to compare.
            array: The values or expressions to check against.

        Returns:
            A new `Expr` representing the 'NOT IN' comparison.
        """
        left_expr = Field.of(left) if isinstance(left, str) else left
        return Expr.not_in_any(left_expr, array)

    def array_contains(
        array: Expr | str, element: Expr | CONSTANT_TYPE
    ) -> "BooleanExpr":
        """Creates an expression that checks if an array contains a specific element or value.

        Example:
            >>> Function.array_contains("colors", "red")
            >>> Function.array_contains(Field.of("sizes"), Field.of("selectedSize"))

        Args:
            array: The array expression or field path to check.
            element: The element (expression or constant) to search for in the array.

        Returns:
            A new `Expr` representing the 'array_contains' comparison.
        """
        array_expr = Field.of(array) if isinstance(array, str) else array
        return Expr.array_contains(array_expr, element)

    def array_contains_all(
        array: Expr | str, elements: List[Expr | CONSTANT_TYPE]
    ) -> "BooleanExpr":
        """Creates an expression that checks if an array contains all the specified elements.

        Example:
            >>> Function.array_contains_all("tags", ["news", "sports"])
            >>> Function.array_contains_all(Field.of("tags"), [Field.of("tag1"), "tag2"])

        Args:
            array: The array expression or field path to check.
            elements: The list of elements (expressions or constants) to check for in the array.

        Returns:
            A new `Expr` representing the 'array_contains_all' comparison.
        """
        array_expr = Field.of(array) if isinstance(array, str) else array
        return Expr.array_contains_all(array_expr, elements)

    def array_contains_any(
        array: Expr | str, elements: List[Expr | CONSTANT_TYPE]
    ) -> "BooleanExpr":
        """Creates an expression that checks if an array contains any of the specified elements.

        Example:
            >>> Function.array_contains_any("groups", ["admin", "editor"])
            >>> Function.array_contains_any(Field.of("categories"), [Field.of("cate1"), Field.of("cate2")])

        Args:
            array: The array expression or field path to check.
            elements: The list of elements (expressions or constants) to check for in the array.

        Returns:
            A new `Expr` representing the 'array_contains_any' comparison.
        """
        array_expr = Field.of(array) if isinstance(array, str) else array
        return Expr.array_contains_any(array_expr, elements)

    def array_length(array: Expr | str) -> "Expr":
        """Creates an expression that calculates the length of an array.

        Example:
            >>> Function.array_length("cart")

        Returns:
            A new `Expr` representing the length of the array.
        """
        array_expr = Field.of(array) if isinstance(array, str) else array
        return Expr.array_length(array_expr)

    def array_reverse(array: Expr | str) -> "Expr":
        """Creates an expression that returns the reversed content of an array.

        Example:
            >>> Function.array_reverse("preferences")

        Returns:
            A new `Expr` representing the reversed array.
        """
        array_expr = Field.of(array) if isinstance(array, str) else array
        return Expr.array_reverse(array_expr)

    def is_nan(expr: Expr | str) -> "BooleanExpr":
        """Creates an expression that checks if this expression evaluates to 'NaN' (Not a Number).

        Example:
            >>> Function.is_nan("measurement")

        Returns:
            A new `Expr` representing the 'isNaN' check.
        """
        expr_val = Field.of(expr) if isinstance(expr, str) else expr
        return Expr.is_nan(expr_val)

    def exists(expr: Expr | str) -> "BooleanExpr":
        """Creates an expression that checks if a field exists in the document.

        Example:
            >>> Function.exists("phoneNumber")

        Returns:
            A new `Expr` representing the 'exists' check.
        """
        expr_val = Field.of(expr) if isinstance(expr, str) else expr
        return Expr.exists(expr_val)

    def sum(expr: Expr | str) -> "Expr":
        """Creates an aggregation that calculates the sum of a numeric field across multiple stage inputs.

        Example:
            >>> Function.sum("orderAmount")

        Returns:
            A new `AggregateFunction` representing the 'sum' aggregation.
        """
        expr_val = Field.of(expr) if isinstance(expr, str) else expr
        return Expr.sum(expr_val)

    def avg(expr: Expr | str) -> "Expr":
        """Creates an aggregation that calculates the average (mean) of a numeric field across multiple
        stage inputs.

        Example:
            >>> Function.avg("age")

        Returns:
            A new `AggregateFunction` representing the 'avg' aggregation.
        """
        expr_val = Field.of(expr) if isinstance(expr, str) else expr
        return Expr.avg(expr_val)

    def count(expr: Expr | str | None = None) -> "Expr":
        """Creates an aggregation that counts the number of stage inputs with valid evaluations of the
        expression or field. If no expression is provided, it counts all inputs.

        Example:
            >>> Function.count("productId")
            >>> Function.count()

        Returns:
            A new `AggregateFunction` representing the 'count' aggregation.
        """
        if expr is None:
            return Count()
        expr_val = Field.of(expr) if isinstance(expr, str) else expr
        return Expr.count(expr_val)

    def min(expr: Expr | str) -> "Expr":
        """Creates an aggregation that finds the minimum value of a field across multiple stage inputs.

        Example:
            >>> Function.min("price")

        Returns:
            A new `AggregateFunction` representing the 'min' aggregation.
        """
        expr_val = Field.of(expr) if isinstance(expr, str) else expr
        return Expr.min(expr_val)

    def max(expr: Expr | str) -> "Expr":
        """Creates an aggregation that finds the maximum value of a field across multiple stage inputs.

        Example:
            >>> Function.max("score")

        Returns:
            A new `AggregateFunction` representing the 'max' aggregation.
        """
        expr_val = Field.of(expr) if isinstance(expr, str) else expr
        return Expr.max(expr_val)

    def char_length(expr: Expr | str) -> "Expr":
        """Creates an expression that calculates the character length of a string.

        Example:
            >>> Function.char_length("name")

        Returns:
            A new `Expr` representing the length of the string.
        """
        expr_val = Field.of(expr) if isinstance(expr, str) else expr
        return Expr.char_length(expr_val)

    def byte_length(expr: Expr | str) -> "Expr":
        """Creates an expression that calculates the byte length of a string in its UTF-8 form.

        Example:
            >>> Function.byte_length("name")

        Returns:
            A new `Expr` representing the byte length of the string.
        """
        expr_val = Field.of(expr) if isinstance(expr, str) else expr
        return Expr.byte_length(expr_val)

    def like(expr: Expr | str, pattern: Expr | str) -> "BooleanExpr":
        """Creates an expression that performs a case-sensitive string comparison.

        Example:
            >>> Function.like("title", "%guide%")
            >>> Function.like(Field.of("title"), Field.of("pattern"))

        Args:
            expr: The expression or field path to perform the comparison on.
            pattern: The pattern (string or expression) to search for. You can use "%" as a wildcard character.

        Returns:
            A new `Expr` representing the 'like' comparison.
        """
        expr_val = Field.of(expr) if isinstance(expr, str) else expr
        return Expr.like(expr_val, pattern)

    def regex_contains(expr: Expr | str, regex: Expr | str) -> "BooleanExpr":
        """Creates an expression that checks if a string contains a specified regular expression as a
        substring.

        Example:
            >>> Function.regex_contains("description", "(?i)example")
            >>> Function.regex_contains(Field.of("description"), Field.of("regex"))

        Args:
            expr: The expression or field path to perform the comparison on.
            regex: The regular expression (string or expression) to use for the search.

        Returns:
            A new `Expr` representing the 'contains' comparison.
        """
        expr_val = Field.of(expr) if isinstance(expr, str) else expr
        return Expr.regex_contains(expr_val, regex)

    def regex_matches(expr: Expr | str, regex: Expr | str) -> "BooleanExpr":
        """Creates an expression that checks if a string matches a specified regular expression.

        Example:
            >>> # Check if the 'email' field matches a valid email pattern
            >>> Function.regex_matches("email", "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}")
            >>> Function.regex_matches(Field.of("email"), Field.of("regex"))

        Args:
            expr: The expression or field path to match against.
            regex: The regular expression (string or expression) to use for the match.

        Returns:
            A new `Expr` representing the regular expression match.
        """
        expr_val = Field.of(expr) if isinstance(expr, str) else expr
        return Expr.regex_matches(expr_val, regex)

    def str_contains(expr: Expr | str, substring: Expr | str) -> "BooleanExpr":
        """Creates an expression that checks if this string expression contains a specified substring.

        Example:
            >>> Function.str_contains("description", "example")
            >>> Function.str_contains(Field.of("description"), Field.of("keyword"))

        Args:
            expr: The expression or field path to perform the comparison on.
            substring: The substring (string or expression) to use for the search.

        Returns:
            A new `Expr` representing the 'contains' comparison.
        """
        expr_val = Field.of(expr) if isinstance(expr, str) else expr
        return Expr.str_contains(expr_val, substring)

    def starts_with(expr: Expr | str, prefix: Expr | str) -> "BooleanExpr":
        """Creates an expression that checks if a string starts with a given prefix.

        Example:
            >>> Function.starts_with("name", "Mr.")
            >>> Function.starts_with(Field.of("fullName"), Field.of("firstName"))

        Args:
            expr: The expression or field path to check.
            prefix: The prefix (string or expression) to check for.

        Returns:
            A new `Expr` representing the 'starts with' comparison.
        """
        expr_val = Field.of(expr) if isinstance(expr, str) else expr
        return Expr.starts_with(expr_val, prefix)

    def ends_with(expr: Expr | str, postfix: Expr | str) -> "BooleanExpr":
        """Creates an expression that checks if a string ends with a given postfix.

        Example:
            >>> Function.ends_with("filename", ".txt")
            >>> Function.ends_with(Field.of("url"), Field.of("extension"))

        Args:
            expr: The expression or field path to check.
            postfix: The postfix (string or expression) to check for.

        Returns:
            A new `Expr` representing the 'ends with' comparison.
        """
        expr_val = Field.of(expr) if isinstance(expr, str) else expr
        return Expr.ends_with(expr_val, postfix)

    def str_concat(first: Expr | str, *elements: Expr | CONSTANT_TYPE) -> "Expr":
        """Creates an expression that concatenates string expressions, fields or constants together.

        Example:
            >>> Function.str_concat("firstName", " ", Field.of("lastName"))

        Args:
            first: The first expression or field path to concatenate.
            *elements: The expressions or constants (typically strings) to concatenate.

        Returns:
            A new `Expr` representing the concatenated string.
        """
        first_expr = Field.of(first) if isinstance(first, str) else first
        return Expr.str_concat(first_expr, *elements)

    def map_get(map_expr: Expr | str, key: str) -> "Expr":
        """Accesses a value from a map (object) field using the provided key.

        Example:
            >>> Function.map_get("address", "city")

        Args:
            map_expr: The expression or field path of the map.
            key: The key to access in the map.

        Returns:
            A new `Expr` representing the value associated with the given key in the map.
        """
        map_val = Field.of(map_expr) if isinstance(map_expr, str) else map_expr
        return Expr.map_get(map_val, key)

    def vector_length(vector_expr: Expr | str) -> "Expr":
        """Creates an expression that calculates the length (dimension) of a Firestore Vector.

        Example:
            >>> Function.vector_length("embedding")

        Returns:
            A new `Expr` representing the length of the vector.
        """
        vector_val = (
            Field.of(vector_expr) if isinstance(vector_expr, str) else vector_expr
        )
        return Expr.vector_length(vector_val)

    def timestamp_to_unix_micros(timestamp_expr: Expr | str) -> "Expr":
        """Creates an expression that converts a timestamp to the number of microseconds since the epoch
        (1970-01-01 00:00:00 UTC).

        Truncates higher levels of precision by rounding down to the beginning of the microsecond.

        Example:
            >>> Function.timestamp_to_unix_micros("timestamp")

        Returns:
            A new `Expr` representing the number of microseconds since the epoch.
        """
        timestamp_val = (
            Field.of(timestamp_expr)
            if isinstance(timestamp_expr, str)
            else timestamp_expr
        )
        return Expr.timestamp_to_unix_micros(timestamp_val)

    def unix_micros_to_timestamp(micros_expr: Expr | str) -> "Expr":
        """Creates an expression that converts a number of microseconds since the epoch (1970-01-01
        00:00:00 UTC) to a timestamp.

        Example:
            >>> Function.unix_micros_to_timestamp("microseconds")

        Returns:
            A new `Expr` representing the timestamp.
        """
        micros_val = (
            Field.of(micros_expr) if isinstance(micros_expr, str) else micros_expr
        )
        return Expr.unix_micros_to_timestamp(micros_val)

    def timestamp_to_unix_millis(timestamp_expr: Expr | str) -> "Expr":
        """Creates an expression that converts a timestamp to the number of milliseconds since the epoch
        (1970-01-01 00:00:00 UTC).

        Truncates higher levels of precision by rounding down to the beginning of the millisecond.

        Example:
            >>> Function.timestamp_to_unix_millis("timestamp")

        Returns:
            A new `Expr` representing the number of milliseconds since the epoch.
        """
        timestamp_val = (
            Field.of(timestamp_expr)
            if isinstance(timestamp_expr, str)
            else timestamp_expr
        )
        return Expr.timestamp_to_unix_millis(timestamp_val)

    def unix_millis_to_timestamp(millis_expr: Expr | str) -> "Expr":
        """Creates an expression that converts a number of milliseconds since the epoch (1970-01-01
        00:00:00 UTC) to a timestamp.

        Example:
            >>> Function.unix_millis_to_timestamp("milliseconds")

        Returns:
            A new `Expr` representing the timestamp.
        """
        millis_val = (
            Field.of(millis_expr) if isinstance(millis_expr, str) else millis_expr
        )
        return Expr.unix_millis_to_timestamp(millis_val)

    def timestamp_to_unix_seconds(
        timestamp_expr: Expr | str,
    ) -> "Expr":
        """Creates an expression that converts a timestamp to the number of seconds since the epoch
        (1970-01-01 00:00:00 UTC).

        Truncates higher levels of precision by rounding down to the beginning of the second.

        Example:
            >>> Function.timestamp_to_unix_seconds("timestamp")

        Returns:
            A new `Expr` representing the number of seconds since the epoch.
        """
        timestamp_val = (
            Field.of(timestamp_expr)
            if isinstance(timestamp_expr, str)
            else timestamp_expr
        )
        return Expr.timestamp_to_unix_seconds(timestamp_val)

    def unix_seconds_to_timestamp(seconds_expr: Expr | str) -> "Expr":
        """Creates an expression that converts a number of seconds since the epoch (1970-01-01 00:00:00
        UTC) to a timestamp.

        Example:
            >>> Function.unix_seconds_to_timestamp("seconds")

        Returns:
            A new `Expr` representing the timestamp.
        """
        seconds_val = (
            Field.of(seconds_expr) if isinstance(seconds_expr, str) else seconds_expr
        )
        return Expr.unix_seconds_to_timestamp(seconds_val)

    def timestamp_add(
        timestamp: Expr | str, unit: Expr | str, amount: Expr | float
    ) -> "Expr":
        """Creates an expression that adds a specified amount of time to this timestamp expression.

        Example:
            >>> Function.timestamp_add("timestamp", "day", 1.5)
            >>> Function.timestamp_add(Field.of("timestamp"), Field.of("unit"), Field.of("amount"))

        Args:
            timestamp: The expression or field path of the timestamp.
            unit: The expression or string evaluating to the unit of time to add, must be one of
                  'microsecond', 'millisecond', 'second', 'minute', 'hour', 'day'.
            amount: The expression or float representing the amount of time to add.

        Returns:
            A new `Expr` representing the resulting timestamp.
        """
        timestamp_expr = (
            Field.of(timestamp) if isinstance(timestamp, str) else timestamp
        )
        return Expr.timestamp_add(timestamp_expr, unit, amount)

    def timestamp_sub(
        timestamp: Expr | str, unit: Expr | str, amount: Expr | float
    ) -> "Expr":
        """Creates an expression that subtracts a specified amount of time from this timestamp expression.

        Example:
            >>> Function.timestamp_sub("timestamp", "hour", 2.5)
            >>> Function.timestamp_sub(Field.of("timestamp"), Field.of("unit"), Field.of("amount"))

        Args:
            timestamp: The expression or field path of the timestamp.
            unit: The expression or string evaluating to the unit of time to subtract, must be one of
                  'microsecond', 'millisecond', 'second', 'minute', 'hour', 'day'.
            amount: The expression or float representing the amount of time to subtract.

        Returns:
            A new `Expr` representing the resulting timestamp.
        """
        timestamp_expr = (
            Field.of(timestamp) if isinstance(timestamp, str) else timestamp
        )
        return Expr.timestamp_sub(timestamp_expr, unit, amount)


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


class LogicalMax(Function):
    """Represents the logical maximum function based on Firestore type ordering."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("logical_maximum", [left, right])


class LogicalMin(Function):
    """Represents the logical minimum function based on Firestore type ordering."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("logical_minimum", [left, right])


class MapGet(Function):
    """Represents accessing a value within a map by key."""

    def __init__(self, map_: Expr, key: Constant[str]):
        super().__init__("map_get", [map_, key])


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


class ReplaceAll(Function):
    """Represents replacing all occurrences of a substring."""

    def __init__(self, value: Expr, pattern: Expr, replacement: Expr):
        super().__init__("replace_all", [value, pattern, replacement])


class ReplaceFirst(Function):
    """Represents replacing the first occurrence of a substring."""

    def __init__(self, value: Expr, pattern: Expr, replacement: Expr):
        super().__init__("replace_first", [value, pattern, replacement])


class Reverse(Function):
    """Represents reversing a string."""

    def __init__(self, expr: Expr):
        super().__init__("reverse", [expr])


class StrConcat(Function):
    """Represents concatenating multiple strings."""

    def __init__(self, *exprs: Expr):
        super().__init__("str_concat", exprs)


class Subtract(Function):
    """Represents the subtraction function."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("subtract", [left, right])


class TimestampAdd(Function):
    """Represents adding a duration to a timestamp."""

    def __init__(self, timestamp: Expr, unit: Expr, amount: Expr):
        super().__init__("timestamp_add", [timestamp, unit, amount])


class TimestampSub(Function):
    """Represents subtracting a duration from a timestamp."""

    def __init__(self, timestamp: Expr, unit: Expr, amount: Expr):
        super().__init__("timestamp_sub", [timestamp, unit, amount])


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


class ArrayConcat(Function):
    """Represents concatenating multiple arrays."""

    def __init__(self, array: Expr, rest: List[Expr]):
        super().__init__("array_concat", [array] + rest)


class ArrayElement(Function):
    """Represents accessing an element within an array"""

    def __init__(self):
        super().__init__("array_element", [])


class ArrayFilter(Function):
    """Represents filtering elements from an array based on a condition."""

    def __init__(self, array: Expr, filter: "BooleanExpr"):
        super().__init__("array_filter", [array, filter])


class ArrayLength(Function):
    """Represents getting the length of an array."""

    def __init__(self, array: Expr):
        super().__init__("array_length", [array])


class ArrayReverse(Function):
    """Represents reversing the elements of an array."""

    def __init__(self, array: Expr):
        super().__init__("array_reverse", [array])


class ArrayTransform(Function):
    """Represents applying a transformation function to each element of an array."""

    def __init__(self, array: Expr, transform: Function):
        super().__init__("array_transform", [array, transform])


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



class Max(AggregateFunction):
    """Represents the maximum aggregation function."""

    def __init__(self, value: Expr):
        super().__init__("maximum", [value])


class Min(AggregateFunction):
    """Represents the minimum aggregation function."""

    def __init__(self, value: Expr):
        super().__init__("minimum", [value])


class Sum(AggregateFunction):
    """Represents the sum aggregation function."""

    def __init__(self, value: Expr):
        super().__init__("sum", [value])


class Avg(AggregateFunction):
    """Represents the average aggregation function."""

    def __init__(self, value: Expr):
        super().__init__("avg", [value])


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
        Most BooleanExprs can be triggered infix. Eg: Field.of('age').gte(18).

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
                BooleanExpr._from_query_filter_pb(f, client)
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
            return BooleanExpr._from_query_filter_pb(f, client)
        else:
            raise TypeError(f"Unexpected filter type: {type(filter_pb)}")


class And(BooleanExpr):
    def __init__(self, *conditions: "BooleanExpr"):
        super().__init__("and", conditions, use_infix_repr=False)


class ArrayContains(BooleanExpr):
    def __init__(self, array: Expr, element: Expr):
        super().__init__(
            "array_contains", [array, element]
        )


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


class Eq(BooleanExpr):
    """Represents the equality comparison."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("eq", [left, right])


class Exists(BooleanExpr):
    """Represents checking if a field exists."""

    def __init__(self, expr: Expr):
        super().__init__("exists", [expr])


class Gt(BooleanExpr):
    """Represents the greater than comparison."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("gt", [left, right])


class Gte(BooleanExpr):
    """Represents the greater than or equal to comparison."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("gte", [left, right])


class If(BooleanExpr):
    """Represents a conditional expression (if-then-else)."""

    def __init__(self, condition: "BooleanExpr", true_expr: Expr, false_expr: Expr):
        super().__init__(
            "if", [condition, true_expr, false_expr]
        )


class In(BooleanExpr):
    """Represents checking if an expression's value is within a list of values."""

    def __init__(self, left: Expr, others: Sequence[Expr]):
        super().__init__(
            "in", [left, ListOfExprs(others)], infix_name_override="in_any"
        )


class IsNaN(BooleanExpr):
    """Represents checking if a numeric value is NaN."""

    def __init__(self, value: Expr):
        super().__init__("is_nan", [value])


class Like(BooleanExpr):
    """Represents a case-sensitive wildcard string comparison."""

    def __init__(self, expr: Expr, pattern: Expr):
        super().__init__("like", [expr, pattern])


class Lt(BooleanExpr):
    """Represents the less than comparison."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("lt", [left, right])


class Lte(BooleanExpr):
    """Represents the less than or equal to comparison."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("lte", [left, right])


class Neq(BooleanExpr):
    """Represents the inequality comparison."""

    def __init__(self, left: Expr, right: Expr):
        super().__init__("neq", [left, right])


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


class StrContains(BooleanExpr):
    """Represents checking if a string contains a specific substring."""

    def __init__(self, expr: Expr, substring: Expr):
        super().__init__("str_contains", [expr, substring])


class Xor(BooleanExpr):
    """Represents the logical XOR of multiple filter conditions."""

    def __init__(self, conditions: Sequence["BooleanExpr"]):
        super().__init__("xor", conditions, use_infix_repr=False)
