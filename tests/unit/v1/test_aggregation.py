# Copyright 2023 Google LLC All rights reserved.
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

from google.cloud.firestore_v1.base_aggregation import (
    CountAggregation,
    AggregationResult,
)
from tests.unit.v1._test_helpers import (
    make_aggregation_query,
    make_aggregation_query_response,
    make_client,
    make_query,
)

_PROJECT = "PROJECT"


def test_count_aggregation_to_pb():
    from google.cloud.firestore_v1.types import query as query_pb2

    count_aggregation = CountAggregation(alias="total")

    expected_aggregation_query_pb = query_pb2.StructuredAggregationQuery.Aggregation()
    expected_aggregation_query_pb.count = (
        query_pb2.StructuredAggregationQuery.Aggregation.Count()
    )
    expected_aggregation_query_pb.alias = count_aggregation.alias
    assert count_aggregation._to_protobuf() == expected_aggregation_query_pb


def test_aggregation_query_constructor():
    client = make_client()
    parent = client.collection("dee")
    query = make_query(parent)
    aggregation_query = make_aggregation_query(query)

    assert aggregation_query._collection_ref == query._parent
    assert aggregation_query._nested_query == query
    assert len(aggregation_query._aggregations) == 0
    assert aggregation_query._client == query._parent._client


def test_aggregation_query_add_aggregation():
    client = make_client()
    parent = client.collection("dee")
    query = make_query(parent)
    aggregation_query = make_aggregation_query(query)
    aggregation_query.add_aggregation(CountAggregation(alias="all"))

    assert len(aggregation_query._aggregations) == 1
    assert aggregation_query._aggregations[0].alias == "all"
    assert isinstance(aggregation_query._aggregations[0], CountAggregation)


def test_aggregation_query_add_aggregations():
    client = make_client()
    parent = client.collection("dee")
    query = make_query(parent)
    aggregation_query = make_aggregation_query(query)

    aggregation_query.add_aggregations(
        [CountAggregation(alias="all"), CountAggregation(alias="total")]
    )

    assert len(aggregation_query._aggregations) == 2
    assert aggregation_query._aggregations[0].alias == "all"
    assert aggregation_query._aggregations[1].alias == "total"

    assert isinstance(aggregation_query._aggregations[0], CountAggregation)
    assert isinstance(aggregation_query._aggregations[1], CountAggregation)


def test_aggregation_query_count():
    client = make_client()
    parent = client.collection("dee")
    query = make_query(parent)
    aggregation_query = make_aggregation_query(query)

    aggregation_query.count(alias="all")

    assert len(aggregation_query._aggregations) == 1
    assert aggregation_query._aggregations[0].alias == "all"

    assert isinstance(aggregation_query._aggregations[0], CountAggregation)


def test_aggregation_query_count_twice():
    client = make_client()
    parent = client.collection("dee")
    query = make_query(parent)
    aggregation_query = make_aggregation_query(query)

    aggregation_query.count(alias="all").count(alias="total")

    assert len(aggregation_query._aggregations) == 2
    assert aggregation_query._aggregations[0].alias == "all"
    assert aggregation_query._aggregations[1].alias == "total"

    assert isinstance(aggregation_query._aggregations[0], CountAggregation)
    assert isinstance(aggregation_query._aggregations[1], CountAggregation)


def test_aggregation_query_to_protobuf():
    client = make_client()
    parent = client.collection("dee")
    query = make_query(parent)
    aggregation_query = make_aggregation_query(query)

    aggregation_query.count(alias="all")
    pb = aggregation_query._to_protobuf()

    assert pb.structured_query == parent._query()._to_protobuf()
    assert len(pb.aggregations) == 1
    assert pb.aggregations[0] == aggregation_query._aggregations[0]._to_protobuf()


def test_aggregation_query_prep_stream():
    client = make_client()
    parent = client.collection("dee")
    query = make_query(parent)
    aggregation_query = make_aggregation_query(query)

    aggregation_query.count(alias="all")

    request, kwargs = aggregation_query._prep_stream()

    parent_path, _ = parent._parent_info()
    expected_request = {
        "parent": parent_path,
        "structured_aggregation_query": aggregation_query._to_protobuf(),
        "transaction": None,
    }
    assert request == expected_request
    assert kwargs == {"retry": None}


def test_aggregation_query_prep_stream_with_transaction():
    client = make_client()
    transaction = client.transaction()
    txn_id = b"\x00\x00\x01-work-\xf2"
    transaction._id = txn_id

    parent = client.collection("dee")
    query = make_query(parent)
    aggregation_query = make_aggregation_query(query)

    aggregation_query.count(alias="all")

    request, kwargs = aggregation_query._prep_stream(transaction=transaction)

    parent_path, _ = parent._parent_info()
    expected_request = {
        "parent": parent_path,
        "structured_aggregation_query": aggregation_query._to_protobuf(),
        "transaction": txn_id,
    }
    assert request == expected_request
    assert kwargs == {"retry": None}


