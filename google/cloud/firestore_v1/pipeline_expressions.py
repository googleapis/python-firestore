
class Expr:
    """
    Represents an expression that can be evaluated to a value within the execution of a pipeline
    """

class Constant(Expr):

class ListOfExprs(Expr):

class Function(Expr):
    """
    A type of Expression that takes in inputs and gives outputs
    """

class Divide(Function):

class DotProduct(Function):

class EuclideanDistance(Function):


class LogicalMax(Function):

class LogicalMin(Function):

class MapGet(Function):

class Mod(Function):

class Multiply(Function):

class Parent(Function):

class ReplaceAll(Function):

class ReplaceFirst(Function):

class Reverse(Function):

class StrConcat(Function):

class Subtract(Function):

class TimestampAdd(Function):

class TimestampSub(Function):

class TimestampToUnixMicros(Function):

class TimestampToUnixMillis(Function):

class TimestampToUnixSeconds(Function):

class ToLower(Function):

class ToUpper(Function):

class Trim(Function):

class UnixMicrosToTimestamp(Function):

class UnixMillisToTimestamp(Function):

class UnixSecondsToTimestamp(Function):

class VectorLength(Function):

class Add(Function):

class ArrayConcat(Function):

class ArrayElement(Function):

class ArrayFilter(Function):

class ArrayLength(Function):

class ArrayReverse(Function):

class ArrayTransform(Function):

class ByteLength(Function):

class CharLength(Function):

class CollectionId(Function):

class CosineDistance(Function):


class Accumulator(Function):
    """
    A type of expression that takes in many, and results in one value
    """


class Max(Accumulator):

class Min(Accumulator):

class Sum(Accumulator):





class Avg(Function, Accumulator):

class Count(Function, Accumulator):
class CountIf(Function, Accumulator):

class Selectable:
  """
  Points at something in the database?
  """

class AccumulatorTarget(Selectable):

class ExprWithAlies(Expr, Selectable):

class Field(Expr, Selectable):


class FilterCondition(Function):
  """
  filters the given data in some way
  """

class And(FilterCondition):

class ArrayContains(FilterCondition)

class ArrayContainsAll(FilterCondition)

class ArrayContainsAny(FilterCondition)

class EndsWith(FilterCondition)

class Eq(FilterCondition)

class Exists(FilterCondition)

class Gt(FilterCondition)

class Gte(FilterCondition)

class If(FilterCondition)

class In(FilterCondition)

class IsNan(FilterCondition)

class Like(FilterCondition)


class Lt(FilterCondition)

class Lte(FilterCondition)

class Neq(FilterCondition)

class Not(FilterCondition)

class Or(FilterCondition)

class RegexContains(FilterCondition)

class RegexMatch(FilterCondition)

class StartsWith(FilterCondition)

class StrContains(FilterCondition):

class Xor(FilterCondition):
