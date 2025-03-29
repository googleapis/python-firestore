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
from typing import Any, Iterable, List, Mapping, Union, Generic, TypeVar, List, Dict, Tuple, Sequence
from abc import ABC
from abc import abstractmethod
from enum import Enum
from enum import auto
import datetime
from dataclasses import dataclass
from google.cloud.firestore_v1.types.document import Value
from google.cloud.firestore_v1.types.query import StructuredQuery as Query_pb
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1._helpers import GeoPoint
from google.cloud.firestore_v1._helpers import encode_value
from google.cloud.firestore_v1._helpers import decode_value

CONSTANT_TYPE = TypeVar('CONSTANT_TYPE', str, int, float, bool, datetime.datetime, bytes, GeoPoint, Vector, list, Dict[str, Any], None)


class Ordering:
    """Represents the direction for sorting results in a pipeline."""

    class Direction(Enum):
        ASCENDING = "ascending"
        DESCENDING = "descending"

    def __init__(self, expr, order_dir: Direction | str=Direction.ASCENDING):
        """
        Initializes an Ordering instance

        Args:
            expr (Expr | str): The expression or field path string to sort by.
                If a string is provided, it's treated as a field path.
            order_dir (Direction | str): The direction to sort in.
                Defaults to ascending
        """
        self.expr = expr if isinstance(expr, Expr) else Field.of(expr)
        self.order_dir = Ordering.Direction[order_dir.upper()] if isinstance(order_dir, str) else order_dir

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
                    "direction": Value(string_value=self.order_dir.value),
                    "expression": self.expr._to_pb()
                }
            }
        )

