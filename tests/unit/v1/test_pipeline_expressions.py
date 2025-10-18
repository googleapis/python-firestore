# Copyright 2025 Google LLC All rights reserved.
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

import pytest
import mock
import datetime

from google.cloud.firestore_v1 import _helpers
from google.cloud.firestore_v1.types import document as document_pb
from google.cloud.firestore_v1.types import query as query_pb
from google.cloud.firestore_v1.types.document import Value
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1._helpers import GeoPoint
from google.cloud.firestore_v1.pipeline_expressions import BooleanExpr, ListOfExprs
import google.cloud.firestore_v1.pipeline_expressions as expr


@pytest.fixture
def mock_client():
    client = mock.Mock(spec=["_database_string", "collection"])
    client._database_string = "projects/p/databases/d"
    return client


class TestOrdering:
    @pytest.mark.parametrize(
        "direction_arg,expected_direction",
        [
            ("ASCENDING", expr.Ordering.Direction.ASCENDING),
            ("DESCENDING", expr.Ordering.Direction.DESCENDING),
            ("ascending", expr.Ordering.Direction.ASCENDING),
            ("descending", expr.Ordering.Direction.DESCENDING),
            (expr.Ordering.Direction.ASCENDING, expr.Ordering.Direction.ASCENDING),
            (expr.Ordering.Direction.DESCENDING, expr.Ordering.Direction.DESCENDING),
        ],
    )
    def test_ctor(self, direction_arg, expected_direction):
        instance = expr.Ordering("field1", direction_arg)
        assert isinstance(instance.expr, expr.Field)
        assert instance.expr.path == "field1"
        assert instance.order_dir == expected_direction

    def test_repr(self):
        field_expr = expr.Field.of("field1")
        instance = expr.Ordering(field_expr, "ASCENDING")
        repr_str = repr(instance)
        assert repr_str == "Field.of('field1').ascending()"

        instance = expr.Ordering(field_expr, "DESCENDING")
        repr_str = repr(instance)
        assert repr_str == "Field.of('field1').descending()"

    def test_to_pb(self):
        field_expr = expr.Field.of("field1")
        instance = expr.Ordering(field_expr, "ASCENDING")
        result = instance._to_pb()
        assert result.map_value.fields["expression"].field_reference_value == "field1"
        assert result.map_value.fields["direction"].string_value == "ascending"

        instance = expr.Ordering(field_expr, "DESCENDING")
        result = instance._to_pb()
        assert result.map_value.fields["expression"].field_reference_value == "field1"
        assert result.map_value.fields["direction"].string_value == "descending"


class TestExpr:
    def test_ctor(self):
        """
        Base class should be abstract
        """
        with pytest.raises(TypeError):
            expr.Expr()

    @pytest.mark.parametrize(
        "method,args,result_cls",
        [
            ("add", (2,), expr.Add),
            ("subtract", (2,), expr.Subtract),
            ("multiply", (2,), expr.Multiply),
            ("divide", (2,), expr.Divide),
            ("mod", (2,), expr.Mod),
            ("abs", (), expr.Abs),
            ("ceil", (), expr.Ceil),
            ("exp", (), expr.Exp),
            ("floor", (), expr.Floor),
            ("ln", (), expr.Ln),
            ("log", (10,), expr.Log),
            ("pow", (2,), expr.Pow),
            ("round", (), expr.Round),
            ("sqrt", (), expr.Sqrt),
            ("logical_maximum", (2,), expr.LogicalMaximum),
            ("logical_minimum", (2,), expr.LogicalMinimum),
            ("equal", (2,), expr.Equal),
            ("not_equal", (2,), expr.NotEqual),
            ("less_than", (2,), expr.LessThan),
            ("less_than_or_equal", (2,), expr.LessThanOrEqual),
            ("greater_than", (2,), expr.GreaterThan),
            ("greater_than_or_equal", (2,), expr.GreaterThanOrEqual),
            ("equal_any", ([None],), expr.EqualAny),
            ("not_equal_any", ([None],), expr.NotEqualAny),
            ("array_get", (1,), expr.ArrayGet),
            ("array_concat", ([None],), expr.ArrayConcat),
            ("array_contains", (None,), expr.ArrayContains),
            ("array_contains_all", ([None],), expr.ArrayContainsAll),
            ("array_contains_any", ([None],), expr.ArrayContainsAny),
            ("array_length", (), expr.ArrayLength),
            ("array_reverse", (), expr.ArrayReverse),
            ("is_nan", (), expr.IsNaN),
            ("exists", (), expr.Exists),
            ("sum", (), expr.Sum),
            ("average", (), expr.Average),
            ("count", (), expr.Count),
            ("minimum", (), expr.Minimum),
            ("maximum", (), expr.Maximum),
            ("char_length", (), expr.CharLength),
            ("byte_length", (), expr.ByteLength),
            ("like", ("pattern",), expr.Like),
            ("regex_contains", ("regex",), expr.RegexContains),
            ("regex_matches", ("regex",), expr.RegexMatch),
            ("string_contains", ("substring",), expr.StringContains),
            ("starts_with", ("prefix",), expr.StartsWith),
            ("ends_with", ("postfix",), expr.EndsWith),
            ("string_concat", ("elem1", expr.Constant("elem2")), expr.StringConcat),
            ("to_lower", (), expr.ToLower),
            ("to_upper", (), expr.ToUpper),
            ("trim", (), expr.Trim),
            ("reverse", (), expr.Reverse),
            ("map_get", ("key",), expr.MapGet),
            ("cosine_distance", [1], expr.CosineDistance),
            ("euclidean_distance", [1], expr.EuclideanDistance),
            ("dot_product", [1], expr.DotProduct),
            ("vector_length", (), expr.VectorLength),
            ("timestamp_to_unix_micros", (), expr.TimestampToUnixMicros),
            ("unix_micros_to_timestamp", (), expr.UnixMicrosToTimestamp),
            ("timestamp_to_unix_millis", (), expr.TimestampToUnixMillis),
            ("unix_millis_to_timestamp", (), expr.UnixMillisToTimestamp),
            ("timestamp_to_unix_seconds", (), expr.TimestampToUnixSeconds),
            ("unix_seconds_to_timestamp", (), expr.UnixSecondsToTimestamp),
            ("timestamp_add", ("day", 1), expr.TimestampAdd),
            ("timestamp_subtract", ("hour", 2.5), expr.TimestampSubtract),
            ("ascending", (), expr.Ordering),
            ("descending", (), expr.Ordering),
            ("as_", ("alias",), expr.AliasedExpr),
        ],
    )
    @pytest.mark.parametrize(
        "base_instance",
        [
            expr.Constant(1),
            expr.Function.add("1", 1),
            expr.Field.of("test"),
            expr.Constant(1).as_("one"),
        ],
    )
    def test_infix_call(self, method, args, result_cls, base_instance):
        """
        many BooleanExpr expressions support infix execution, and are exposed as methods on Expr. Test calling them
        """
        method_ptr = getattr(base_instance, method)

        result = method_ptr(*args)
        assert isinstance(result, result_cls)
        if isinstance(result, (expr.Ordering, expr.AliasedExpr)):
            assert result.expr == base_instance
        else:
            assert result.params[0] == base_instance


