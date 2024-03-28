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

import mock
import pytest
import types

from google.cloud.firestore_v1.types.query import StructuredQuery
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure

from tests.unit.v1._test_helpers import (
    make_vector_query,
    make_client,
    make_query,
)
from tests.unit.v1.test_base_query import _make_query_response
from google.cloud.firestore_v1._helpers import encode_value, make_retry_timeout_kwargs

_PROJECT = "PROJECT"
_TXN_ID = b"\x00\x00\x01-work-\xf2"


@pytest.mark.parametrize(
    "distance_measure, expected_distance",
    [
        (
            DistanceMeasure.EUCLIDEAN,
            StructuredQuery.FindNearest.DistanceMeasure.EUCLIDEAN,
        ),
        (DistanceMeasure.COSINE, StructuredQuery.FindNearest.DistanceMeasure.COSINE),
        (
            DistanceMeasure.DOT_PRODUCT,
            StructuredQuery.FindNearest.DistanceMeasure.DOT_PRODUCT,
        ),
    ],
)
def test_vector_query_constructor_to_pb(distance_measure, expected_distance):
    client = make_client()
    parent = client.collection("dee")
    query = make_query(parent)
    vector_query = make_vector_query(query)

    assert vector_query._nested_query == query
    assert vector_query._client == query._parent._client

    vector_query.find_nearest(
        vector_field="embedding",
        query_vector=Vector([1.0, 2.0, 3.0]),
        distance_measure=distance_measure,
        limit=5,
    )

    expected_pb = query._to_protobuf()
    expected_pb.find_nearest = StructuredQuery.FindNearest(
        vector_field=StructuredQuery.FieldReference(field_path="embedding"),
        query_vector=encode_value(Vector([1.0, 2.0, 3.0]).to_map_value()),
        distance_measure=expected_distance,
        limit=5,
    )
    assert vector_query._to_protobuf() == expected_pb


def test_vector_query_invalid_distance():
    client = make_client()
    parent = client.collection("dee")
    query = make_query(parent)
    vector_query = make_vector_query(query)

    vector_query.find_nearest(
        vector_field="embedding",
        query_vector=Vector([1.0, 2.0, 3.0]),
        distance_measure="random",
        limit=5,
    )

    try:
        vector_query._to_protobuf()
    except ValueError as e:
        assert e.args[0] == "Invalid distance_measure"


def _transaction(client):
    transaction = client.transaction()
    txn_id = _TXN_ID
    transaction._id = txn_id
    return transaction


def _expected_pb(parent, vector_field, vector, distance_type, limit):
    query = make_query(parent)
    expected_pb = query._to_protobuf()
    expected_pb.find_nearest = StructuredQuery.FindNearest(
        vector_field=StructuredQuery.FieldReference(field_path=vector_field),
        query_vector=encode_value(vector.to_map_value()),
        distance_measure=distance_type,
        limit=limit,
    )
    return expected_pb


@pytest.mark.parametrize(
    "distance_measure, expected_distance",
    [
        (
            DistanceMeasure.EUCLIDEAN,
            StructuredQuery.FindNearest.DistanceMeasure.EUCLIDEAN,
        ),
        (DistanceMeasure.COSINE, StructuredQuery.FindNearest.DistanceMeasure.COSINE),
        (
            DistanceMeasure.DOT_PRODUCT,
            StructuredQuery.FindNearest.DistanceMeasure.DOT_PRODUCT,
        ),
    ],
)
def test_vector_query(distance_measure, expected_distance):
    # Create a minimal fake GAPIC.
    firestore_api = mock.Mock(spec=["run_query"])
    client = make_client()
    client._firestore_api_internal = firestore_api

    # Make a **real** collection reference as parent.
    parent = client.collection("dee")
    parent_path, expected_prefix = parent._parent_info()

    data = {"snooze": 10, "embedding": Vector([1.0, 2.0, 3.0])}
    response_pb = _make_query_response(
        name="{}/test_doc".format(expected_prefix), data=data
    )

    kwargs = make_retry_timeout_kwargs(retry=None, timeout=None)

    # Execute the vector query and check the response.
    firestore_api.run_query.return_value = iter([response_pb])

    vector_query = parent.find_nearest(
        vector_field="embedding",
        query_vector=Vector([1.0, 2.0, 3.0]),
        distance_measure=distance_measure,
        limit=5,
    )

    returned = vector_query.get(transaction=_transaction(client), **kwargs)
    assert isinstance(returned, list)
    assert len(returned) == 1
    assert returned[0].to_dict() == data

    expected_pb = _expected_pb(
        parent=parent,
        vector_field="embedding",
        vector=Vector([1.0, 2.0, 3.0]),
        distance_type=expected_distance,
        limit=5,
    )
    firestore_api.run_query.assert_called_once_with(
        request={
            "parent": parent_path,
            "structured_query": expected_pb,
            "transaction": _TXN_ID,
        },
        metadata=client._rpc_metadata,
        **kwargs,
    )