class SampleOptions:
    """Options for the 'sample' pipeline stage."""
    class Mode(Enum):
        DOCUMENTS = "documents"
        PERCENT = "percent"

    def __init__(self, value: int | float, mode:Mode | str):
        self.value = value
        self.mode = SampleOptions.Mode[mode.upper()] if isinstance(mode, str) else mode

    def __repr__(self):
        if self.mode == SampleOptions.Mode.DOCUMENTS:
            mode_str = "doc_limit"
        else:
            mode_str = "percentage"
        return f"SampleOptions.{mode_str}({self.value})"

    @staticmethod
    def doc_limit(value:int):
        """
        Sample a set number of documents

        Args:
            value: number of documents to sample
        """
        return SampleOptions(value, mode=SampleOptions.Mode.DOCUMENTS)

    @staticmethod
    def percentage(value:float):
        """
        Sample a percentage of documents

        Args:
            value: percentage of documents to return
        """
        return SampleOptions(value, mode=SampleOptions.Mode.PERCENTAGE)

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

    def add(self, other: Expr | float) -> "Add":
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

    def subtract(self, other: Expr | float) -> "Subtract":
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

    def multiply(self, other: Expr | float) -> "Multiply":
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

    def divide(self, other: Expr | float) -> "Divide":
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

    def mod(self, other: Expr | float) -> "Mod":
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

    def logical_max(self, other: Expr | CONSTANT_TYPE) -> "LogicalMax":
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

    def logical_min(self, other: Expr | CONSTANT_TYPE) -> "LogicalMin":
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

    def in_any(self, *others: Expr | CONSTANT_TYPE) -> "In":
        """Creates an expression that checks if this expression is equal to any of the
        provided values or expressions.

        Example:
            >>> # Check if the 'category' field is either "Electronics" or value of field 'primaryType'
            >>> Field.of("category").in_any("Electronics", Field.of("primaryType"))

        Args:
            *others: The values or expressions to check against.

        Returns:
            A new `Expr` representing the 'IN' comparison.
        """
        return In(self, [self._cast_to_expr_or_convert_to_constant(o) for o in others])

    def not_in_any(self, *others: Expr | CONSTANT_TYPE) -> "Not":
        """Creates an expression that checks if this expression is not equal to any of the
        provided values or expressions.

        Example:
            >>> # Check if the 'status' field is neither "pending" nor "cancelled"
            >>> Field.of("status").not_in_any("pending", "cancelled")

        Args:
            *others: The values or expressions to check against.

        Returns:
            A new `Expr` representing the 'NOT IN' comparison.
        """
        return Not(self.in_any(*others))

    def array_concat(self, array: List[Expr | CONSTANT_TYPE]) -> "ArrayConcat":
        """Creates an expression that concatenates an array expression with another array.

        Example:
            >>> # Combine the 'tags' array with a new array and an array field
            >>> Field.of("tags").array_concat(["newTag1", "newTag2", Field.of("otherTag")])

        Args:
            array: The list of constants or expressions to concat with.

        Returns:
            A new `Expr` representing the concatenated array.
        """
        return ArrayConcat(self, [self._cast_to_expr_or_convert_to_constant(o) for o in array])

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

    def array_contains_all(self, elements: List[Expr | CONSTANT_TYPE]) -> "ArrayContainsAll":
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
        return ArrayContainsAll(self, [self._cast_to_expr_or_convert_to_constant(e) for e in elements])

    def array_contains_any(self, elements: List[Expr | CONSTANT_TYPE]) -> "ArrayContainsAny":
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
        return ArrayContainsAny(self, [self._cast_to_expr_or_convert_to_constant(e) for e in elements])

    def array_length(self) -> "ArrayLength":
        """Creates an expression that calculates the length of an array.

        Example:
            >>> # Get the number of items in the 'cart' array
            >>> Field.of("cart").array_length()

        Returns:
            A new `Expr` representing the length of the array.
        """
        return ArrayLength(self)

    def array_reverse(self) -> "ArrayReverse":
        """Creates an expression that returns the reversed content of an array.

        Example:
            >>> # Get the 'preferences' array in reversed order.
            >>> Field.of("preferences").array_reverse()

        Returns:
            A new `Expr` representing the reversed array.
        """
        return ArrayReverse(self)

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

    def sum(self) -> "Sum":
        """Creates an aggregation that calculates the sum of a numeric field across multiple stage inputs.

        Example:
            >>> # Calculate the total revenue from a set of orders
            >>> Field.of("orderAmount").sum().as_("totalRevenue")

        Returns:
            A new `Accumulator` representing the 'sum' aggregation.
        """
        return Sum(self, False)

    def avg(self) -> "Avg":
        """Creates an aggregation that calculates the average (mean) of a numeric field across multiple
        stage inputs.

        Example:
            >>> # Calculate the average age of users
            >>> Field.of("age").avg().as_("averageAge")

        Returns:
            A new `Accumulator` representing the 'avg' aggregation.
        """
        return Avg(self, False)

    def count(self) -> "Count":
        """Creates an aggregation that counts the number of stage inputs with valid evaluations of the
        expression or field.

        Example:
            >>> # Count the total number of products
            >>> Field.of("productId").count().as_("totalProducts")

        Returns:
            A new `Accumulator` representing the 'count' aggregation.
        """
        return Count(self)

    def min(self) -> "Min":
        """Creates an aggregation that finds the minimum value of a field across multiple stage inputs.

        Example:
            >>> # Find the lowest price of all products
            >>> Field.of("price").min().as_("lowestPrice")

        Returns:
            A new `Accumulator` representing the 'min' aggregation.
        """
        return Min(self, False)

    def max(self) -> "Max":
        """Creates an aggregation that finds the maximum value of a field across multiple stage inputs.

        Example:
            >>> # Find the highest score in a leaderboard
            >>> Field.of("score").max().as_("highestScore")

        Returns:
            A new `Accumulator` representing the 'max' aggregation.
        """
        return Max(self, False)

    def char_length(self) -> "CharLength":
        """Creates an expression that calculates the character length of a string.

        Example:
            >>> # Get the character length of the 'name' field
            >>> Field.of("name").char_length()

        Returns:
            A new `Expr` representing the length of the string.
        """
        return CharLength(self)

    def byte_length(self) -> "ByteLength":
        """Creates an expression that calculates the byte length of a string in its UTF-8 form.

        Example:
            >>> # Get the byte length of the 'name' field
            >>> Field.of("name").byte_length()

        Returns:
            A new `Expr` representing the byte length of the string.
        """
        return ByteLength(self)

    def like(self, pattern: Expr | str) -> "Like":
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

    def regex_contains(self, regex: Expr | str) -> "RegexContains":
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

    def regex_matches(self, regex: Expr | str) -> "RegexMatch":
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

    def str_contains(self, substring: Expr | str) -> "StrContains":
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

    def starts_with(self, prefix: Expr | str) -> "StartsWith":
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

    def ends_with(self, postfix: Expr | str) -> "EndsWith":
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

    def str_concat(self, *elements: Expr | CONSTANT_TYPE) -> "StrConcat":
        """Creates an expression that concatenates string expressions, fields or constants together.

        Example:
            >>> # Combine the 'firstName', " ", and 'lastName' fields into a single string
            >>> Field.of("firstName").str_concat(" ", Field.of("lastName"))

        Args:
            *elements: The expressions or constants (typically strings) to concatenate.

        Returns:
            A new `Expr` representing the concatenated string.
        """
        return StrConcat(*[self._cast_to_expr_or_convert_to_constant(el) for el in elements])

    def to_lower(self) -> "ToLower":
        """Creates an expression that converts a string to lowercase.

        Example:
            >>> # Convert the 'name' field to lowercase
            >>> Field.of("name").to_lower()

        Returns:
            A new `Expr` representing the lowercase string.
        """
        return ToLower(self)

    def to_upper(self) -> "ToUpper":
        """Creates an expression that converts a string to uppercase.

        Example:
            >>> # Convert the 'title' field to uppercase
            >>> Field.of("title").to_upper()

        Returns:
            A new `Expr` representing the uppercase string.
        """
        return ToUpper(self)

    def trim(self) -> "Trim":
        """Creates an expression that removes leading and trailing whitespace from a string.

        Example:
            >>> # Trim whitespace from the 'userInput' field
            >>> Field.of("userInput").trim()

        Returns:
            A new `Expr` representing the trimmed string.
        """
        return Trim(self)

    def reverse(self) -> "Reverse":
        """Creates an expression that reverses a string.

        Example:
            >>> # Reverse the 'userInput' field
            >>> Field.of("userInput").reverse()

        Returns:
            A new `Expr` representing the reversed string.
        """
        return Reverse(self)

    def replace_first(self, find: Expr | str, replace: Expr | str) -> "ReplaceFirst":
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
        return ReplaceFirst(self, self._cast_to_expr_or_convert_to_constant(find), self._cast_to_expr_or_convert_to_constant(replace))

    def replace_all(self, find: Expr | str, replace: Expr | str) -> "ReplaceAll":
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
        return ReplaceAll(self, self._cast_to_expr_or_convert_to_constant(find), self._cast_to_expr_or_convert_to_constant(replace))

    def map_get(self, key: str) -> "MapGet":
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
        return MapGet(self, key)

    def cosine_distance(self, other: Expr | list[float] | Vector) -> "CosineDistance":
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

    def euclidean_distance(self, other: Expr | list[float] | Vector) -> "EuclideanDistance":
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

    def dot_product(self, other: Expr | list[float] | Vector) -> "DotProduct":
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

    def vector_length(self) -> "VectorLength":
        """Creates an expression that calculates the length (dimension) of a Firestore Vector.

        Example:
            >>> # Get the vector length (dimension) of the field 'embedding'.
            >>> Field.of("embedding").vector_length()

        Returns:
            A new `Expr` representing the length of the vector.
        """
        return VectorLength(self)

    def timestamp_to_unix_micros(self) -> "TimestampToUnixMicros":
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

    def unix_micros_to_timestamp(self) -> "UnixMicrosToTimestamp":
        """Creates an expression that converts a number of microseconds since the epoch (1970-01-01
        00:00:00 UTC) to a timestamp.

        Example:
            >>> # Convert the 'microseconds' field to a timestamp.
            >>> Field.of("microseconds").unix_micros_to_timestamp()

        Returns:
            A new `Expr` representing the timestamp.
        """
        return UnixMicrosToTimestamp(self)

    def timestamp_to_unix_millis(self) -> "TimestampToUnixMillis":
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

    def unix_millis_to_timestamp(self) -> "UnixMillisToTimestamp":
        """Creates an expression that converts a number of milliseconds since the epoch (1970-01-01
        00:00:00 UTC) to a timestamp.

        Example:
            >>> # Convert the 'milliseconds' field to a timestamp.
            >>> Field.of("milliseconds").unix_millis_to_timestamp()

        Returns:
            A new `Expr` representing the timestamp.
        """
        return UnixMillisToTimestamp(self)

    def timestamp_to_unix_seconds(self) -> "TimestampToUnixSeconds":
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

    def unix_seconds_to_timestamp(self) -> "UnixSecondsToTimestamp":
        """Creates an expression that converts a number of seconds since the epoch (1970-01-01 00:00:00
        UTC) to a timestamp.

        Example:
            >>> # Convert the 'seconds' field to a timestamp.
            >>> Field.of("seconds").unix_seconds_to_timestamp()

        Returns:
            A new `Expr` representing the timestamp.
        """
        return UnixSecondsToTimestamp(self)

    def timestamp_add(self, unit: Expr | str, amount: Expr | float) -> "TimestampAdd":
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
        return TimestampAdd(self, self._cast_to_expr_or_convert_to_constant(unit), self._cast_to_expr_or_convert_to_constant(amount))

    def timestamp_sub(self, unit: Expr | str, amount: Expr | float) -> "TimestampSub":
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
        return TimestampSub(self, self._cast_to_expr_or_convert_to_constant(unit), self._cast_to_expr_or_convert_to_constant(amount))

    def ascending(self) -> Ordering:
        """Creates an `Ordering` that sorts documents in ascending order based on this expression.

        Example:
            >>> # Sort documents by the 'name' field in ascending order
            >>> firestore.pipeline().collection("users").sort(Field.of("name").ascending())

        Returns:
            A new `Ordering` for ascending sorting.
        """
        return Ordering(self, Ordering.Direction.ASCENDING)

    def descending(self) -> Ordering:
        """Creates an `Ordering` that sorts documents in descending order based on this expression.

        Example:
            >>> # Sort documents by the 'createdAt' field in descending order
            >>> firestore.pipeline().collection("users").sort(Field.of("createdAt").descending())

        Returns:
            A new `Ordering` for descending sorting.
        """
        return Ordering(self, Ordering.Direction.DESCENDING)

    def as_(self, alias: str) -> "ExprWithAlias":
        """Assigns an alias to this expression.

        Aliases are useful for renaming fields in the output of a stage or for giving meaningful
        names to calculated values.

        Example:
            >>> # Calculate the total price and assign it the alias "totalPrice" and add it to the output.
            >>> firestore.pipeline().collection("items").add_fields(
            ...     Field.of("price").multiply(Field.of("quantity")).as_("totalPrice")
            ... )

        Args:
            alias: The alias to assign to this expression.

        Returns:
            A new `Selectable` (typically an `ExprWithAlias`) that wraps this
            expression and associates it with the provided alias.
        """
        return ExprWithAlias(self, alias)