class TestConstant:
    @pytest.mark.parametrize(
        "input_val, to_pb_val",
        [
            ("test", Value(string_value="test")),
            ("", Value(string_value="")),
            (10, Value(integer_value=10)),
            (0, Value(integer_value=0)),
            (10.0, Value(double_value=10)),
            (0.0, Value(double_value=0)),
            (True, Value(boolean_value=True)),
            (b"test", Value(bytes_value=b"test")),
            (None, Value(null_value=0)),
            (
                datetime.datetime(2025, 5, 12),
                Value(timestamp_value={"seconds": 1747008000}),
            ),
            (GeoPoint(1, 2), Value(geo_point_value={"latitude": 1, "longitude": 2})),
            (
                [0.0, 1.0, 2.0],
                Value(
                    array_value={"values": [Value(double_value=i) for i in range(3)]}
                ),
            ),
            ({"a": "b"}, Value(map_value={"fields": {"a": Value(string_value="b")}})),
            (
                Vector([1.0, 2.0]),
                Value(
                    map_value={
                        "fields": {
                            "__type__": Value(string_value="__vector__"),
                            "value": Value(
                                array_value={
                                    "values": [Value(double_value=v) for v in [1, 2]],
                                }
                            ),
                        }
                    }
                ),
            ),
        ],
    )
    def test_to_pb(self, input_val, to_pb_val):
        instance = expr.Constant.of(input_val)
        assert instance._to_pb() == to_pb_val

    @pytest.mark.parametrize(
        "input_val,expected",
        [
            ("test", "Constant.of('test')"),
            ("", "Constant.of('')"),
            (10, "Constant.of(10)"),
            (0, "Constant.of(0)"),
            (10.0, "Constant.of(10.0)"),
            (0.0, "Constant.of(0.0)"),
            (True, "Constant.of(True)"),
            (b"test", "Constant.of(b'test')"),
            (None, "Constant.of(None)"),
            (
                datetime.datetime(2025, 5, 12),
                "Constant.of(datetime.datetime(2025, 5, 12, 0, 0))",
            ),
            (GeoPoint(1, 2), "Constant.of(GeoPoint(latitude=1, longitude=2))"),
            ([1, 2, 3], "Constant.of([1, 2, 3])"),
            ({"a": "b"}, "Constant.of({'a': 'b'})"),
            (Vector([1.0, 2.0]), "Constant.of(Vector<1.0, 2.0>)"),
        ],
    )
    def test_repr(self, input_val, expected):
        instance = expr.Constant.of(input_val)
        repr_string = repr(instance)
        assert repr_string == expected

    @pytest.mark.parametrize(
        "first,second,expected",
        [
            (expr.Constant.of(1), expr.Constant.of(2), False),
            (expr.Constant.of(1), expr.Constant.of(1), True),
            (expr.Constant.of(1), 1, True),
            (expr.Constant.of(1), 2, False),
            (expr.Constant.of("1"), 1, False),
            (expr.Constant.of("1"), "1", True),
            (expr.Constant.of(None), expr.Constant.of(0), False),
            (expr.Constant.of(None), expr.Constant.of(None), True),
            (expr.Constant.of([1, 2, 3]), expr.Constant.of([1, 2, 3]), True),
            (expr.Constant.of([1, 2, 3]), expr.Constant.of([1, 2]), False),
            (expr.Constant.of([1, 2, 3]), [1, 2, 3], True),
            (expr.Constant.of([1, 2, 3]), object(), False),
        ],
    )
    def test_equality(self, first, second, expected):
        assert (first == second) is expected


class TestListOfExprs:
    def test_to_pb(self):
        instance = expr.ListOfExprs([expr.Constant(1), expr.Constant(2)])
        result = instance._to_pb()
        assert len(result.array_value.values) == 2
        assert result.array_value.values[0].integer_value == 1
        assert result.array_value.values[1].integer_value == 2

    def test_empty_to_pb(self):
        instance = expr.ListOfExprs([])
        result = instance._to_pb()
        assert len(result.array_value.values) == 0

    def test_repr(self):
        instance = expr.ListOfExprs([expr.Constant(1), expr.Constant(2)])
        repr_string = repr(instance)
        assert repr_string == "ListOfExprs([Constant.of(1), Constant.of(2)])"
        empty_instance = expr.ListOfExprs([])
        empty_repr_string = repr(empty_instance)
        assert empty_repr_string == "ListOfExprs([])"

    @pytest.mark.parametrize(
        "first,second,expected",
        [
            (expr.ListOfExprs([]), expr.ListOfExprs([]), True),
            (expr.ListOfExprs([]), expr.ListOfExprs([expr.Constant(1)]), False),
            (expr.ListOfExprs([expr.Constant(1)]), expr.ListOfExprs([]), False),
            (
                expr.ListOfExprs([expr.Constant(1)]),
                expr.ListOfExprs([expr.Constant(1)]),
                True,
            ),
            (
                expr.ListOfExprs([expr.Constant(1)]),
                expr.ListOfExprs([expr.Constant(2)]),
                False,
            ),
            (
                expr.ListOfExprs([expr.Constant(1), expr.Constant(2)]),
                expr.ListOfExprs([expr.Constant(1), expr.Constant(2)]),
                True,
            ),
            (expr.ListOfExprs([expr.Constant(1)]), [expr.Constant(1)], False),
            (expr.ListOfExprs([expr.Constant(1)]), [1], False),
            (expr.ListOfExprs([expr.Constant(1)]), object(), False),
        ],
    )
    def test_equality(self, first, second, expected):
        assert (first == second) is expected


