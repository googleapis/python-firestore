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
import google.cloud.firestore_v1.pipeline_expressions as expr
from google.cloud.firestore_v1.pipeline_expressions import BooleanExpr
from google.cloud.firestore_v1.pipeline_expressions import _ListOfExprs
from google.cloud.firestore_v1.pipeline_expressions import Expr
from google.cloud.firestore_v1.pipeline_expressions import Constant
from google.cloud.firestore_v1.pipeline_expressions import Field
from google.cloud.firestore_v1.pipeline_expressions import Ordering


@pytest.fixture
def mock_client():
    client = mock.Mock(spec=["_database_string", "collection"])
    client._database_string = "projects/p/databases/d"
    return client


class TestOrdering:
    @pytest.mark.parametrize(
        "direction_arg,expected_direction",
        [
            ("ASCENDING", Ordering.Direction.ASCENDING),
            ("DESCENDING", Ordering.Direction.DESCENDING),
            ("ascending", Ordering.Direction.ASCENDING),
            ("descending", Ordering.Direction.DESCENDING),
            (Ordering.Direction.ASCENDING, Ordering.Direction.ASCENDING),
            (Ordering.Direction.DESCENDING, Ordering.Direction.DESCENDING),
        ],
    )
    def test_ctor(self, direction_arg, expected_direction):
        instance = Ordering("field1", direction_arg)
        assert isinstance(instance.expr, Field)
        assert instance.expr.path == "field1"
        assert instance.order_dir == expected_direction

    def test_repr(self):
        field_expr = Field.of("field1")
        instance = Ordering(field_expr, "ASCENDING")
        repr_str = repr(instance)
        assert repr_str == "Field.of('field1').ascending()"

        instance = Ordering(field_expr, "DESCENDING")
        repr_str = repr(instance)
        assert repr_str == "Field.of('field1').descending()"

    def test_to_pb(self):
        field_expr = Field.of("field1")
        instance = Ordering(field_expr, "ASCENDING")
        result = instance._to_pb()
        assert result.map_value.fields["expression"].field_reference_value == "field1"
        assert result.map_value.fields["direction"].string_value == "ascending"

        instance = Ordering(field_expr, "DESCENDING")
        result = instance._to_pb()
        assert result.map_value.fields["expression"].field_reference_value == "field1"
        assert result.map_value.fields["direction"].string_value == "descending"


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
        instance = Constant.of(input_val)
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
        instance = Constant.of(input_val)
        repr_string = repr(instance)
        assert repr_string == expected

    @pytest.mark.parametrize(
        "first,second,expected",
        [
            (Constant.of(1), Constant.of(2), False),
            (Constant.of(1), Constant.of(1), True),
            (Constant.of(1), 1, True),
            (Constant.of(1), 2, False),
            (Constant.of("1"), 1, False),
            (Constant.of("1"), "1", True),
            (Constant.of(None), Constant.of(0), False),
            (Constant.of(None), Constant.of(None), True),
            (Constant.of([1, 2, 3]), Constant.of([1, 2, 3]), True),
            (Constant.of([1, 2, 3]), Constant.of([1, 2]), False),
            (Constant.of([1, 2, 3]), [1, 2, 3], True),
            (Constant.of([1, 2, 3]), object(), False),
        ],
    )
    def test_equality(self, first, second, expected):
        assert (first == second) is expected