@pytest.mark.parametrize(
    "distance_measure, expected_distance",
    [
        (
            DistanceMeasure.EUCLIDEAN,
            StructuredQuery.FindNearest.DistanceMeasure.EUCLIDEAN,
        ),
        (DistanceMeasure.COSINE, StructuredQuery.FindNearest.DistanceMeasure.COSINE),
        (
            DistanceMeasure.DOT_PRODUCT,
            StructuredQuery.FindNearest.DistanceMeasure.DOT_PRODUCT,
        ),
    ],
)
def test_vector_query_with_filter(distance_measure, expected_distance):
    # Create a minimal fake GAPIC.
    firestore_api = mock.Mock(spec=["run_query"])
    client = make_client()
    client._firestore_api_internal = firestore_api

    # Make a **real** collection reference as parent.
    parent = client.collection("dee")
    query = make_query(parent)
    parent_path, expected_prefix = parent._parent_info()

    data = {"snooze": 10, "embedding": Vector([1.0, 2.0, 3.0])}
    response_pb1 = _make_query_response(
        name="{}/test_doc".format(expected_prefix), data=data
    )
    response_pb2 = _make_query_response(
        name="{}/test_doc".format(expected_prefix), data=data
    )

    kwargs = make_retry_timeout_kwargs(retry=None, timeout=None)

    # Execute the vector query and check the response.
    firestore_api.run_query.return_value = iter([response_pb1, response_pb2])

    vector_query = query.where("snooze", "==", 10).find_nearest(
        vector_field="embedding",
        query_vector=Vector([1.0, 2.0, 3.0]),
        distance_measure=distance_measure,
        limit=5,
    )

    returned = vector_query.get(transaction=_transaction(client), **kwargs)
    assert isinstance(returned, list)
    assert len(returned) == 2
    assert returned[0].to_dict() == data

    expected_pb = _expected_pb(
        parent=parent,
        vector_field="embedding",
        vector=Vector([1.0, 2.0, 3.0]),
        distance_type=expected_distance,
        limit=5,
    )
    expected_pb.where = StructuredQuery.Filter(
        field_filter=StructuredQuery.FieldFilter(
            field=StructuredQuery.FieldReference(field_path="snooze"),
            op=StructuredQuery.FieldFilter.Operator.EQUAL,
            value=encode_value(10),
        )
    )

    firestore_api.run_query.assert_called_once_with(
        request={
            "parent": parent_path,
            "structured_query": expected_pb,
            "transaction": _TXN_ID,
        },
        metadata=client._rpc_metadata,
        **kwargs,
    )


@pytest.mark.parametrize(
    "distance_measure, expected_distance",
    [
        (
            DistanceMeasure.EUCLIDEAN,
            StructuredQuery.FindNearest.DistanceMeasure.EUCLIDEAN,
        ),
        (DistanceMeasure.COSINE, StructuredQuery.FindNearest.DistanceMeasure.COSINE),
        (
            DistanceMeasure.DOT_PRODUCT,
            StructuredQuery.FindNearest.DistanceMeasure.DOT_PRODUCT,
        ),
    ],
)
def test_vector_query_collection_group(distance_measure, expected_distance):
    # Create a minimal fake GAPIC.
    firestore_api = mock.Mock(spec=["run_query"])
    client = make_client()
    client._firestore_api_internal = firestore_api

    # Make a **real** collection group reference as parent.
    collection_group_ref = client.collection_group("dee")

    data = {"snooze": 10, "embedding": Vector([1.0, 2.0, 3.0])}
    response_pb = _make_query_response(name="xxx/test_doc", data=data)

    kwargs = make_retry_timeout_kwargs(retry=None, timeout=None)

    # Execute the vector query and check the response.
    firestore_api.run_query.return_value = iter([response_pb])

    vector_query = collection_group_ref.where("snooze", "==", 10).find_nearest(
        vector_field="embedding",
        query_vector=Vector([1.0, 2.0, 3.0]),
        distance_measure=distance_measure,
        limit=5,
    )

    returned = vector_query.get(transaction=_transaction(client), **kwargs)
    assert isinstance(returned, list)
    assert len(returned) == 1
    assert returned[0].to_dict() == data

    parent = client.collection("dee")
    parent_path, expected_prefix = parent._parent_info()

    expected_pb = _expected_pb(
        parent=parent,
        vector_field="embedding",
        vector=Vector([1.0, 2.0, 3.0]),
        distance_type=expected_distance,
        limit=5,
    )
    expected_pb.where = StructuredQuery.Filter(
        field_filter=StructuredQuery.FieldFilter(
            field=StructuredQuery.FieldReference(field_path="snooze"),
            op=StructuredQuery.FieldFilter.Operator.EQUAL,
            value=encode_value(10),
        )
    )
    expected_pb.from_ = [
        StructuredQuery.CollectionSelector(collection_id="dee", all_descendants=True)
    ]

    firestore_api.run_query.assert_called_once_with(
        request={
            "parent": parent_path,
            "structured_query": expected_pb,
            "transaction": _TXN_ID,
        },
        metadata=client._rpc_metadata,
        **kwargs,
    )


def test_query_stream_multiple_empty_response_in_stream():
    # Create a minimal fake GAPIC with a dummy response.
    firestore_api = mock.Mock(spec=["run_query"])
    empty_response1 = _make_query_response()
    empty_response2 = _make_query_response()
    run_query_response = iter([empty_response1, empty_response2])
    firestore_api.run_query.return_value = run_query_response

    # Attach the fake GAPIC to a real client.
    client = make_client()
    client._firestore_api_internal = firestore_api

    # Make a **real** collection reference as parent.
    parent = client.collection("dah", "dah", "dum")
    vector_query = parent.where("snooze", "==", 10).find_nearest(
        vector_field="embedding",
        query_vector=Vector([1.0, 2.0, 3.0]),
        distance_measure=DistanceMeasure.EUCLIDEAN,
        limit=5,
    )

    get_response = vector_query.stream()
    assert isinstance(get_response, types.GeneratorType)
    assert list(get_response) == []

    # Verify the mock call.
    parent_path, _ = parent._parent_info()
    firestore_api.run_query.assert_called_once_with(
        request={
            "parent": parent_path,
            "structured_query": vector_query._to_protobuf(),
            "transaction": None,
        },
        metadata=client._rpc_metadata,
    )