class Constant(Expr, Generic[CONSTANT_TYPE]):
    """Represents a constant literal value in an expression."""
    def __init__(self, value: CONSTANT_TYPE):
        self.value: CONSTANT_TYPE = value

    @staticmethod
    def of(value:CONSTANT_TYPE) -> Constant[CONSTANT_TYPE]:
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

    def _to_pb(self):
        return Value(array_value={"values": [e._to_pb() for e in self.exprs]})


class Function(Expr):
    """A base class for expressions that represent function calls."""

    def __init__(self, name: str, params: Sequence[Expr]):
        self.name = name
        self.params = list(params)

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join([repr(p) for p in self.params])})"

    def _to_pb(self):
        return Value(
            function_value={
                "name": self.name, "args": [p._to_pb() for p in self.params]
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
    def __init__(self, map_: Expr, key: str):
        super().__init__("map_get", [map_, Constant(key)])


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
    def __init__(self, array: Expr, filter: "FilterCondition"):
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


class Accumulator(Function):
    """A base class for aggregation functions that operate across multiple inputs."""


class Max(Accumulator):
    """Represents the maximum aggregation function."""
    def __init__(self, value: Expr, distinct: bool=False):
        super().__init__("maximum", [value])


class Min(Accumulator):
    """Represents the minimum aggregation function."""
    def __init__(self, value: Expr, distinct: bool=False):
        super().__init__("minimum", [value])


class Sum(Accumulator):
    """Represents the sum aggregation function."""
    def __init__(self, value: Expr, distinct: bool=False):
        super().__init__("sum", [value])


class Avg(Accumulator):
    """Represents the average aggregation function."""
    def __init__(self, value: Expr, distinct: bool=False):
        super().__init__("avg", [value])


class Count(Accumulator):
    """Represents the count aggregation function."""
    def __init__(self, value: Expr | None = None):
        super().__init__("count", [value] if value else [])


class CountIf(Function):
    """Represents counting inputs where a condition is true (likely used internally or planned)."""
    def __init__(self, value: Expr, distinct: bool=False):
        super().__init__("countif", [value] if value else [])


class Selectable(Expr):
    """Base class for expressions that can be selected or aliased in projection stages."""

    @abstractmethod
    def _to_map(self):
        raise NotImplementedError


T = TypeVar('T', bound=Expr)
class ExprWithAlias(Selectable, Generic[T]):
    """Wraps an expression with an alias."""
    def __init__(self, expr: T, alias: str):
        self.expr = expr
        self.alias = alias

    def _to_map(self):
        return self.alias, self.expr._to_pb()

    def __repr__(self):
        return f"{self.expr}.as_('{self.alias}')"

    def _to_pb(self):
        return Value(
            map_value={"fields": {self.alias: self.expr._to_pb()}}
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

    @staticmethod
    def _from_query_filter_pb(filter_pb, client):
        if isinstance(filter_pb, Query_pb.CompositeFilter):
            sub_filters = [FilterCondition._from_query_filter_pb(f, client) for f in filter_pb.filters]
            if filter_pb.op == Query_pb.CompositeFilter.Operator.OR:
                return Or(*sub_filters)
            elif filter_pb.op == Query_pb.CompositeFilter.Operator.AND:
                return And(*sub_filters)
            else:
                raise TypeError(f"Unexpected CompositeFilter operator type: {filter_pb.op}")
        elif isinstance(filter_pb, Query_pb.UnaryFilter):
            field = Field.of(filter_pb.field)
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
            field = Field.of(filter_pb.field)
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
            f = filter_pb.composite_filter or filter_pb.field_filter or filter_pb.unary_filter
            return FilterCondition._from_query_filter_pb(f, client)
        else:
            raise TypeError(f"Unexpected filter type: {type(filter_pb)}")


class And(FilterCondition):
    def __init__(self, *conditions: "FilterCondition"):
        super().__init__("and", conditions)


class ArrayContains(FilterCondition):
    def __init__(self, array: Expr, element: Expr):
        super().__init__(
            "array_contains", [array, element if element else Constant(None)]
        )


class ArrayContainsAll(FilterCondition):
    """Represents checking if an array contains all specified elements."""
    def __init__(self, array: Expr, elements: List[Expr]):
        super().__init__("array_contains_all", [array, ListOfExprs(elements)])


class ArrayContainsAny(FilterCondition):
    """Represents checking if an array contains any of the specified elements."""
    def __init__(self, array: Expr, elements: List[Expr]):
        super().__init__("array_contains_any", [array, ListOfExprs(elements)])


class EndsWith(FilterCondition):
    """Represents checking if a string ends with a specific postfix."""
    def __init__(self, expr: Expr, postfix: Expr):
        super().__init__("ends_with", [expr, postfix])


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


class If(FilterCondition):
    """Represents a conditional expression (if-then-else)."""
    def __init__(self, condition: "FilterCondition", true_expr: Expr, false_expr: Expr):
        super().__init__(
            "if", [condition, true_expr, false_expr if false_expr else Constant(None)]
        )


class In(FilterCondition):
    """Represents checking if an expression's value is within a list of values."""
    def __init__(self, left: Expr, others: List[Expr]):
        super().__init__("in", [left, ListOfExprs(others)])


class IsNaN(FilterCondition):
    """Represents checking if a numeric value is NaN."""
    def __init__(self, value: Expr):
        super().__init__("is_nan", [value])


class Like(FilterCondition):
    """Represents a case-sensitive wildcard string comparison."""
    def __init__(self, expr: Expr, pattern: Expr):
        super().__init__("like", [expr, pattern])


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
        super().__init__("not", [condition])


class Or(FilterCondition):
    """Represents the logical OR of multiple filter conditions."""
    def __init__(self, *conditions: "FilterCondition"):
        super().__init__("or", conditions)


class RegexContains(FilterCondition):
    """Represents checking if a string contains a substring matching a regex."""
    def __init__(self, expr: Expr, regex: Expr):
        super().__init__("regex_contains", [expr, regex])


class RegexMatch(FilterCondition):
    """Represents checking if a string fully matches a regex."""
    def __init__(self, expr: Expr, regex: Expr):
        super().__init__("regex_match", [expr, regex])


class StartsWith(FilterCondition):
    """Represents checking if a string starts with a specific prefix."""
    def __init__(self, expr: Expr, prefix: Expr):
        super().__init__("starts_with", [expr, prefix])


class StrContains(FilterCondition):
    """Represents checking if a string contains a specific substring."""
    def __init__(self, expr: Expr, substring: Expr):
        super().__init__("str_contains", [expr, substring])


class Xor(FilterCondition):
    """Represents the logical XOR of multiple filter conditions."""
    def __init__(self, conditions: List["FilterCondition"]):
        super().__init__("xor", conditions)