class TestListOfExprs:
    def test_to_pb(self):
        instance = _ListOfExprs([Constant(1), Constant(2)])
        result = instance._to_pb()
        assert len(result.array_value.values) == 2
        assert result.array_value.values[0].integer_value == 1
        assert result.array_value.values[1].integer_value == 2

    def test_empty_to_pb(self):
        instance = _ListOfExprs([])
        result = instance._to_pb()
        assert len(result.array_value.values) == 0

    def test_repr(self):
        instance = _ListOfExprs([Constant(1), Constant(2)])
        repr_string = repr(instance)
        assert repr_string == "[Constant.of(1), Constant.of(2)]"
        empty_instance = _ListOfExprs([])
        empty_repr_string = repr(empty_instance)
        assert empty_repr_string == "[]"

    @pytest.mark.parametrize(
        "first,second,expected",
        [
            (_ListOfExprs([]), _ListOfExprs([]), True),
            (_ListOfExprs([]), _ListOfExprs([Constant(1)]), False),
            (_ListOfExprs([Constant(1)]), _ListOfExprs([]), False),
            (
                _ListOfExprs([Constant(1)]),
                _ListOfExprs([Constant(1)]),
                True,
            ),
            (
                _ListOfExprs([Constant(1)]),
                _ListOfExprs([Constant(2)]),
                False,
            ),
            (
                _ListOfExprs([Constant(1), Constant(2)]),
                _ListOfExprs([Constant(1), Constant(2)]),
                True,
            ),
            (_ListOfExprs([Constant(1)]), [Constant(1)], False),
            (_ListOfExprs([Constant(1)]), [1], False),
            (_ListOfExprs([Constant(1)]), object(), False),
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
            Field.of("field1"),
            Field.of("field2").as_("alias2"),
        ]
        result = expr.Selectable._value_from_selectables(*selectable_list)
        assert len(result.map_value.fields) == 2
        assert result.map_value.fields["field1"].field_reference_value == "field1"
        assert result.map_value.fields["alias2"].field_reference_value == "field2"

    @pytest.mark.parametrize(
        "first,second,expected",
        [
            (Field.of("field1"), Field.of("field1"), True),
            (Field.of("field1"), Field.of("field2"), False),
            (Field.of(None), object(), False),
            (Field.of("f").as_("a"), Field.of("f").as_("a"), True),
            (Field.of("one").as_("a"), Field.of("two").as_("a"), False),
            (Field.of("f").as_("one"), Field.of("f").as_("two"), False),
            (Field.of("field"), Field.of("field").as_("alias"), False),
            (Field.of("field").as_("alias"), Field.of("field"), False),
        ],
    )
    def test_equality(self, first, second, expected):
        assert (first == second) is expected

    class TestField:
        def test_repr(self):
            instance = Field.of("field1")
            repr_string = repr(instance)
            assert repr_string == "Field.of('field1')"

        def test_of(self):
            instance = Field.of("field1")
            assert instance.path == "field1"

        def test_to_pb(self):
            instance = Field.of("field1")
            result = instance._to_pb()
            assert result.field_reference_value == "field1"

        def test_to_map(self):
            instance = Field.of("field1")
            result = instance._to_map()
            assert result[0] == "field1"
            assert result[1] == Value(field_reference_value="field1")

    class TestAliasedExpr:
        def test_repr(self):
            instance = Field.of("field1").as_("alias1")
            assert repr(instance) == "Field.of('field1').as_('alias1')"

        def test_ctor(self):
            arg = Field.of("field1")
            alias = "alias1"
            instance = expr.AliasedExpr(arg, alias)
            assert instance.expr == arg
            assert instance.alias == alias

        def test_to_pb(self):
            arg = Field.of("field1")
            alias = "alias1"
            instance = expr.AliasedExpr(arg, alias)
            result = instance._to_pb()
            assert result.map_value.fields.get("alias1") == arg._to_pb()

        def test_to_map(self):
            instance = Field.of("field1").as_("alias1")
            result = instance._to_map()
            assert result[0] == "alias1"
            assert result[1] == Value(field_reference_value="field1")

    class TestAliasedAggregate:
        def test_repr(self):
            instance = Field.of("field1").maximum().as_("alias1")
            assert repr(instance) == "Field.of('field1').maximum().as_('alias1')"

        def test_ctor(self):
            arg = Expr.minimum("field1")
            alias = "alias1"
            instance = expr.AliasedAggregate(arg, alias)
            assert instance.expr == arg
            assert instance.alias == alias

        def test_to_pb(self):
            arg = Field.of("field1").average()
            alias = "alias1"
            instance = expr.AliasedAggregate(arg, alias)
            result = instance._to_pb()
            assert result.map_value.fields.get("alias1") == arg._to_pb()

        def test_to_map(self):
            arg = Field.of("field1").count()
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
        field1 = Field.of("field1")
        field2 = Field.of("field2")
        expected_cond1 = expr.And(field1.exists(), field1.equal(Constant("val1")))
        expected_cond2 = expr.And(field2.exists(), field2.is_null())
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
        field1 = Field.of("field1")
        field2 = Field.of("field2")
        expected_cond1 = expr.And(field1.exists(), field1.greater_than(Constant(100)))
        expected_cond2 = expr.And(field2.exists(), field2.less_than(Constant(200)))
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

        field1 = Field.of("field1")
        field2 = Field.of("field2")
        field3 = Field.of("field3")
        expected_cond1 = expr.And(field1.exists(), field1.equal(Constant("val1")))
        expected_cond2 = expr.And(field2.exists(), field2.greater_than(Constant(10)))
        expected_cond3 = expr.And(
            field3.exists(), expr.Not(field3.is_null())
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
            (query_pb.StructuredQuery.UnaryFilter.Operator.IS_NAN, Expr.is_nan),
            (
                query_pb.StructuredQuery.UnaryFilter.Operator.IS_NOT_NAN,
                lambda f: expr.Not(f.is_nan()),
            ),
            (
                query_pb.StructuredQuery.UnaryFilter.Operator.IS_NULL,
                lambda f: f.is_null()
            ),
            (
                query_pb.StructuredQuery.UnaryFilter.Operator.IS_NOT_NULL,
                lambda f: expr.Not(f.is_null()),
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

        field_expr_inst = Field.of(field_path)
        expected_condition = expected_expr_func(field_expr_inst)
        # should include existance checks
        expected = expr.And(field_expr_inst.exists(), expected_condition)

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
                Expr.less_than,
            ),
            (
                query_pb.StructuredQuery.FieldFilter.Operator.LESS_THAN_OR_EQUAL,
                10,
                Expr.less_than_or_equal,
            ),
            (
                query_pb.StructuredQuery.FieldFilter.Operator.GREATER_THAN,
                10,
                Expr.greater_than,
            ),
            (
                query_pb.StructuredQuery.FieldFilter.Operator.GREATER_THAN_OR_EQUAL,
                10,
                Expr.greater_than_or_equal,
            ),
            (query_pb.StructuredQuery.FieldFilter.Operator.EQUAL, 10, Expr.equal),
            (
                query_pb.StructuredQuery.FieldFilter.Operator.NOT_EQUAL,
                10,
                Expr.not_equal,
            ),
            (
                query_pb.StructuredQuery.FieldFilter.Operator.ARRAY_CONTAINS,
                10,
                Expr.array_contains,
            ),
            (
                query_pb.StructuredQuery.FieldFilter.Operator.ARRAY_CONTAINS_ANY,
                [10, 20],
                Expr.array_contains_any,
            ),
            (
                query_pb.StructuredQuery.FieldFilter.Operator.IN,
                [10, 20],
                Expr.equal_any,
            ),
            (
                query_pb.StructuredQuery.FieldFilter.Operator.NOT_IN,
                [10, 20],
                Expr.not_equal_any,
            ),
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

        field_expr = Field.of(field_path)
        # convert values into constants
        value = (
            [Constant(e) for e in value] if isinstance(value, list) else Constant(value)
        )
        expected_condition = expected_expr_func(field_expr, value)
        # should include existance checks
        expected = expr.And(field_expr.exists(), expected_condition)

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


class TestExpressionMethods:
    """
    contains test methods for each Expr method
    """

    @pytest.mark.parametrize(
        "first,second,expected",
        [
            (
                Field.of("a").char_length(),
                Field.of("a").char_length(),
                True,
            ),
            (
                Field.of("a").char_length(),
                Field.of("b").char_length(),
                False,
            ),
            (
                Field.of("a").char_length(),
                Field.of("a").byte_length(),
                False,
            ),
            (
                Field.of("a").char_length(),
                Field.of("b").byte_length(),
                False,
            ),
            (
                Constant.of("").byte_length(),
                Field.of("").byte_length(),
                False,
            ),
            (Field.of("").byte_length(), Field.of("").byte_length(), True),
        ],
    )
    def test_equality(self, first, second, expected):
        assert (first == second) is expected

    def _make_arg(self, name="Mock"):
        class MockExpr(Constant):
            def __repr__(self):
                return self.value

        arg = MockExpr(name)
        return arg

    def test_and(self):
        arg1 = self._make_arg()
        arg2 = self._make_arg()
        arg3 = self._make_arg()
        instance = expr.And(arg1, arg2, arg3)
        assert instance.name == "and"
        assert instance.params == [arg1, arg2, arg3]
        assert repr(instance) == "And(Mock, Mock, Mock)"

    def test_or(self):
        arg1 = self._make_arg("Arg1")
        arg2 = self._make_arg("Arg2")
        instance = expr.Or(arg1, arg2)
        assert instance.name == "or"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Or(Arg1, Arg2)"

    def test_array_contains(self):
        arg1 = self._make_arg("ArrayField")
        arg2 = self._make_arg("Element")
        instance = Expr.array_contains(arg1, arg2)
        assert instance.name == "array_contains"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "ArrayField.array_contains(Element)"
        infix_instance = arg1.array_contains(arg2)
        assert infix_instance == instance

    def test_array_contains_any(self):
        arg1 = self._make_arg("ArrayField")
        arg2 = self._make_arg("Element1")
        arg3 = self._make_arg("Element2")
        instance = Expr.array_contains_any(arg1, [arg2, arg3])
        assert instance.name == "array_contains_any"
        assert isinstance(instance.params[1], _ListOfExprs)
        assert instance.params[0] == arg1
        assert instance.params[1].exprs == [arg2, arg3]
        assert repr(instance) == "ArrayField.array_contains_any([Element1, Element2])"
        infix_instance = arg1.array_contains_any([arg2, arg3])
        assert infix_instance == instance

    def test_exists(self):
        arg1 = self._make_arg("Field")
        instance = Expr.exists(arg1)
        assert instance.name == "exists"
        assert instance.params == [arg1]
        assert repr(instance) == "Field.exists()"
        infix_instance = arg1.exists()
        assert infix_instance == instance

    def test_equal(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = Expr.equal(arg1, arg2)
        assert instance.name == "equal"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.equal(Right)"
        infix_instance = arg1.equal(arg2)
        assert infix_instance == instance

    def test_greater_than_or_equal(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = Expr.greater_than_or_equal(arg1, arg2)
        assert instance.name == "greater_than_or_equal"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.greater_than_or_equal(Right)"
        infix_instance = arg1.greater_than_or_equal(arg2)
        assert infix_instance == instance

    def test_greater_than(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = Expr.greater_than(arg1, arg2)
        assert instance.name == "greater_than"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.greater_than(Right)"
        infix_instance = arg1.greater_than(arg2)
        assert infix_instance == instance

    def test_less_than_or_equal(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = Expr.less_than_or_equal(arg1, arg2)
        assert instance.name == "less_than_or_equal"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.less_than_or_equal(Right)"
        infix_instance = arg1.less_than_or_equal(arg2)
        assert infix_instance == instance

    def test_less_than(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = Expr.less_than(arg1, arg2)
        assert instance.name == "less_than"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.less_than(Right)"
        infix_instance = arg1.less_than(arg2)
        assert infix_instance == instance

    def test_not_equal(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = Expr.not_equal(arg1, arg2)
        assert instance.name == "not_equal"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.not_equal(Right)"
        infix_instance = arg1.not_equal(arg2)
        assert infix_instance == instance

    def test_equal_any(self):
        arg1 = self._make_arg("Field")
        arg2 = self._make_arg("Value1")
        arg3 = self._make_arg("Value2")
        instance = Expr.equal_any(arg1, [arg2, arg3])
        assert instance.name == "equal_any"
        assert isinstance(instance.params[1], _ListOfExprs)
        assert instance.params[0] == arg1
        assert instance.params[1].exprs == [arg2, arg3]
        assert repr(instance) == "Field.equal_any([Value1, Value2])"
        infix_instance = arg1.equal_any([arg2, arg3])
        assert infix_instance == instance

    def test_not_equal_any(self):
        arg1 = self._make_arg("Field")
        arg2 = self._make_arg("Value1")
        arg3 = self._make_arg("Value2")
        instance = Expr.not_equal_any(arg1, [arg2, arg3])
        assert instance.name == "not_equal_any"
        assert isinstance(instance.params[1], _ListOfExprs)
        assert instance.params[0] == arg1
        assert instance.params[1].exprs == [arg2, arg3]
        assert repr(instance) == "Field.not_equal_any([Value1, Value2])"
        infix_instance = arg1.not_equal_any([arg2, arg3])
        assert infix_instance == instance

    def test_is_nan(self):
        arg1 = self._make_arg("Value")
        instance = Expr.is_nan(arg1)
        assert instance.name == "is_nan"
        assert instance.params == [arg1]
        assert repr(instance) == "Value.is_nan()"
        infix_instance = arg1.is_nan()
        assert infix_instance == instance

    def test_is_null(self):
        arg1 = self._make_arg("Value")
        instance = Expr.is_null(arg1)
        assert instance.name == "is_null"
        assert instance.params == [arg1]
        assert repr(instance) == "Value.is_null()"
        infix_instance = arg1.is_null()
        assert infix_instance == instance

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
        instance = Expr.array_contains_all(arg1, [arg2, arg3])
        assert instance.name == "array_contains_all"
        assert isinstance(instance.params[1], _ListOfExprs)
        assert instance.params[0] == arg1
        assert instance.params[1].exprs == [arg2, arg3]
        assert repr(instance) == "ArrayField.array_contains_all([Element1, Element2])"
        infix_instance = arg1.array_contains_all([arg2, arg3])
        assert infix_instance == instance

    def test_ends_with(self):
        arg1 = self._make_arg("Expr")
        arg2 = self._make_arg("Postfix")
        instance = Expr.ends_with(arg1, arg2)
        assert instance.name == "ends_with"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Expr.ends_with(Postfix)"
        infix_instance = arg1.ends_with(arg2)
        assert infix_instance == instance

    def test_conditional(self):
        arg1 = self._make_arg("Condition")
        arg2 = self._make_arg("ThenExpr")
        arg3 = self._make_arg("ElseExpr")
        instance = expr.Conditional(arg1, arg2, arg3)
        assert instance.name == "conditional"
        assert instance.params == [arg1, arg2, arg3]
        assert repr(instance) == "Conditional(Condition, ThenExpr, ElseExpr)"

    def test_like(self):
        arg1 = self._make_arg("Expr")
        arg2 = self._make_arg("Pattern")
        instance = Expr.like(arg1, arg2)
        assert instance.name == "like"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Expr.like(Pattern)"
        infix_instance = arg1.like(arg2)
        assert infix_instance == instance

    def test_regex_contains(self):
        arg1 = self._make_arg("Expr")
        arg2 = self._make_arg("Regex")
        instance = Expr.regex_contains(arg1, arg2)
        assert instance.name == "regex_contains"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Expr.regex_contains(Regex)"
        infix_instance = arg1.regex_contains(arg2)
        assert infix_instance == instance

    def test_regex_match(self):
        arg1 = self._make_arg("Expr")
        arg2 = self._make_arg("Regex")
        instance = Expr.regex_match(arg1, arg2)
        assert instance.name == "regex_match"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Expr.regex_match(Regex)"
        infix_instance = arg1.regex_match(arg2)
        assert infix_instance == instance

    def test_starts_with(self):
        arg1 = self._make_arg("Expr")
        arg2 = self._make_arg("Prefix")
        instance = Expr.starts_with(arg1, arg2)
        assert instance.name == "starts_with"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Expr.starts_with(Prefix)"
        infix_instance = arg1.starts_with(arg2)
        assert infix_instance == instance

    def test_string_contains(self):
        arg1 = self._make_arg("Expr")
        arg2 = self._make_arg("Substring")
        instance = Expr.string_contains(arg1, arg2)
        assert instance.name == "string_contains"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Expr.string_contains(Substring)"
        infix_instance = arg1.string_contains(arg2)
        assert infix_instance == instance

    def test_xor(self):
        arg1 = self._make_arg("Condition1")
        arg2 = self._make_arg("Condition2")
        instance = expr.Xor([arg1, arg2])
        assert instance.name == "xor"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Xor(Condition1, Condition2)"

    def test_divide(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = Expr.divide(arg1, arg2)
        assert instance.name == "divide"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.divide(Right)"
        infix_instance = arg1.divide(arg2)
        assert infix_instance == instance

    def test_logical_maximum(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = Expr.logical_maximum(arg1, arg2)
        assert instance.name == "maximum"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.logical_maximum(Right)"
        infix_instance = arg1.logical_maximum(arg2)
        assert infix_instance == instance

    def test_logical_minimum(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = Expr.logical_minimum(arg1, arg2)
        assert instance.name == "minimum"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.logical_minimum(Right)"
        infix_instance = arg1.logical_minimum(arg2)
        assert infix_instance == instance

    def test_map_get(self):
        arg1 = self._make_arg("Map")
        arg2 = "key"
        instance = Expr.map_get(arg1, arg2)
        assert instance.name == "map_get"
        assert instance.params == [arg1, Constant.of(arg2)]
        assert repr(instance) == "Map.map_get(Constant.of('key'))"
        infix_instance = arg1.map_get(Constant.of(arg2))
        assert infix_instance == instance

    def test_mod(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = Expr.mod(arg1, arg2)
        assert instance.name == "mod"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.mod(Right)"
        infix_instance = arg1.mod(arg2)
        assert infix_instance == instance

    def test_multiply(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = Expr.multiply(arg1, arg2)
        assert instance.name == "multiply"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.multiply(Right)"
        infix_instance = arg1.multiply(arg2)
        assert infix_instance == instance

    def test_string_concat(self):
        arg1 = self._make_arg("Str1")
        arg2 = self._make_arg("Str2")
        arg3 = self._make_arg("Str3")
        instance = Expr.string_concat(arg1, arg2, arg3)
        assert instance.name == "string_concat"
        assert instance.params == [arg1, arg2, arg3]
        assert repr(instance) == "Str1.string_concat(Str2, Str3)"
        infix_instance = arg1.string_concat(arg2, arg3)
        assert infix_instance == instance

    def test_subtract(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = Expr.subtract(arg1, arg2)
        assert instance.name == "subtract"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.subtract(Right)"
        infix_instance = arg1.subtract(arg2)
        assert infix_instance == instance

    def test_timestamp_add(self):
        arg1 = self._make_arg("Timestamp")
        arg2 = self._make_arg("Unit")
        arg3 = self._make_arg("Amount")
        instance = Expr.timestamp_add(arg1, arg2, arg3)
        assert instance.name == "timestamp_add"
        assert instance.params == [arg1, arg2, arg3]
        assert repr(instance) == "Timestamp.timestamp_add(Unit, Amount)"
        infix_instance = arg1.timestamp_add(arg2, arg3)
        assert infix_instance == instance

    def test_timestamp_subtract(self):
        arg1 = self._make_arg("Timestamp")
        arg2 = self._make_arg("Unit")
        arg3 = self._make_arg("Amount")
        instance = Expr.timestamp_subtract(arg1, arg2, arg3)
        assert instance.name == "timestamp_subtract"
        assert instance.params == [arg1, arg2, arg3]
        assert repr(instance) == "Timestamp.timestamp_subtract(Unit, Amount)"
        infix_instance = arg1.timestamp_subtract(arg2, arg3)
        assert infix_instance == instance

    def test_timestamp_to_unix_micros(self):
        arg1 = self._make_arg("Input")
        instance = Expr.timestamp_to_unix_micros(arg1)
        assert instance.name == "timestamp_to_unix_micros"
        assert instance.params == [arg1]
        assert repr(instance) == "Input.timestamp_to_unix_micros()"
        infix_instance = arg1.timestamp_to_unix_micros()
        assert infix_instance == instance

    def test_timestamp_to_unix_millis(self):
        arg1 = self._make_arg("Input")
        instance = Expr.timestamp_to_unix_millis(arg1)
        assert instance.name == "timestamp_to_unix_millis"
        assert instance.params == [arg1]
        assert repr(instance) == "Input.timestamp_to_unix_millis()"
        infix_instance = arg1.timestamp_to_unix_millis()
        assert infix_instance == instance

    def test_timestamp_to_unix_seconds(self):
        arg1 = self._make_arg("Input")
        instance = Expr.timestamp_to_unix_seconds(arg1)
        assert instance.name == "timestamp_to_unix_seconds"
        assert instance.params == [arg1]
        assert repr(instance) == "Input.timestamp_to_unix_seconds()"
        infix_instance = arg1.timestamp_to_unix_seconds()
        assert infix_instance == instance

    def test_unix_micros_to_timestamp(self):
        arg1 = self._make_arg("Input")
        instance = Expr.unix_micros_to_timestamp(arg1)
        assert instance.name == "unix_micros_to_timestamp"
        assert instance.params == [arg1]
        assert repr(instance) == "Input.unix_micros_to_timestamp()"
        infix_instance = arg1.unix_micros_to_timestamp()
        assert infix_instance == instance

    def test_unix_millis_to_timestamp(self):
        arg1 = self._make_arg("Input")
        instance = Expr.unix_millis_to_timestamp(arg1)
        assert instance.name == "unix_millis_to_timestamp"
        assert instance.params == [arg1]
        assert repr(instance) == "Input.unix_millis_to_timestamp()"
        infix_instance = arg1.unix_millis_to_timestamp()
        assert infix_instance == instance

    def test_unix_seconds_to_timestamp(self):
        arg1 = self._make_arg("Input")
        instance = Expr.unix_seconds_to_timestamp(arg1)
        assert instance.name == "unix_seconds_to_timestamp"
        assert instance.params == [arg1]
        assert repr(instance) == "Input.unix_seconds_to_timestamp()"
        infix_instance = arg1.unix_seconds_to_timestamp()
        assert infix_instance == instance

    def test_vector_length(self):
        arg1 = self._make_arg("Array")
        instance = Expr.vector_length(arg1)
        assert instance.name == "vector_length"
        assert instance.params == [arg1]
        assert repr(instance) == "Array.vector_length()"
        infix_instance = arg1.vector_length()
        assert infix_instance == instance

    def test_add(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = Expr.add(arg1, arg2)
        assert instance.name == "add"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.add(Right)"
        infix_instance = arg1.add(arg2)
        assert infix_instance == instance

    def test_array_length(self):
        arg1 = self._make_arg("Array")
        instance = Expr.array_length(arg1)
        assert instance.name == "array_length"
        assert instance.params == [arg1]
        assert repr(instance) == "Array.array_length()"
        infix_instance = arg1.array_length()
        assert infix_instance == instance

    def test_array_reverse(self):
        arg1 = self._make_arg("Array")
        instance = Expr.array_reverse(arg1)
        assert instance.name == "array_reverse"
        assert instance.params == [arg1]
        assert repr(instance) == "Array.array_reverse()"
        infix_instance = arg1.array_reverse()
        assert infix_instance == instance

    def test_byte_length(self):
        arg1 = self._make_arg("Expr")
        instance = Expr.byte_length(arg1)
        assert instance.name == "byte_length"
        assert instance.params == [arg1]
        assert repr(instance) == "Expr.byte_length()"
        infix_instance = arg1.byte_length()
        assert infix_instance == instance

    def test_char_length(self):
        arg1 = self._make_arg("Expr")
        instance = Expr.char_length(arg1)
        assert instance.name == "char_length"
        assert instance.params == [arg1]
        assert repr(instance) == "Expr.char_length()"
        infix_instance = arg1.char_length()
        assert infix_instance == instance

    def test_collection_id(self):
        arg1 = self._make_arg("Value")
        instance = Expr.collection_id(arg1)
        assert instance.name == "collection_id"
        assert instance.params == [arg1]
        assert repr(instance) == "Value.collection_id()"
        infix_instance = arg1.collection_id()
        assert infix_instance == instance

    def test_sum(self):
        arg1 = self._make_arg("Value")
        instance = Expr.sum(arg1)
        assert instance.name == "sum"
        assert instance.params == [arg1]
        assert repr(instance) == "Value.sum()"
        infix_instance = arg1.sum()
        assert infix_instance == instance

    def test_average(self):
        arg1 = self._make_arg("Value")
        instance = Expr.average(arg1)
        assert instance.name == "average"
        assert instance.params == [arg1]
        assert repr(instance) == "Value.average()"
        infix_instance = arg1.average()
        assert infix_instance == instance

    def test_count(self):
        arg1 = self._make_arg("Value")
        instance = Expr.count(arg1)
        assert instance.name == "count"
        assert instance.params == [arg1]
        assert repr(instance) == "Value.count()"
        infix_instance = arg1.count()
        assert infix_instance == instance

    def test_base_count(self):
        instance = expr.Count()
        assert instance.name == "count"
        assert instance.params == []
        assert repr(instance) == "Count()"

    def test_minimum(self):
        arg1 = self._make_arg("Value")
        instance = Expr.minimum(arg1)
        assert instance.name == "minimum"
        assert instance.params == [arg1]
        assert repr(instance) == "Value.minimum()"
        infix_instance = arg1.minimum()
        assert infix_instance == instance

    def test_maximum(self):
        arg1 = self._make_arg("Value")
        instance = Expr.maximum(arg1)
        assert instance.name == "maximum"
        assert instance.params == [arg1]
        assert repr(instance) == "Value.maximum()"
        infix_instance = arg1.maximum()
        assert infix_instance == instance