class TestSelectable:
    """
    contains tests for each Expr class that derives from Selectable
    """

    def test_ctor(self):
        """
        Base class should be abstract
        """
        with pytest.raises(TypeError):
            expr.Selectable()

    def test_value_from_selectables(self):
        selectable_list = [
            expr.Field.of("field1"),
            expr.Field.of("field2").as_("alias2"),
        ]
        result = expr.Selectable._value_from_selectables(*selectable_list)
        assert len(result.map_value.fields) == 2
        assert result.map_value.fields["field1"].field_reference_value == "field1"
        assert result.map_value.fields["alias2"].field_reference_value == "field2"

    @pytest.mark.parametrize(
        "first,second,expected",
        [
            (expr.Field.of("field1"), expr.Field.of("field1"), True),
            (expr.Field.of("field1"), expr.Field.of("field2"), False),
            (expr.Field.of(None), object(), False),
            (expr.Field.of("f").as_("a"), expr.Field.of("f").as_("a"), True),
            (expr.Field.of("one").as_("a"), expr.Field.of("two").as_("a"), False),
            (expr.Field.of("f").as_("one"), expr.Field.of("f").as_("two"), False),
            (expr.Field.of("field"), expr.Field.of("field").as_("alias"), False),
            (expr.Field.of("field").as_("alias"), expr.Field.of("field"), False),
        ],
    )
    def test_equality(self, first, second, expected):
        assert (first == second) is expected

    class TestField:
        def test_repr(self):
            instance = expr.Field.of("field1")
            repr_string = repr(instance)
            assert repr_string == "Field.of('field1')"

        def test_of(self):
            instance = expr.Field.of("field1")
            assert instance.path == "field1"

        def test_to_pb(self):
            instance = expr.Field.of("field1")
            result = instance._to_pb()
            assert result.field_reference_value == "field1"

        def test_to_map(self):
            instance = expr.Field.of("field1")
            result = instance._to_map()
            assert result[0] == "field1"
            assert result[1] == Value(field_reference_value="field1")

    class TestAliasedExpr:
        def test_repr(self):
            instance = expr.Field.of("field1").as_("alias1")
            assert repr(instance) == "Field.of('field1').as_('alias1')"

        def test_ctor(self):
            arg = expr.Field.of("field1")
            alias = "alias1"
            instance = expr.AliasedExpr(arg, alias)
            assert instance.expr == arg
            assert instance.alias == alias

        def test_to_pb(self):
            arg = expr.Field.of("field1")
            alias = "alias1"
            instance = expr.AliasedExpr(arg, alias)
            result = instance._to_pb()
            assert result.map_value.fields.get("alias1") == arg._to_pb()

        def test_to_map(self):
            instance = expr.Field.of("field1").as_("alias1")
            result = instance._to_map()
            assert result[0] == "alias1"
            assert result[1] == Value(field_reference_value="field1")

    class TestAliasedAggregate:

        def test_repr(self):
            instance = expr.Field.of("field1").maximum().as_("alias1")
            assert repr(instance) == "Maximum(Field.of('field1')).as_('alias1')"

        def test_ctor(self):
            arg = expr.Field.of("field1").minimum()
            alias = "alias1"
            instance = expr.AliasedAggregate(arg, alias)
            assert instance.expr == arg
            assert instance.alias == alias

        def test_to_pb(self):
            arg = expr.Field.of("field1").average()
            alias = "alias1"
            instance = expr.AliasedAggregate(arg, alias)
            result = instance._to_pb()
            assert result.map_value.fields.get("alias1") == arg._to_pb()

        def test_to_map(self):
            arg = expr.Field.of("field1").count()
            alias = "alias1"
            instance = expr.AliasedAggregate(arg, alias)
            result = instance._to_map()
            assert result[0] == "alias1"
            assert result[1] == arg._to_pb()


