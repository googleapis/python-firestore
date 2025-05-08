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
# limitations under the License.

import pytest
import mock

from google.cloud.firestore_v1 import _helpers
from google.cloud.firestore_v1.types import document as document_pb
from google.cloud.firestore_v1.types import query as query_pb
from google.cloud.firestore_v1.pipeline_expressions import FilterCondition
from google.cloud.firestore_v1 import pipeline_expressions as expr


@pytest.fixture
def mock_client():
    client = mock.Mock(spec=["_database_string", "collection"])
    client._database_string = "projects/p/databases/d"
    return client


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