def _aggregation_query_get_helper(retry=None, timeout=None, read_time=None):
    from google.cloud.firestore_v1 import _helpers
    from google.cloud._helpers import _datetime_to_pb_timestamp

    # Create a minimal fake GAPIC.
    firestore_api = mock.Mock(spec=["run_aggregation_query"])

    # Attach the fake GAPIC to a real client.
    client = make_client()
    client._firestore_api_internal = firestore_api

    # Make a **real** collection reference as parent.
    parent = client.collection("dee")
    query = make_query(parent)
    aggregation_query = make_aggregation_query(query)
    aggregation_query.count(alias="all")

    aggregation_result = AggregationResult(alias="total", value=5, read_time=read_time)
    response_pb = make_aggregation_query_response(
        [aggregation_result], read_time=read_time
    )
    firestore_api.run_aggregation_query.return_value = iter([response_pb])
    kwargs = _helpers.make_retry_timeout_kwargs(retry, timeout)

    # Execute the query and check the response.
    returned = aggregation_query.get(**kwargs)
    assert isinstance(returned, list)
    assert len(returned) == 1

    for result in returned:
        for r in result:
            assert r.alias == aggregation_result.alias
            assert r.value == aggregation_result.value
            if read_time is not None:
                result_datetime = _datetime_to_pb_timestamp(r.read_time)
                assert result_datetime == read_time

    # Verify the mock call.
    parent_path, _ = parent._parent_info()
    firestore_api.run_aggregation_query.assert_called_once_with(
        request={
            "parent": parent_path,
            "structured_aggregation_query": aggregation_query._to_protobuf(),
            "transaction": None,
        },
        metadata=client._rpc_metadata,
        **kwargs,
    )


def test_aggregation_query_get():
    _aggregation_query_get_helper()


def test_aggregation_query_get_with_readtime():
    from google.cloud._helpers import _datetime_to_pb_timestamp

    one_hour_ago = datetime.now(tz=timezone.utc) - timedelta(hours=1)
    read_time = _datetime_to_pb_timestamp(one_hour_ago)
    _aggregation_query_get_helper(read_time=read_time)


def test_aggregation_query_get_retry_timeout():
    from google.api_core.retry import Retry

    retry = Retry(predicate=object())
    timeout = 123.0
    _aggregation_query_get_helper(retry=retry, timeout=timeout)


def test_aggregation_query_get_transaction():
    from google.cloud.firestore_v1 import _helpers

    # Create a minimal fake GAPIC.
    firestore_api = mock.Mock(spec=["run_aggregation_query"])

    # Attach the fake GAPIC to a real client.
    client = make_client()
    client._firestore_api_internal = firestore_api

    # Make a **real** collection reference as parent.
    parent = client.collection("dee")

    transaction = client.transaction()

    txn_id = b"\x00\x00\x01-work-\xf2"
    transaction._id = txn_id

    query = make_query(parent)
    aggregation_query = make_aggregation_query(query)
    aggregation_query.count(alias="all")

    aggregation_result = AggregationResult(alias="total", value=5)
    response_pb = make_aggregation_query_response(
        [aggregation_result], transaction=txn_id
    )
    firestore_api.run_aggregation_query.return_value = iter([response_pb])
    retry = None
    timeout = None
    kwargs = _helpers.make_retry_timeout_kwargs(retry, timeout)

    # Execute the query and check the response.
    returned = aggregation_query.get(transaction=transaction, **kwargs)
    assert isinstance(returned, list)
    assert len(returned) == 1

    for result in returned:
        for r in result:
            assert r.alias == aggregation_result.alias
            assert r.value == aggregation_result.value

    # Verify the mock call.
    parent_path, _ = parent._parent_info()

    firestore_api.run_aggregation_query.assert_called_once_with(
        request={
            "parent": parent_path,
            "structured_aggregation_query": aggregation_query._to_protobuf(),
            "transaction": txn_id,
        },
        metadata=client._rpc_metadata,
        **kwargs,
    )


_not_passed = object()