class TestBooleanExpr:
    def test__from_query_filter_pb_composite_filter_or(self, mock_client):
        """
        test composite OR filters

        should create an or statement, made up of ands checking of existance of relevant fields
        """
        filter1_pb = query_pb.StructuredQuery.FieldFilter(
            field=query_pb.StructuredQuery.FieldReference(field_path="field1"),
            op=query_pb.StructuredQuery.FieldFilter.Operator.EQUAL,
            value=_helpers.encode_value("val1"),
        )
        filter2_pb = query_pb.StructuredQuery.UnaryFilter(
            field=query_pb.StructuredQuery.FieldReference(field_path="field2"),
            op=query_pb.StructuredQuery.UnaryFilter.Operator.IS_NULL,
        )

        composite_pb = query_pb.StructuredQuery.CompositeFilter(
            op=query_pb.StructuredQuery.CompositeFilter.Operator.OR,
            filters=[
                query_pb.StructuredQuery.Filter(field_filter=filter1_pb),
                query_pb.StructuredQuery.Filter(unary_filter=filter2_pb),
            ],
        )
        wrapped_filter_pb = query_pb.StructuredQuery.Filter(
            composite_filter=composite_pb
        )

        result = BooleanExpr._from_query_filter_pb(wrapped_filter_pb, mock_client)

        # should include existance checks
        expected_cond1 = expr.And(
            expr.Exists(expr.Field.of("field1")),
            expr.Equal(expr.Field.of("field1"), expr.Constant("val1")),
        )
        expected_cond2 = expr.And(
            expr.Exists(expr.Field.of("field2")),
            expr.Equal(expr.Field.of("field2"), expr.Constant(None)),
        )
        expected = expr.Or(expected_cond1, expected_cond2)

        assert repr(result) == repr(expected)

    def test__from_query_filter_pb_composite_filter_and(self, mock_client):
        """
        test composite AND filters

        should create an and statement, made up of ands checking of existance of relevant fields
        """
        filter1_pb = query_pb.StructuredQuery.FieldFilter(
            field=query_pb.StructuredQuery.FieldReference(field_path="field1"),
            op=query_pb.StructuredQuery.FieldFilter.Operator.GREATER_THAN,
            value=_helpers.encode_value(100),
        )
        filter2_pb = query_pb.StructuredQuery.FieldFilter(
            field=query_pb.StructuredQuery.FieldReference(field_path="field2"),
            op=query_pb.StructuredQuery.FieldFilter.Operator.LESS_THAN,
            value=_helpers.encode_value(200),
        )

        composite_pb = query_pb.StructuredQuery.CompositeFilter(
            op=query_pb.StructuredQuery.CompositeFilter.Operator.AND,
            filters=[
                query_pb.StructuredQuery.Filter(field_filter=filter1_pb),
                query_pb.StructuredQuery.Filter(field_filter=filter2_pb),
            ],
        )
        wrapped_filter_pb = query_pb.StructuredQuery.Filter(
            composite_filter=composite_pb
        )

        result = BooleanExpr._from_query_filter_pb(wrapped_filter_pb, mock_client)

        # should include existance checks
        expected_cond1 = expr.And(
            expr.Exists(expr.Field.of("field1")),
            expr.GreaterThan(expr.Field.of("field1"), expr.Constant(100)),
        )
        expected_cond2 = expr.And(
            expr.Exists(expr.Field.of("field2")),
            expr.LessThan(expr.Field.of("field2"), expr.Constant(200)),
        )
        expected = expr.And(expected_cond1, expected_cond2)
        assert repr(result) == repr(expected)

    def test__from_query_filter_pb_composite_filter_nested(self, mock_client):
        """
        test composite filter with complex nested checks
        """
        # OR (field1 == "val1", AND(field2 > 10, field3 IS NOT NULL))
        filter1_pb = query_pb.StructuredQuery.FieldFilter(
            field=query_pb.StructuredQuery.FieldReference(field_path="field1"),
            op=query_pb.StructuredQuery.FieldFilter.Operator.EQUAL,
            value=_helpers.encode_value("val1"),
        )
        filter2_pb = query_pb.StructuredQuery.FieldFilter(
            field=query_pb.StructuredQuery.FieldReference(field_path="field2"),
            op=query_pb.StructuredQuery.FieldFilter.Operator.GREATER_THAN,
            value=_helpers.encode_value(10),
        )
        filter3_pb = query_pb.StructuredQuery.UnaryFilter(
            field=query_pb.StructuredQuery.FieldReference(field_path="field3"),
            op=query_pb.StructuredQuery.UnaryFilter.Operator.IS_NOT_NULL,
        )
        inner_and_pb = query_pb.StructuredQuery.CompositeFilter(
            op=query_pb.StructuredQuery.CompositeFilter.Operator.AND,
            filters=[
                query_pb.StructuredQuery.Filter(field_filter=filter2_pb),
                query_pb.StructuredQuery.Filter(unary_filter=filter3_pb),
            ],
        )
        outer_or_pb = query_pb.StructuredQuery.CompositeFilter(
            op=query_pb.StructuredQuery.CompositeFilter.Operator.OR,
            filters=[
                query_pb.StructuredQuery.Filter(field_filter=filter1_pb),
                query_pb.StructuredQuery.Filter(composite_filter=inner_and_pb),
            ],
        )
        wrapped_filter_pb = query_pb.StructuredQuery.Filter(
            composite_filter=outer_or_pb
        )

        result = BooleanExpr._from_query_filter_pb(wrapped_filter_pb, mock_client)

        expected_cond1 = expr.And(
            expr.Exists(expr.Field.of("field1")),
            expr.Equal(expr.Field.of("field1"), expr.Constant("val1")),
        )
        expected_cond2 = expr.And(
            expr.Exists(expr.Field.of("field2")),
            expr.GreaterThan(expr.Field.of("field2"), expr.Constant(10)),
        )
        expected_cond3 = expr.And(
            expr.Exists(expr.Field.of("field3")),
            expr.Not(expr.Equal(expr.Field.of("field3"), expr.Constant(None))),
        )
        expected_inner_and = expr.And(expected_cond2, expected_cond3)
        expected_outer_or = expr.Or(expected_cond1, expected_inner_and)

        assert repr(result) == repr(expected_outer_or)

    def test__from_query_filter_pb_composite_filter_unknown_op(self, mock_client):
        """
        check composite filter with unsupported operator type
        """
        filter1_pb = query_pb.StructuredQuery.FieldFilter(
            field=query_pb.StructuredQuery.FieldReference(field_path="field1"),
            op=query_pb.StructuredQuery.FieldFilter.Operator.EQUAL,
            value=_helpers.encode_value("val1"),
        )
        composite_pb = query_pb.StructuredQuery.CompositeFilter(
            op=query_pb.StructuredQuery.CompositeFilter.Operator.OPERATOR_UNSPECIFIED,
            filters=[query_pb.StructuredQuery.Filter(field_filter=filter1_pb)],
        )
        wrapped_filter_pb = query_pb.StructuredQuery.Filter(
            composite_filter=composite_pb
        )

        with pytest.raises(TypeError, match="Unexpected CompositeFilter operator type"):
            BooleanExpr._from_query_filter_pb(wrapped_filter_pb, mock_client)

    @pytest.mark.parametrize(
        "op_enum, expected_expr_func",
        [
            (query_pb.StructuredQuery.UnaryFilter.Operator.IS_NAN, expr.IsNaN),
            (
                query_pb.StructuredQuery.UnaryFilter.Operator.IS_NOT_NAN,
                lambda f: expr.Not(f.is_nan()),
            ),
            (
                query_pb.StructuredQuery.UnaryFilter.Operator.IS_NULL,
                lambda f: f.equal(None),
            ),
            (
                query_pb.StructuredQuery.UnaryFilter.Operator.IS_NOT_NULL,
                lambda f: expr.Not(f.equal(None)),
            ),
        ],
    )
    def test__from_query_filter_pb_unary_filter(
        self, mock_client, op_enum, expected_expr_func
    ):
        """
        test supported unary filters
        """
        field_path = "unary_field"
        filter_pb = query_pb.StructuredQuery.UnaryFilter(
            field=query_pb.StructuredQuery.FieldReference(field_path=field_path),
            op=op_enum,
        )
        wrapped_filter_pb = query_pb.StructuredQuery.Filter(unary_filter=filter_pb)

        result = BooleanExpr._from_query_filter_pb(wrapped_filter_pb, mock_client)

        field_expr_inst = expr.Field.of(field_path)
        expected_condition = expected_expr_func(field_expr_inst)
        # should include existance checks
        expected = expr.And(expr.Exists(field_expr_inst), expected_condition)

        assert repr(result) == repr(expected)

    def test__from_query_filter_pb_unary_filter_unknown_op(self, mock_client):
        """
        check unary filter with unsupported operator type
        """
        field_path = "unary_field"
        filter_pb = query_pb.StructuredQuery.UnaryFilter(
            field=query_pb.StructuredQuery.FieldReference(field_path=field_path),
            op=query_pb.StructuredQuery.UnaryFilter.Operator.OPERATOR_UNSPECIFIED,  # Unknown op
        )
        wrapped_filter_pb = query_pb.StructuredQuery.Filter(unary_filter=filter_pb)

        with pytest.raises(TypeError, match="Unexpected UnaryFilter operator type"):
            BooleanExpr._from_query_filter_pb(wrapped_filter_pb, mock_client)

    @pytest.mark.parametrize(
        "op_enum, value, expected_expr_func",
        [
            (
                query_pb.StructuredQuery.FieldFilter.Operator.LESS_THAN,
                10,
                expr.LessThan,
            ),
            (
                query_pb.StructuredQuery.FieldFilter.Operator.LESS_THAN_OR_EQUAL,
                10,
                expr.LessThanOrEqual,
            ),
            (
                query_pb.StructuredQuery.FieldFilter.Operator.GREATER_THAN,
                10,
                expr.GreaterThan,
            ),
            (
                query_pb.StructuredQuery.FieldFilter.Operator.GREATER_THAN_OR_EQUAL,
                10,
                expr.GreaterThanOrEqual,
            ),
            (query_pb.StructuredQuery.FieldFilter.Operator.EQUAL, 10, expr.Equal),
            (
                query_pb.StructuredQuery.FieldFilter.Operator.NOT_EQUAL,
                10,
                expr.NotEqual,
            ),
            (
                query_pb.StructuredQuery.FieldFilter.Operator.ARRAY_CONTAINS,
                10,
                expr.ArrayContains,
            ),
            (
                query_pb.StructuredQuery.FieldFilter.Operator.ARRAY_CONTAINS_ANY,
                [10, 20],
                expr.ArrayContainsAny,
            ),
            (query_pb.StructuredQuery.FieldFilter.Operator.IN, [10, 20], expr.EqualAny),
            (query_pb.StructuredQuery.FieldFilter.Operator.NOT_IN, [10, 20], expr.NotEqualAny),
        ],
    )
    def test__from_query_filter_pb_field_filter(
        self, mock_client, op_enum, value, expected_expr_func
    ):
        """
        test supported field filters
        """
        field_path = "test_field"
        value_pb = _helpers.encode_value(value)
        filter_pb = query_pb.StructuredQuery.FieldFilter(
            field=query_pb.StructuredQuery.FieldReference(field_path=field_path),
            op=op_enum,
            value=value_pb,
        )
        wrapped_filter_pb = query_pb.StructuredQuery.Filter(field_filter=filter_pb)

        result = BooleanExpr._from_query_filter_pb(wrapped_filter_pb, mock_client)

        field_expr = expr.Field.of(field_path)
        # convert values into constants
        value = (
            [expr.Constant(e) for e in value]
            if isinstance(value, list)
            else expr.Constant(value)
        )
        expected_condition = expected_expr_func(field_expr, value)
        # should include existance checks
        expected = expr.And(expr.Exists(field_expr), expected_condition)

        assert repr(result) == repr(expected)

    def test__from_query_filter_pb_field_filter_unknown_op(self, mock_client):
        """
        check field filter with unsupported operator type
        """
        field_path = "test_field"
        value_pb = _helpers.encode_value(10)
        filter_pb = query_pb.StructuredQuery.FieldFilter(
            field=query_pb.StructuredQuery.FieldReference(field_path=field_path),
            op=query_pb.StructuredQuery.FieldFilter.Operator.OPERATOR_UNSPECIFIED,  # Unknown op
            value=value_pb,
        )
        wrapped_filter_pb = query_pb.StructuredQuery.Filter(field_filter=filter_pb)

        with pytest.raises(TypeError, match="Unexpected FieldFilter operator type"):
            BooleanExpr._from_query_filter_pb(wrapped_filter_pb, mock_client)

    def test__from_query_filter_pb_unknown_filter_type(self, mock_client):
        """
        test with unsupported filter type
        """
        # Test with an unexpected protobuf type
        with pytest.raises(TypeError, match="Unexpected filter type"):
            BooleanExpr._from_query_filter_pb(document_pb.Value(), mock_client)


