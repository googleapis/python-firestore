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
from google.cloud.firestore_v1.pipeline_expressions import FilterCondition, ListOfExprs
import google.cloud.firestore_v1.pipeline_expressions as expr


@pytest.fixture
def mock_client():
    client = mock.Mock(spec=["_database_string", "collection"])
    client._database_string = "projects/p/databases/d"
    return client


class TestExpr:
    def test_ctor(self):
        """
        Base class should be abstract
        """
        with pytest.raises(TypeError):
            expr.Expr()


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


class TestFilterCondition:
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

        result = FilterCondition._from_query_filter_pb(wrapped_filter_pb, mock_client)

        # should include existance checks
        expected_cond1 = expr.And(
            expr.Exists(expr.Field.of("field1")),
            expr.Eq(expr.Field.of("field1"), expr.Constant("val1")),
        )
        expected_cond2 = expr.And(
            expr.Exists(expr.Field.of("field2")),
            expr.Eq(expr.Field.of("field2"), expr.Constant(None)),
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

        result = FilterCondition._from_query_filter_pb(wrapped_filter_pb, mock_client)

        # should include existance checks
        expected_cond1 = expr.And(
            expr.Exists(expr.Field.of("field1")),
            expr.Gt(expr.Field.of("field1"), expr.Constant(100)),
        )
        expected_cond2 = expr.And(
            expr.Exists(expr.Field.of("field2")),
            expr.Lt(expr.Field.of("field2"), expr.Constant(200)),
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

        result = FilterCondition._from_query_filter_pb(wrapped_filter_pb, mock_client)

        expected_cond1 = expr.And(
            expr.Exists(expr.Field.of("field1")),
            expr.Eq(expr.Field.of("field1"), expr.Constant("val1")),
        )
        expected_cond2 = expr.And(
            expr.Exists(expr.Field.of("field2")),
            expr.Gt(expr.Field.of("field2"), expr.Constant(10)),
        )
        expected_cond3 = expr.And(
            expr.Exists(expr.Field.of("field3")),
            expr.Not(expr.Eq(expr.Field.of("field3"), expr.Constant(None))),
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
            FilterCondition._from_query_filter_pb(wrapped_filter_pb, mock_client)

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
                lambda f: f.eq(None),
            ),
            (
                query_pb.StructuredQuery.UnaryFilter.Operator.IS_NOT_NULL,
                lambda f: expr.Not(f.eq(None)),
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

        result = FilterCondition._from_query_filter_pb(wrapped_filter_pb, mock_client)

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
            FilterCondition._from_query_filter_pb(wrapped_filter_pb, mock_client)

    @pytest.mark.parametrize(
        "op_enum, value, expected_expr_func",
        [
            (query_pb.StructuredQuery.FieldFilter.Operator.LESS_THAN, 10, expr.Lt),
            (
                query_pb.StructuredQuery.FieldFilter.Operator.LESS_THAN_OR_EQUAL,
                10,
                expr.Lte,
            ),
            (query_pb.StructuredQuery.FieldFilter.Operator.GREATER_THAN, 10, expr.Gt),
            (
                query_pb.StructuredQuery.FieldFilter.Operator.GREATER_THAN_OR_EQUAL,
                10,
                expr.Gte,
            ),
            (query_pb.StructuredQuery.FieldFilter.Operator.EQUAL, 10, expr.Eq),
            (query_pb.StructuredQuery.FieldFilter.Operator.NOT_EQUAL, 10, expr.Neq),
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
            (query_pb.StructuredQuery.FieldFilter.Operator.IN, [10, 20], expr.In),
            (
                query_pb.StructuredQuery.FieldFilter.Operator.NOT_IN,
                [10, 20],
                lambda f, v: expr.Not(f.in_any(v)),
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

        result = FilterCondition._from_query_filter_pb(wrapped_filter_pb, mock_client)

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
            FilterCondition._from_query_filter_pb(wrapped_filter_pb, mock_client)

    def test__from_query_filter_pb_unknown_filter_type(self, mock_client):
        """
        test with unsupported filter type
        """
        # Test with an unexpected protobuf type
        with pytest.raises(TypeError, match="Unexpected filter type"):
            FilterCondition._from_query_filter_pb(document_pb.Value(), mock_client)


    @pytest.mark.parametrize("method,args,result_cls", [
        ("eq", (2,), expr.Eq),
        ("neq", (2,), expr.Neq),
        ("lt", (2,), expr.Lt),
        ("lte", (2,), expr.Lte),
        ("gt", (2,), expr.Gt),
        ("gte", (2,), expr.Gte),
        ("in_any", ([None],), expr.In),
        ("not_in_any", ([None],), expr.Not),
        ("array_contains", (None,), expr.ArrayContains),
        ("array_contains_any", ([None],), expr.ArrayContainsAny),
        ("is_nan", (), expr.IsNaN),
        ("exists", (), expr.Exists),
    ])
    def test_infix_call(self, method, args, result_cls):
        """
        most FilterExpressions should support infix execution
        """
        base_instance = expr.Constant(1)
        method_ptr = getattr(base_instance, method)

        result = method_ptr(*args)
        assert isinstance(result, result_cls)

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
        assert repr(instance) == "Or(Arg1, Arg2)"

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
        assert repr(instance) == "ArrayField.array_contains_any(ListOfExprs([Element1, Element2]))"

    def test_exists(self):
        arg1 = self._make_arg("Field")
        instance = expr.Exists(arg1)
        assert instance.name == "exists"
        assert instance.params == [arg1]
        assert repr(instance) == "Field.exists()"

    def test_eq(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.Eq(arg1, arg2)
        assert instance.name == "eq"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.eq(Right)"

    def test_gte(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.Gte(arg1, arg2)
        assert instance.name == "gte"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.gte(Right)"

    def test_gt(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.Gt(arg1, arg2)
        assert instance.name == "gt"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.gt(Right)"

    def test_lte(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.Lte(arg1, arg2)
        assert instance.name == "lte"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.lte(Right)"

    def test_lt(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.Lt(arg1, arg2)
        assert instance.name == "lt"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.lt(Right)"

    def test_neq(self):
        arg1 = self._make_arg("Left")
        arg2 = self._make_arg("Right")
        instance = expr.Neq(arg1, arg2)
        assert instance.name == "neq"
        assert instance.params == [arg1, arg2]
        assert repr(instance) == "Left.neq(Right)"

    def test_in(self):
        arg1 = self._make_arg("Field")
        arg2 = self._make_arg("Value1")
        arg3 = self._make_arg("Value2")
        instance = expr.In(arg1, [arg2, arg3])
        assert instance.name == "in"
        assert isinstance(instance.params[1], ListOfExprs)
        assert instance.params[0] == arg1
        assert instance.params[1].exprs == [arg2, arg3]
        assert repr(instance) == "Field.in_any(ListOfExprs([Value1, Value2]))"

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