def _aggregation_query_stream_w_retriable_exc_helper(
    retry=_not_passed,
    timeout=None,
    transaction=None,
    expect_retry=True,
):
    from google.api_core import exceptions
    from google.api_core import gapic_v1
    from google.cloud.firestore_v1 import _helpers

    if retry is _not_passed:
        retry = gapic_v1.method.DEFAULT

    if transaction is not None:
        expect_retry = False

    # Create a minimal fake GAPIC.
    firestore_api = mock.Mock(spec=["run_aggregation_query", "_transport"])
    transport = firestore_api._transport = mock.Mock(spec=["run_aggregation_query"])
    stub = transport.run_aggregation_query = mock.create_autospec(
        gapic_v1.method._GapicCallable
    )
    stub._retry = mock.Mock(spec=["_predicate"])
    stub._predicate = lambda exc: True  # pragma: NO COVER

    # Attach the fake GAPIC to a real client.
    client = make_client()
    client._firestore_api_internal = firestore_api

    # Make a **real** collection reference as parent.
    parent = client.collection("dee")

    aggregation_result = AggregationResult(alias="total", value=5)
    response_pb = make_aggregation_query_response([aggregation_result])

    retriable_exc = exceptions.ServiceUnavailable("testing")

    def _stream_w_exception(*_args, **_kw):
        yield response_pb
        raise retriable_exc

    firestore_api.run_aggregation_query.side_effect = [_stream_w_exception(), iter([])]
    kwargs = _helpers.make_retry_timeout_kwargs(retry, timeout)

    # Execute the query and check the response.
    query = make_query(parent)
    aggregation_query = make_aggregation_query(query)

    get_response = aggregation_query.stream(transaction=transaction, **kwargs)

    assert isinstance(get_response, types.GeneratorType)
    if expect_retry:
        returned = list(get_response)
    else:
        returned = [next(get_response)]
        with pytest.raises(exceptions.ServiceUnavailable):
            next(get_response)

    assert len(returned) == 1

    for result in returned:
        for r in result:
            assert r.alias == aggregation_result.alias
            assert r.value == aggregation_result.value

    # Verify the mock call.
    parent_path, _ = parent._parent_info()
    calls = firestore_api.run_aggregation_query.call_args_list

    if expect_retry:
        assert len(calls) == 2
    else:
        assert len(calls) == 1

    if transaction is not None:
        expected_transaction_id = transaction.id
    else:
        expected_transaction_id = None

    assert calls[0] == mock.call(
        request={
            "parent": parent_path,
            "structured_aggregation_query": aggregation_query._to_protobuf(),
            "transaction": expected_transaction_id,
        },
        metadata=client._rpc_metadata,
        **kwargs,
    )

    if expect_retry:
        assert calls[1] == mock.call(
            request={
                "parent": parent_path,
                "structured_aggregation_query": aggregation_query._to_protobuf(),
                "transaction": None,
            },
            metadata=client._rpc_metadata,
            **kwargs,
        )


def test_aggregation_query_stream_w_retriable_exc_w_defaults():
    _aggregation_query_stream_w_retriable_exc_helper()


def test_aggregation_query_stream_w_retriable_exc_w_retry():
    retry = mock.Mock(spec=["_predicate"])
    retry._predicate = lambda exc: False
    _aggregation_query_stream_w_retriable_exc_helper(retry=retry, expect_retry=False)


def test_aggregation_query_stream_w_retriable_exc_w_transaction():
    from google.cloud.firestore_v1 import transaction

    txn = transaction.Transaction(client=mock.Mock(spec=[]))
    txn._id = b"DEADBEEF"
    _aggregation_query_stream_w_retriable_exc_helper(transaction=txn)


def test_aggregation_from_query():
    from google.cloud.firestore_v1 import _helpers

    # Create a minimal fake GAPIC.
    firestore_api = mock.Mock(spec=["run_aggregation_query"])

    # Attach the fake GAPIC to a real client.
    client = make_client()
    client._firestore_api_internal = firestore_api

    # Make a **real** collection reference as parent.
    parent = client.collection("dee")
    query = make_query(parent)

    transaction = client.transaction()

    txn_id = b"\x00\x00\x01-work-\xf2"
    transaction._id = txn_id

    aggregation_result = AggregationResult(alias="total", value=5)
    response_pb = make_aggregation_query_response(
        [aggregation_result], transaction=txn_id
    )
    firestore_api.run_aggregation_query.return_value = iter([response_pb])
    retry = None
    timeout = None
    kwargs = _helpers.make_retry_timeout_kwargs(retry, timeout)

    # Execute the query and check the response.
    aggregation_query = query.count(alias="total")
    returned = aggregation_query.get(transaction=transaction, **kwargs)
    assert isinstance(returned, list)
    assert len(returned) == 1

    for result in returned:
        for r in result:
            assert r.alias == aggregation_result.alias
            assert r.value == aggregation_result.value

    # Verify the mock call.
    parent_path, _ = parent._parent_info()

    firestore_api.run_aggregation_query.assert_called_once_with(
        request={
            "parent": parent_path,
            "structured_aggregation_query": aggregation_query._to_protobuf(),
            "transaction": txn_id,
        },
        metadata=client._rpc_metadata,
        **kwargs,
    )