class TestBooleanExprClasses:
    """
    contains test methods for each Expr class that derives from BooleanExpr
    """

    def _make_arg(self, name="Mock"):
        arg = mock.Mock()
        arg.__repr__ = lambda x: name
        return arg

    def test_and(self):
        arg1 = self._make_arg()
        arg2 = self._make_arg()
        instance = expr.And(arg1, arg2)
        assert instance.name == "and"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "And(Mock, Mock)"

    def test_or(self):
        arg1 = self._make_arg("Arg1")
        arg2 = self._make_arg("Arg2")
        instance = expr.Or(arg1, arg2)
        assert instance.name == "or"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Arg1.or(Arg2)"

    def test_array_contains(self):
        arg1 = self._make_arg("ArrayField")
        arg2 = self._make_arg("Element")
        instance = expr.ArrayContains(arg1, arg2)
        assert instance.name == "array_contains"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "ArrayField.array_contains(Element)"

    def test_array_contains_any(self):
        arg1 = self._make_arg("ArrayField")
        arg2 = self._make_arg("Element1")
        arg3 = self._make_arg("Element2")
        instance = expr.ArrayContainsAny(arg1, [arg2, arg3])
        assert instance.name == "array_contains_any"
        assert isinstance(instance.params[1], ListOfExprs)
        assert instance.params[0] == arg1
        assert instance.params[1].exprs == [arg2, arg3]
        assert (
            repr(instance)
            == "ArrayField.array_contains_any(ListOfExprs([Element1, Element2]))"
        )

    def test_exists(self):
        arg1 = self._make_arg("Field")
        instance = expr.Exists(arg1)
        assert instance.name == "exists"
        assert instance.params == [arg1]
        assert repr(instance) == "Field.exists()"

    def test_equal(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.Equal(arg1, arg2)
        assert instance.name == "equal"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.equal(Right)"

    def test_greater_than_or_equal(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.GreaterThanOrEqual(arg1, arg2)
        assert instance.name == "greater_than_or_equal"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.greater_than_or_equal(Right)"

    def test_greater_than(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.GreaterThan(arg1, arg2)
        assert instance.name == "greater_than"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.greater_than(Right)"

    def test_less_than_or_equal(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.LessThanOrEqual(arg1, arg2)
        assert instance.name == "less_than_or_equal"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.less_than_or_equal(Right)"

    def test_less_than(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.LessThan(arg1, arg2)
        assert instance.name == "less_than"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.less_than(Right)"

    def test_not_equal(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.NotEqual(arg1, arg2)
        assert instance.name == "not_equal"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.not_equal(Right)"

    def test_equal_any(self):
        arg1 = self._make_arg("Field")
        arg2 = self._make_arg("Value1")
        arg3 = self._make_arg("Value2")
        instance = expr.EqualAny(arg1, [arg2, arg3])
        assert instance.name == "equal_any"
        assert isinstance(instance.params[1], ListOfExprs)
        assert instance.params[0] == arg1
        assert instance.params[1].exprs == [arg2, arg3]
        assert repr(instance) == "Field.equal_any(ListOfExprs([Value1, Value2]))"

    def test_not_equal_any(self):
        arg1 = self._make_arg("Field")
        arg2 = self._make_arg("Value1")
        arg3 = self._make_arg("Value2")
        instance = expr.NotEqualAny(arg1, [arg2, arg3])
        assert instance.name == "not_equal_any"
        assert isinstance(instance.params[1], ListOfExprs)
        assert instance.params[0] == arg1
        assert instance.params[1].exprs == [arg2, arg3]
        assert repr(instance) == "Field.not_equal_any(ListOfExprs([Value1, Value2]))"

    def test_is_nan(self):
        arg1 = self._make_arg("Value")
        instance = expr.IsNaN(arg1)
        assert instance.name == "is_nan"
        assert instance.params == [arg1]
        assert repr(instance) == "Value.is_nan()"

    def test_not(self):
        arg1 = self._make_arg("Condition")
        instance = expr.Not(arg1)
        assert instance.name == "not"
        assert instance.params == [arg1]
        assert repr(instance) == "Not(Condition)"

    def test_array_contains_all(self):
        arg1 = self._make_arg("ArrayField")
        arg2 = self._make_arg("Element1")
        arg3 = self._make_arg("Element2")
        instance = expr.ArrayContainsAll(arg1, [arg2, arg3])
        assert instance.name == "array_contains_all"
        assert isinstance(instance.params[1], ListOfExprs)
        assert instance.params[0] == arg1
        assert instance.params[1].exprs == [arg2, arg3]
        assert (
            repr(instance)
            == "ArrayField.array_contains_all(ListOfExprs([Element1, Element2]))"
        )

    def test_ends_with(self):
        arg1 = self._make_arg("Expr")
        arg2 = self._make_arg("Postfix")
        instance = expr.EndsWith(arg1, arg2)
        assert instance.name == "ends_with"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Expr.ends_with(Postfix)"

    def test_if(self):
        arg1 = self._make_arg("Condition")
        arg2 = self._make_arg("TrueExpr")
        arg3 = self._make_arg("FalseExpr")
        instance = expr.If(arg1, arg2, arg3)
        assert instance.name == "if"
        assert instance.params == [arg1, arg2, arg3]
        assert repr(instance) == "If(Condition, TrueExpr, FalseExpr)"

    def test_like(self):
        arg1 = self._make_arg("Expr")
        arg2 = self._make_arg("Pattern")
        instance = expr.Like(arg1, arg2)
        assert instance.name == "like"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Expr.like(Pattern)"

    def test_regex_contains(self):
        arg1 = self._make_arg("Expr")
        arg2 = self._make_arg("Regex")
        instance = expr.RegexContains(arg1, arg2)
        assert instance.name == "regex_contains"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Expr.regex_contains(Regex)"

    def test_regex_match(self):
        arg1 = self._make_arg("Expr")
        arg2 = self._make_arg("Regex")
        instance = expr.RegexMatch(arg1, arg2)
        assert instance.name == "regex_match"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Expr.regex_match(Regex)"

    def test_starts_with(self):
        arg1 = self._make_arg("Expr")
        arg2 = self._make_arg("Prefix")
        instance = expr.StartsWith(arg1, arg2)
        assert instance.name == "starts_with"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Expr.starts_with(Prefix)"

    def test_string_contains(self):
        arg1 = self._make_arg("Expr")
        arg2 = self._make_arg("Substring")
        instance = expr.StringContains(arg1, arg2)
        assert instance.name == "string_contains"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Expr.string_contains(Substring)"

    def test_xor(self):
        arg1 = self._make_arg("Condition1")
        arg2 = self._make_arg("Condition2")
        instance = expr.Xor([arg1, arg2])
        assert instance.name == "xor"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Xor(Condition1, Condition2)"


class TestFunctionClasses:
    """
    contains test methods for each Expr class that derives from Function
    """

    @pytest.mark.parametrize(
        "method,args,result_cls",
        [
            ("add", ("field", 2), expr.Add),
            ("subtract", ("field", 2), expr.Subtract),
            ("multiply", ("field", 2), expr.Multiply),
            ("divide", ("field", 2), expr.Divide),
            ("mod", ("field", 2), expr.Mod),
            ("abs", ("field",), expr.Abs),
            ("ceil", ("field",), expr.Ceil),
            ("exp", ("field",), expr.Exp),
            ("floor", ("field",), expr.Floor),
            ("ln", ("field",), expr.Ln),
            ("log", ("field", 10), expr.Log),
            ("pow", ("field", 2), expr.Pow),
            ("round", ("field",), expr.Round),
            ("sqrt", ("field",), expr.Sqrt),
            ("logical_maximum", ("field", 2), expr.LogicalMaximum),
            ("logical_minimum", ("field", 2), expr.LogicalMinimum),
            ("equal", ("field", 2), expr.Equal),
            ("not_equal", ("field", 2), expr.NotEqual),
            ("less_than", ("field", 2), expr.LessThan),
            ("less_than_or_equal", ("field", 2), expr.LessThanOrEqual),
            ("greater_than", ("field", 2), expr.GreaterThan),
            ("greater_than_or_equal", ("field", 2), expr.GreaterThanOrEqual),
            ("equal_any", ("field", [None]), expr.EqualAny),
            ("not_equal_any", ("field", [None]), expr.NotEqualAny),
            ("array", ([1, 2, 3],), expr.Array),
            ("array_get", ("field", 2), expr.ArrayGet),
            ("array_contains", ("field", None), expr.ArrayContains),
            ("array_contains_all", ("field", [None]), expr.ArrayContainsAll),
            ("array_contains_any", ("field", [None]), expr.ArrayContainsAny),
            ("array_length", ("field",), expr.ArrayLength),
            ("array_reverse", ("field",), expr.ArrayReverse),
            ("is_nan", ("field",), expr.IsNaN),
            ("exists", ("field",), expr.Exists),
            ("sum", ("field",), expr.Sum),
            ("average", ("field",), expr.Average),
            ("count", ("field",), expr.Count),
            ("minimum", ("field",), expr.Minimum),
            ("maximum", ("field",), expr.Maximum),
            ("char_length", ("field",), expr.CharLength),
            ("byte_length", ("field",), expr.ByteLength),
            ("like", ("field", "pattern"), expr.Like),
            ("regex_contains", ("field", "regex"), expr.RegexContains),
            ("regex_matches", ("field", "regex"), expr.RegexMatch),
            ("string_contains", ("field", "substring"), expr.StringContains),
            ("starts_with", ("field", "prefix"), expr.StartsWith),
            ("ends_with", ("field", "postfix"), expr.EndsWith),
            ("string_concat", ("field", "elem1", "elem2"), expr.StringConcat),
            ("map_get", ("field", "key"), expr.MapGet),
            ("vector_length", ("field",), expr.VectorLength),
            ("timestamp_to_unix_micros", ("field",), expr.TimestampToUnixMicros),
            ("unix_micros_to_timestamp", ("field",), expr.UnixMicrosToTimestamp),
            ("timestamp_to_unix_millis", ("field",), expr.TimestampToUnixMillis),
            ("unix_millis_to_timestamp", ("field",), expr.UnixMillisToTimestamp),
            ("timestamp_to_unix_seconds", ("field",), expr.TimestampToUnixSeconds),
            ("unix_seconds_to_timestamp", ("field",), expr.UnixSecondsToTimestamp),
            ("timestamp_add", ("field", "day", 1), expr.TimestampAdd),
            ("timestamp_subtract", ("field", "hour", 2.5), expr.TimestampSubtract),
        ],
    )
    def test_function_builder(self, method, args, result_cls):
        """
        Test building functions using methods exposed on base Function class.
        """
        method_ptr = getattr(expr.Function, method)

        result = method_ptr(*args)
        assert isinstance(result, result_cls)

    @pytest.mark.parametrize(
        "first,second,expected",
        [
            (expr.Array([]), expr.Array([]), True),
            (expr.Array([]), expr.CharLength(1), False),
            (expr.Array([]), object(), False),
            (expr.Array([]), None, False),
            (expr.CharLength(1), expr.Array([]), False),
            (expr.CharLength(1), expr.CharLength(2), False),
            (expr.CharLength(1), expr.CharLength(1), True),
            (expr.CharLength(1), expr.ByteLength(1), False),
            (expr.Array([1]), expr.Array([1]), True),
            (expr.Array([1]), expr.Array([2]), False),
            (expr.Array([1]), expr.Array([]), False),
            (expr.Array([1, 2]), expr.Array([1]), False),
        ],
    )
    def test_equality(self, first, second, expected):
        assert (first == second) is expected

    def _make_arg(self, name="Mock"):
        arg = mock.Mock()
        arg.__repr__ = lambda x: name
        return arg

    def test_divide(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.Divide(arg1, arg2)
        assert instance.name == "divide"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Divide(Left, Right)"

    def test_logical_maximum(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.LogicalMaximum(arg1, arg2)
        assert instance.name == "max"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "LogicalMaximum(Left, Right)"

    def test_logical_minimum(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.LogicalMinimum(arg1, arg2)
        assert instance.name == "min"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "LogicalMinimum(Left, Right)"

    def test_map_get(self):
        arg1 = self._make_arg("Map")
        arg2 = expr.Constant("Key")
        instance = expr.MapGet(arg1, arg2)
        assert instance.name == "map_get"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "MapGet(Map, Constant.of('Key'))"

    def test_mod(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.Mod(arg1, arg2)
        assert instance.name == "mod"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Mod(Left, Right)"

    def test_multiply(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.Multiply(arg1, arg2)
        assert instance.name == "multiply"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Multiply(Left, Right)"

    def test_parent(self):
        arg1 = self._make_arg("Value")
        instance = expr.Parent(arg1)
        assert instance.name == "parent"
        assert instance.params == [arg1]
        assert repr(instance) == "Parent(Value)"

    def test_string_concat(self):
        arg1 = self._make_arg("Str1")
        arg2 = self._make_arg("Str2")
        instance = expr.StringConcat(arg1, arg2)
        assert instance.name == "string_concat"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "StringConcat(Str1, Str2)"

    def test_subtract(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.Subtract(arg1, arg2)
        assert instance.name == "subtract"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Subtract(Left, Right)"

    def test_timestamp_add(self):
        arg1 = self._make_arg("Timestamp")
        arg2 = self._make_arg("Unit")
        arg3 = self._make_arg("Amount")
        instance = expr.TimestampAdd(arg1, arg2, arg3)
        assert instance.name == "timestamp_add"
        assert instance.params == [arg1, arg2, arg3]
        assert repr(instance) == "TimestampAdd(Timestamp, Unit, Amount)"

    def test_timestamp_subtract(self):
        arg1 = self._make_arg("Timestamp")
        arg2 = self._make_arg("Unit")
        arg3 = self._make_arg("Amount")
        instance = expr.TimestampSubtract(arg1, arg2, arg3)
        assert instance.name == "timestamp_subtract"
        assert instance.params == [arg1, arg2, arg3]
        assert repr(instance) == "TimestampSubtract(Timestamp, Unit, Amount)"

    def test_timestamp_to_unix_micros(self):
        arg1 = self._make_arg("Input")
        instance = expr.TimestampToUnixMicros(arg1)
        assert instance.name == "timestamp_to_unix_micros"
        assert instance.params == [arg1]
        assert repr(instance) == "TimestampToUnixMicros(Input)"

    def test_timestamp_to_unix_millis(self):
        arg1 = self._make_arg("Input")
        instance = expr.TimestampToUnixMillis(arg1)
        assert instance.name == "timestamp_to_unix_millis"
        assert instance.params == [arg1]
        assert repr(instance) == "TimestampToUnixMillis(Input)"

    def test_timestamp_to_unix_seconds(self):
        arg1 = self._make_arg("Input")
        instance = expr.TimestampToUnixSeconds(arg1)
        assert instance.name == "timestamp_to_unix_seconds"
        assert instance.params == [arg1]
        assert repr(instance) == "TimestampToUnixSeconds(Input)"

    def test_unix_micros_to_timestamp(self):
        arg1 = self._make_arg("Input")
        instance = expr.UnixMicrosToTimestamp(arg1)
        assert instance.name == "unix_micros_to_timestamp"
        assert instance.params == [arg1]
        assert repr(instance) == "UnixMicrosToTimestamp(Input)"

    def test_unix_millis_to_timestamp(self):
        arg1 = self._make_arg("Input")
        instance = expr.UnixMillisToTimestamp(arg1)
        assert instance.name == "unix_millis_to_timestamp"
        assert instance.params == [arg1]
        assert repr(instance) == "UnixMillisToTimestamp(Input)"

    def test_unix_seconds_to_timestamp(self):
        arg1 = self._make_arg("Input")
        instance = expr.UnixSecondsToTimestamp(arg1)
        assert instance.name == "unix_seconds_to_timestamp"
        assert instance.params == [arg1]
        assert repr(instance) == "UnixSecondsToTimestamp(Input)"

    def test_vector_length(self):
        arg1 = self._make_arg("Array")
        instance = expr.VectorLength(arg1)
        assert instance.name == "vector_length"
        assert instance.params == [arg1]
        assert repr(instance) == "VectorLength(Array)"

    def test_add(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.Add(arg1, arg2)
        assert instance.name == "add"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Add(Left, Right)"

    def test_array_length(self):
        arg1 = self._make_arg("Array")
        instance = expr.ArrayLength(arg1)
        assert instance.name == "array_length"
        assert instance.params == [arg1]
        assert repr(instance) == "ArrayLength(Array)"

    def test_array_reverse(self):
        arg1 = self._make_arg("Array")
        instance = expr.ArrayReverse(arg1)
        assert instance.name == "array_reverse"
        assert instance.params == [arg1]
        assert repr(instance) == "ArrayReverse(Array)"

    def test_byte_length(self):
        arg1 = self._make_arg("Expr")
        instance = expr.ByteLength(arg1)
        assert instance.name == "byte_length"
        assert instance.params == [arg1]
        assert repr(instance) == "ByteLength(Expr)"

    def test_char_length(self):
        arg1 = self._make_arg("Expr")
        instance = expr.CharLength(arg1)
        assert instance.name == "char_length"
        assert instance.params == [arg1]
        assert repr(instance) == "CharLength(Expr)"

    def test_collection_id(self):
        arg1 = self._make_arg("Value")
        instance = expr.CollectionId(arg1)
        assert instance.name == "collection_id"
        assert instance.params == [arg1]
        assert repr(instance) == "CollectionId(Value)"

    def test_sum(self):
        arg1 = self._make_arg("Value")
        instance = expr.Sum(arg1)
        assert instance.name == "sum"
        assert instance.params == [arg1]
        assert repr(instance) == "Sum(Value)"

    def test_average(self):
        arg1 = self._make_arg("Value")
        instance = expr.Average(arg1)
        assert instance.name == "average"
        assert instance.params == [arg1]
        assert repr(instance) == "Average(Value)"

    def test_count(self):
        arg1 = self._make_arg("Value")
        instance = expr.Count(arg1)
        assert instance.name == "count"
        assert instance.params == [arg1]
        assert repr(instance) == "Count(Value)"

    def test_count_empty(self):
        instance = expr.Count()
        assert instance.params == []
        assert repr(instance) == "Count()"

    def test_minimum(self):
        arg1 = self._make_arg("Value")
        instance = expr.Minimum(arg1)
        assert instance.name == "min"
        assert instance.params == [arg1]
        assert repr(instance) == "Minimum(Value)"

    def test_maximum(self):
        arg1 = self._make_arg("Value")
        instance = expr.Maximum(arg1)
        assert instance.name == "max"
        assert instance.params == [arg1]
        assert repr(instance) == "Maximum(Value)"

    def test_dot_product(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.DotProduct(arg1, arg2)
        assert instance.name == "dot_product"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "DotProduct(Left, Right)"

    def test_euclidean_distance(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.EuclideanDistance(arg1, arg2)
        assert instance.name == "euclidean_distance"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "EuclideanDistance(Left, Right)"

    def test_cosine_distance(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.CosineDistance(arg1, arg2)
        assert instance.name == "cosine_distance"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "CosineDistance(Left, Right)"

    def test_reverse(self):
        arg1 = self._make_arg("Expr")
        instance = expr.Reverse(arg1)
        assert instance.name == "reverse"
        assert instance.params == [arg1]
        assert repr(instance) == "Reverse(Expr)"

    def test_to_lower(self):
        arg1 = self._make_arg("Expr")
        instance = expr.ToLower(arg1)
        assert instance.name == "to_lower"
        assert instance.params == [arg1]
        assert repr(instance) == "ToLower(Expr)"

    def test_to_upper(self):
        arg1 = self._make_arg("Expr")
        instance = expr.ToUpper(arg1)
        assert instance.name == "to_upper"
        assert instance.params == [arg1]
        assert repr(instance) == "ToUpper(Expr)"

    def test_trim(self):
        arg1 = self._make_arg("Expr")
        instance = expr.Trim(arg1)
        assert instance.name == "trim"
        assert instance.params == [arg1]
        assert repr(instance) == "Trim(Expr)"

    def test_array(self):
        arg = self._make_arg("Value")
        instance = expr.Array([1, 2, arg])
        assert instance.name == "array"
        assert instance.params == [1, 2, arg]
        assert repr(instance) == "Array([1, 2, Value])"

    def test_array_get(self):
        arg1 = self._make_arg("Array")
        arg2 = self._make_arg("Index")
        instance = expr.ArrayGet(arg1, arg2)
        assert instance.name == "array_get"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "ArrayGet(Array, Index)"

    def test_array_concat(self):
        arg1 = self._make_arg("1")
        arg2 = self._make_arg("2")
        arg3 = self._make_arg("3")
        instance = expr.ArrayConcat(arg1, [arg2, arg3])
        assert instance.name == "array_concat"
        assert instance.params == [arg1, arg2, arg3]
        assert repr(instance) == "ArrayConcat(1, 2, 3)"

    def test_abs(self):
        arg1 = self._make_arg("Value")
        instance = expr.Abs(arg1)
        assert instance.name == "abs"
        assert instance.params == [arg1]
        assert repr(instance) == "Abs(Value)"

    def test_ceil(self):
        arg1 = self._make_arg("Value")
        instance = expr.Ceil(arg1)
        assert instance.name == "ceil"
        assert instance.params == [arg1]
        assert repr(instance) == "Ceil(Value)"

    def test_exp(self):
        arg1 = self._make_arg("Value")
        instance = expr.Exp(arg1)
        assert instance.name == "exp"
        assert instance.params == [arg1]
        assert repr(instance) == "Exp(Value)"

    def test_floor(self):
        arg1 = self._make_arg("Value")
        instance = expr.Floor(arg1)
        assert instance.name == "floor"
        assert instance.params == [arg1]
        assert repr(instance) == "Floor(Value)"

    def test_ln(self):
        arg1 = self._make_arg("Value")
        instance = expr.Ln(arg1)
        assert instance.name == "ln"
        assert instance.params == [arg1]
        assert repr(instance) == "Ln(Value)"

    def test_log(self):
        arg1 = self._make_arg("Value")
        arg2 = self._make_arg("Base")
        instance = expr.Log(arg1, arg2)
        assert instance.name == "log"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Log(Value, Base)"

    def test_pow(self):
        arg1 = self._make_arg("Base")
        arg2 = self._make_arg("Exponent")
        instance = expr.Pow(arg1, arg2)
        assert instance.name == "pow"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Pow(Base, Exponent)"

    def test_round(self):
        arg1 = self._make_arg("Value")
        instance = expr.Round(arg1)
        assert instance.name == "round"
        assert instance.params == [arg1]
        assert repr(instance) == "Round(Value)"

    def test_sqrt(self):
        arg1 = self._make_arg("Value")
        instance = expr.Sqrt(arg1)
        assert instance.name == "sqrt"
        assert instance.params == [arg1]
        assert repr(instance) == "Sqrt(Value)"
