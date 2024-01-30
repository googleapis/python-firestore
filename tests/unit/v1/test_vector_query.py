# Copyright 2024 Google LLC All rights reserved.
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

import types
import mock
import pytest

from datetime import datetime, timezone, timedelta
from google.cloud.firestore_v1.types.query import StructuredQuery
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure

from google.cloud.firestore_v1.base_aggregation import (
    CountAggregation,
    SumAggregation,
    AvgAggregation,
    AggregationResult,
)
from tests.unit.v1._test_helpers import (
    make_vector_query,
    make_aggregation_query_response,
    make_client,
    make_query,
)
from tests.unit.v1.test_base_query import _make_query_response
from google.cloud.firestore_v1._helpers import encode_value

_PROJECT = "PROJECT"

def test_vector_query_constructor():
    client = make_client()
    parent = client.collection("dee")
    query = make_query(parent)
    vector_query = make_vector_query(query)

    assert vector_query._nested_query == query
    assert vector_query._client == query._parent._client

def test_vector_query_constructor_to_pb():
    client = make_client()
    parent = client.collection("dee")
    query = make_query(parent)
    vector_query = make_vector_query(query)
    vector_query.find_nearest(
        vector_field="embedding", 
        query_vector=Vector([1.0, 2.0, 3.0]),
        distance_measure=DistanceMeasure.EUCLIDEAN,
        limit=5)

    expected_pb = query._to_protobuf()
    expected_pb.find_nearest = StructuredQuery.FindNearest(
        vector_field = StructuredQuery.FieldReference(field_path = "embedding"),
        query_vector = encode_value(Vector([1.0, 2.0, 3.0]).to_map_value()),
        distance_measure = StructuredQuery.FindNearest.DistanceMeasure.EUCLIDEAN,
        limit = 5
    )
    assert vector_query._to_protobuf() == expected_pb

def test_vector_query():
    from google.cloud.firestore_v1 import _helpers

    # Create a minimal fake GAPIC.
    firestore_api = mock.Mock(spec=["run_query"])

    # Attach the fake GAPIC to a real client.
    client = make_client()
    client._firestore_api_internal = firestore_api

    # Make a **real** collection reference as parent.
    parent = client.collection("dee")
    query = make_query(parent)

    transaction = client.transaction()

    txn_id = b"\x00\x00\x01-work-\xf2"
    transaction._id = txn_id

    parent_path, expected_prefix = parent._parent_info()
    name = "{}/test_doc".format(expected_prefix)
    data = {"snooze": 10, "embedding": Vector([1.0, 2.0, 3.0])}
    response_pb = _make_query_response(name=name, data=data)
    kwargs = _helpers.make_retry_timeout_kwargs(retry=None, timeout=None)

    # Execute the vector query and check the response.
    firestore_api.run_query.return_value = iter([response_pb])

    vector_query = query.find_nearest(
        vector_field="embedding", 
        query_vector=Vector([1.0, 2.0, 3.0]),
        distance_measure=DistanceMeasure.EUCLIDEAN,
        limit=5)

    returned = vector_query.get(transaction=transaction, **kwargs)
    assert isinstance(returned, list)
    assert len(returned) == 1
    assert returned[0].to_dict() == data

    expected_pb = query._to_protobuf()
    expected_pb.find_nearest = StructuredQuery.FindNearest(
        vector_field = StructuredQuery.FieldReference(field_path = "embedding"),
        query_vector = encode_value(Vector([1.0, 2.0, 3.0]).to_map_value()),
        distance_measure = StructuredQuery.FindNearest.DistanceMeasure.EUCLIDEAN,
        limit = 5
    )

    firestore_api.run_query.assert_called_once_with(
        request={
            "parent": parent_path,
            "structured_query": vector_query._to_protobuf(),
            "transaction": txn_id,
        },
        metadata=client._rpc_metadata,
        **kwargs,
    )
