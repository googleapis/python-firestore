# Copyright 2017 Google LLC
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

import asyncio
import datetime
import itertools
import math
import pytest
import pytest_asyncio
import operator
from typing import Callable, Dict, List, Optional

from google.oauth2 import service_account

from google.api_core import retry as retries
from google.api_core import exceptions as core_exceptions

from google.api_core.exceptions import AlreadyExists
from google.api_core.exceptions import FailedPrecondition
from google.api_core.exceptions import InvalidArgument
from google.api_core.exceptions import NotFound
from google.cloud._helpers import _datetime_to_pb_timestamp
from google.cloud._helpers import UTC
from google.cloud import firestore_v1 as firestore

from tests.system.test__helpers import (
    FIRESTORE_CREDS,
    FIRESTORE_PROJECT,
    RANDOM_ID_REGEX,
    MISSING_DOCUMENT,
    UNIQUE_RESOURCE_ID,
    EMULATOR_CREDS,
    FIRESTORE_EMULATOR,
)


RETRIES = retries.Retry(
    initial=0.1,
    maximum=60.0,
    multiplier=1.3,
    predicate=retries.if_exception_type(
        core_exceptions.DeadlineExceeded,
        core_exceptions.InternalServerError,
        core_exceptions.ServiceUnavailable,
    ),
    deadline=60.0,
)


pytestmark = pytest.mark.asyncio


def _get_credentials_and_project():
    if FIRESTORE_EMULATOR:
        credentials = EMULATOR_CREDS
        project = FIRESTORE_PROJECT
    else:
        credentials = service_account.Credentials.from_service_account_file(
            FIRESTORE_CREDS
        )
        project = FIRESTORE_PROJECT or credentials.project_id
    return credentials, project


@pytest.fixture(scope="module")
def client():
    credentials, project = _get_credentials_and_project()
    yield firestore.AsyncClient(project=project, credentials=credentials)


@pytest_asyncio.fixture
async def cleanup():
    operations = []
    yield operations.append

    for operation in operations:
        await operation()


@pytest.fixture(scope="module")
def event_loop():
    """Change event_loop fixture to module level."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


async def test_collections(client):
    collections = [x async for x in client.collections(retry=RETRIES)]
    assert isinstance(collections, list)


async def test_collections_w_import():
    from google.cloud import firestore

    credentials, project = _get_credentials_and_project()
    client = firestore.AsyncClient(project=project, credentials=credentials)
    collections = [x async for x in client.collections(retry=RETRIES)]

    assert isinstance(collections, list)


async def test_create_document(client, cleanup):
    now = datetime.datetime.utcnow().replace(tzinfo=UTC)
    collection_id = "doc-create" + UNIQUE_RESOURCE_ID
    document_id = "doc" + UNIQUE_RESOURCE_ID
    document = client.document(collection_id, document_id)
    # Add to clean-up before API request (in case ``create()`` fails).
    cleanup(document.delete)

    data = {
        "now": firestore.SERVER_TIMESTAMP,
        "eenta-ger": 11,
        "bites": b"\xe2\x98\x83 \xe2\x9b\xb5",
        "also": {"nestednow": firestore.SERVER_TIMESTAMP, "quarter": 0.25},
    }
    write_result = await document.create(data)

    updated = write_result.update_time
    delta = updated - now
    # Allow a bit of clock skew, but make sure timestamps are close.
    assert -300.0 < delta.total_seconds() < 300.0

    with pytest.raises(AlreadyExists):
        await document.create(data)

    # Verify the server times.
    snapshot = await document.get()
    stored_data = snapshot.to_dict()
    server_now = stored_data["now"]

    delta = updated - server_now
    # NOTE: We could check the ``transform_results`` from the write result
    #       for the document transform, but this value gets dropped. Instead
    #       we make sure the timestamps are close.
    # TODO(microgen): this was 0.0 - 5.0 before. After microgen, This started
    # getting very small negative times.
    assert -0.2 <= delta.total_seconds() < 5.0
    expected_data = {
        "now": server_now,
        "eenta-ger": data["eenta-ger"],
        "bites": data["bites"],
        "also": {"nestednow": server_now, "quarter": data["also"]["quarter"]},
    }
    assert stored_data == expected_data


async def test_create_document_w_subcollection(client, cleanup):
    collection_id = "doc-create-sub" + UNIQUE_RESOURCE_ID
    document_id = "doc" + UNIQUE_RESOURCE_ID
    document = client.document(collection_id, document_id)
    # Add to clean-up before API request (in case ``create()`` fails).
    cleanup(document.delete)

    data = {"now": firestore.SERVER_TIMESTAMP}
    await document.create(data)

    child_ids = ["child1", "child2"]

    for child_id in child_ids:
        subcollection = document.collection(child_id)
        _, subdoc = await subcollection.add({"foo": "bar"})
        cleanup(subdoc.delete)

    children = document.collections()
    assert sorted([child.id async for child in children]) == sorted(child_ids)


def assert_timestamp_less(timestamp_pb1, timestamp_pb2):
    assert timestamp_pb1 < timestamp_pb2


async def test_no_document(client):
    document_id = "no_document" + UNIQUE_RESOURCE_ID
    document = client.document("abcde", document_id)
    snapshot = await document.get()
    assert snapshot.to_dict() is None


async def test_document_set(client, cleanup):
    document_id = "for-set" + UNIQUE_RESOURCE_ID
    document = client.document("i-did-it", document_id)
    # Add to clean-up before API request (in case ``set()`` fails).
    cleanup(document.delete)

    # 0. Make sure the document doesn't exist yet
    snapshot = await document.get()
    assert snapshot.to_dict() is None

    # 1. Use ``create()`` to create the document.
    data1 = {"foo": 88}
    write_result1 = await document.create(data1)
    snapshot1 = await document.get()
    assert snapshot1.to_dict() == data1
    # Make sure the update is what created the document.
    assert snapshot1.create_time == snapshot1.update_time
    assert snapshot1.update_time == write_result1.update_time

    # 2. Call ``set()`` again to overwrite.
    data2 = {"bar": None}
    write_result2 = await document.set(data2)
    snapshot2 = await document.get()
    assert snapshot2.to_dict() == data2
    # Make sure the create time hasn't changed.
    assert snapshot2.create_time == snapshot1.create_time
    assert snapshot2.update_time == write_result2.update_time


async def test_document_integer_field(client, cleanup):
    document_id = "for-set" + UNIQUE_RESOURCE_ID
    document = client.document("i-did-it", document_id)
    # Add to clean-up before API request (in case ``set()`` fails).
    cleanup(document.delete)

    data1 = {"1a": {"2b": "3c", "ab": "5e"}, "6f": {"7g": "8h", "cd": "0j"}}
    await document.create(data1)

    data2 = {"1a.ab": "4d", "6f.7g": "9h"}
    await document.update(data2)
    snapshot = await document.get()
    expected = {"1a": {"2b": "3c", "ab": "4d"}, "6f": {"7g": "9h", "cd": "0j"}}
    assert snapshot.to_dict() == expected


async def test_document_set_merge(client, cleanup):
    document_id = "for-set" + UNIQUE_RESOURCE_ID
    document = client.document("i-did-it", document_id)
    # Add to clean-up before API request (in case ``set()`` fails).
    cleanup(document.delete)

    # 0. Make sure the document doesn't exist yet
    snapshot = await document.get()
    assert not snapshot.exists

    # 1. Use ``create()`` to create the document.
    data1 = {"name": "Sam", "address": {"city": "SF", "state": "CA"}}
    write_result1 = await document.create(data1)
    snapshot1 = await document.get()
    assert snapshot1.to_dict() == data1
    # Make sure the update is what created the document.
    assert snapshot1.create_time == snapshot1.update_time
    assert snapshot1.update_time == write_result1.update_time

    # 2. Call ``set()`` to merge
    data2 = {"address": {"city": "LA"}}
    write_result2 = await document.set(data2, merge=True)
    snapshot2 = await document.get()
    assert snapshot2.to_dict() == {
        "name": "Sam",
        "address": {"city": "LA", "state": "CA"},
    }
    # Make sure the create time hasn't changed.
    assert snapshot2.create_time == snapshot1.create_time
    assert snapshot2.update_time == write_result2.update_time


async def test_document_set_w_int_field(client, cleanup):
    document_id = "set-int-key" + UNIQUE_RESOURCE_ID
    document = client.document("i-did-it", document_id)
    # Add to clean-up before API request (in case ``set()`` fails).
    cleanup(document.delete)

    # 0. Make sure the document doesn't exist yet
    snapshot = await document.get()
    assert not snapshot.exists

    # 1. Use ``create()`` to create the document.
    before = {"testing": "1"}
    await document.create(before)

    # 2. Replace using ``set()``.
    data = {"14": {"status": "active"}}
    await document.set(data)

    # 3. Verify replaced data.
    snapshot1 = await document.get()
    assert snapshot1.to_dict() == data


async def test_document_update_w_int_field(client, cleanup):
    # Attempt to reproduce #5489.
    document_id = "update-int-key" + UNIQUE_RESOURCE_ID
    document = client.document("i-did-it", document_id)
    # Add to clean-up before API request (in case ``set()`` fails).
    cleanup(document.delete)

    # 0. Make sure the document doesn't exist yet
    snapshot = await document.get()
    assert not snapshot.exists

    # 1. Use ``create()`` to create the document.
    before = {"testing": "1"}
    await document.create(before)

    # 2. Add values using ``update()``.
    data = {"14": {"status": "active"}}
    await document.update(data)

    # 3. Verify updated data.
    expected = before.copy()
    expected.update(data)
    snapshot1 = await document.get()
    assert snapshot1.to_dict() == expected


@pytest.mark.skipif(FIRESTORE_EMULATOR, reason="Internal Issue b/137867104")
async def test_update_document(client, cleanup):
    document_id = "for-update" + UNIQUE_RESOURCE_ID
    document = client.document("made", document_id)
    # Add to clean-up before API request (in case ``create()`` fails).
    cleanup(document.delete)

    # 0. Try to update before the document exists.
    with pytest.raises(NotFound) as exc_info:
        await document.update({"not": "there"})
    assert exc_info.value.message.startswith(MISSING_DOCUMENT)
    assert document_id in exc_info.value.message

    # 1. Try to update before the document exists (now with an option).
    with pytest.raises(NotFound) as exc_info:
        await document.update({"still": "not-there"})
    assert exc_info.value.message.startswith(MISSING_DOCUMENT)
    assert document_id in exc_info.value.message

    # 2. Update and create the document (with an option).
    data = {"foo": {"bar": "baz"}, "scoop": {"barn": 981}, "other": True}
    write_result2 = await document.create(data)

    # 3. Send an update without a field path (no option).
    field_updates3 = {"foo": {"quux": 800}}
    write_result3 = await document.update(field_updates3)
    assert_timestamp_less(write_result2.update_time, write_result3.update_time)
    snapshot3 = await document.get()
    expected3 = {
        "foo": field_updates3["foo"],
        "scoop": data["scoop"],
        "other": data["other"],
    }
    assert snapshot3.to_dict() == expected3

    # 4. Send an update **with** a field path and a delete and a valid
    #    "last timestamp" option.
    field_updates4 = {"scoop.silo": None, "other": firestore.DELETE_FIELD}
    option4 = client.write_option(last_update_time=snapshot3.update_time)
    write_result4 = await document.update(field_updates4, option=option4)
    assert_timestamp_less(write_result3.update_time, write_result4.update_time)
    snapshot4 = await document.get()
    expected4 = {
        "foo": field_updates3["foo"],
        "scoop": {"barn": data["scoop"]["barn"], "silo": field_updates4["scoop.silo"]},
    }
    assert snapshot4.to_dict() == expected4

    # 5. Call ``update()`` with invalid (in the past) "last timestamp" option.
    assert_timestamp_less(option4._last_update_time, snapshot4.update_time)
    with pytest.raises(FailedPrecondition) as exc_info:
        await document.update({"bad": "time-past"}, option=option4)

    # 6. Call ``update()`` with invalid (in future) "last timestamp" option.
    # TODO(microgen): start using custom datetime with nanos in protoplus?
    timestamp_pb = _datetime_to_pb_timestamp(snapshot4.update_time)
    timestamp_pb.seconds += 3600

    option6 = client.write_option(last_update_time=timestamp_pb)
    # TODO(microgen):invalid argument thrown after microgen.
    # with pytest.raises(FailedPrecondition) as exc_info:
    with pytest.raises(InvalidArgument) as exc_info:
        await document.update({"bad": "time-future"}, option=option6)


def check_snapshot(snapshot, document, data, write_result):
    assert snapshot.reference is document
    assert snapshot.to_dict() == data
    assert snapshot.exists
    assert snapshot.create_time == write_result.update_time
    assert snapshot.update_time == write_result.update_time


async def test_document_get(client, cleanup):
    now = datetime.datetime.utcnow().replace(tzinfo=UTC)
    document_id = "for-get" + UNIQUE_RESOURCE_ID
    document = client.document("created", document_id)
    # Add to clean-up before API request (in case ``create()`` fails).
    cleanup(document.delete)

    # First make sure it doesn't exist.
    assert not (await document.get()).exists

    ref_doc = client.document("top", "middle1", "middle2", "bottom")
    data = {
        "turtle": "power",
        "cheese": 19.5,
        "fire": 199099299,
        "referee": ref_doc,
        "gio": firestore.GeoPoint(45.5, 90.0),
        "deep": ["some", b"\xde\xad\xbe\xef"],
        "map": {"ice": True, "water": None, "vapor": {"deeper": now}},
    }
    write_result = await document.create(data)
    snapshot = await document.get()
    check_snapshot(snapshot, document, data, write_result)


async def test_document_delete(client, cleanup):
    document_id = "deleted" + UNIQUE_RESOURCE_ID
    document = client.document("here-to-be", document_id)
    # Add to clean-up before API request (in case ``create()`` fails).
    cleanup(document.delete)
    await document.create({"not": "much"})

    # 1. Call ``delete()`` with invalid (in the past) "last timestamp" option.
    snapshot1 = await document.get()
    timestamp_pb = _datetime_to_pb_timestamp(snapshot1.update_time)
    timestamp_pb.seconds += 3600

    option1 = client.write_option(last_update_time=timestamp_pb)
    # TODO(microgen):invalid argument thrown after microgen.
    # with pytest.raises(FailedPrecondition):
    with pytest.raises(InvalidArgument):
        await document.delete(option=option1)

    # 2. Call ``delete()`` with invalid (in future) "last timestamp" option.
    timestamp_pb = _datetime_to_pb_timestamp(snapshot1.update_time)
    timestamp_pb.seconds += 3600

    option2 = client.write_option(last_update_time=timestamp_pb)
    # TODO(microgen):invalid argument thrown after microgen.
    # with pytest.raises(FailedPrecondition):
    with pytest.raises(InvalidArgument):
        await document.delete(option=option2)

    # 3. Actually ``delete()`` the document.
    delete_time3 = await document.delete()

    # 4. ``delete()`` again, even though we know the document is gone.
    delete_time4 = await document.delete()
    assert_timestamp_less(delete_time3, delete_time4)


async def test_collection_add(client, cleanup):
    # TODO(microgen): list_documents is returning a generator, not a list.
    # Consider if this is desired. Also, Document isn't hashable.
    collection_id = "coll-add" + UNIQUE_RESOURCE_ID
    collection1 = client.collection(collection_id)
    collection2 = client.collection(collection_id, "doc", "child")
    collection3 = client.collection(collection_id, "table", "child")
    explicit_doc_id = "hula" + UNIQUE_RESOURCE_ID

    assert set([i async for i in collection1.list_documents()]) == set()
    assert set([i async for i in collection2.list_documents()]) == set()
    assert set([i async for i in collection3.list_documents()]) == set()

    # Auto-ID at top-level.
    data1 = {"foo": "bar"}
    update_time1, document_ref1 = await collection1.add(data1)
    cleanup(document_ref1.delete)
    assert set([i async for i in collection1.list_documents()]) == {document_ref1}
    assert set([i async for i in collection2.list_documents()]) == set()
    assert set([i async for i in collection3.list_documents()]) == set()
    snapshot1 = await document_ref1.get()
    assert snapshot1.to_dict() == data1
    assert snapshot1.update_time == update_time1
    assert RANDOM_ID_REGEX.match(document_ref1.id)

    # Explicit ID at top-level.
    data2 = {"baz": 999}
    update_time2, document_ref2 = await collection1.add(
        data2, document_id=explicit_doc_id
    )
    cleanup(document_ref2.delete)
    assert set([i async for i in collection1.list_documents()]) == {
        document_ref1,
        document_ref2,
    }
    assert set([i async for i in collection2.list_documents()]) == set()
    assert set([i async for i in collection3.list_documents()]) == set()
    snapshot2 = await document_ref2.get()
    assert snapshot2.to_dict() == data2
    assert snapshot2.create_time == update_time2
    assert snapshot2.update_time == update_time2
    assert document_ref2.id == explicit_doc_id

    nested_ref = collection1.document("doc")

    # Auto-ID for nested collection.
    data3 = {"quux": b"\x00\x01\x02\x03"}
    update_time3, document_ref3 = await collection2.add(data3)
    cleanup(document_ref3.delete)
    assert set([i async for i in collection1.list_documents()]) == {
        document_ref1,
        document_ref2,
        nested_ref,
    }
    assert set([i async for i in collection2.list_documents()]) == {document_ref3}
    assert set([i async for i in collection3.list_documents()]) == set()
    snapshot3 = await document_ref3.get()
    assert snapshot3.to_dict() == data3
    assert snapshot3.update_time == update_time3
    assert RANDOM_ID_REGEX.match(document_ref3.id)

    # Explicit for nested collection.
    data4 = {"kazaam": None, "bad": False}
    update_time4, document_ref4 = await collection2.add(
        data4, document_id=explicit_doc_id
    )
    cleanup(document_ref4.delete)
    assert set([i async for i in collection1.list_documents()]) == {
        document_ref1,
        document_ref2,
        nested_ref,
    }
    assert set([i async for i in collection2.list_documents()]) == {
        document_ref3,
        document_ref4,
    }
    assert set([i async for i in collection3.list_documents()]) == set()
    snapshot4 = await document_ref4.get()
    assert snapshot4.to_dict() == data4
    assert snapshot4.create_time == update_time4
    assert snapshot4.update_time == update_time4
    assert document_ref4.id == explicit_doc_id

    # Exercise "missing" document (no doc, but subcollection).
    data5 = {"bam": 123, "folyk": False}
    update_time5, document_ref5 = await collection3.add(data5)
    cleanup(document_ref5.delete)
    missing_ref = collection1.document("table")
    assert set([i async for i in collection1.list_documents()]) == {
        document_ref1,
        document_ref2,
        nested_ref,
        missing_ref,
    }
    assert set([i async for i in collection2.list_documents()]) == {
        document_ref3,
        document_ref4,
    }
    assert set([i async for i in collection3.list_documents()]) == {document_ref5}


@pytest_asyncio.fixture
async def query_docs(client):
    collection_id = "qs" + UNIQUE_RESOURCE_ID
    sub_collection = "child" + UNIQUE_RESOURCE_ID
    collection = client.collection(collection_id, "doc", sub_collection)

    cleanup = []
    stored = {}
    num_vals = 5
    allowed_vals = range(num_vals)
    for a_val in allowed_vals:
        for b_val in allowed_vals:
            document_data = {
                "a": a_val,
                "b": b_val,
                "c": [a_val, num_vals * 100],
                "stats": {"sum": a_val + b_val, "product": a_val * b_val},
            }
            _, doc_ref = await collection.add(document_data)
            # Add to clean-up.
            cleanup.append(doc_ref.delete)
            stored[doc_ref.id] = document_data

    yield collection, stored, allowed_vals

    for operation in cleanup:
        await operation()


async def test_query_stream_w_simple_field_eq_op(query_docs):
    collection, stored, allowed_vals = query_docs
    query = collection.where("a", "==", 1)
    values = {snapshot.id: snapshot.to_dict() async for snapshot in query.stream()}
    assert len(values) == len(allowed_vals)
    for key, value in values.items():
        assert stored[key] == value
        assert value["a"] == 1


async def test_query_stream_w_simple_field_array_contains_op(query_docs):
    collection, stored, allowed_vals = query_docs
    query = collection.where("c", "array_contains", 1)
    values = {snapshot.id: snapshot.to_dict() async for snapshot in query.stream()}
    assert len(values) == len(allowed_vals)
    for key, value in values.items():
        assert stored[key] == value
        assert value["a"] == 1


async def test_query_stream_w_simple_field_in_op(query_docs):
    collection, stored, allowed_vals = query_docs
    num_vals = len(allowed_vals)
    query = collection.where("a", "in", [1, num_vals + 100])
    values = {snapshot.id: snapshot.to_dict() async for snapshot in query.stream()}
    assert len(values) == len(allowed_vals)
    for key, value in values.items():
        assert stored[key] == value
        assert value["a"] == 1


async def test_query_stream_w_simple_field_array_contains_any_op(query_docs):
    collection, stored, allowed_vals = query_docs
    num_vals = len(allowed_vals)
    query = collection.where("c", "array_contains_any", [1, num_vals * 200])
    values = {snapshot.id: snapshot.to_dict() async for snapshot in query.stream()}
    assert len(values) == len(allowed_vals)
    for key, value in values.items():
        assert stored[key] == value
        assert value["a"] == 1


async def test_query_stream_w_order_by(query_docs):
    collection, stored, allowed_vals = query_docs
    query = collection.order_by("b", direction=firestore.Query.DESCENDING)
    values = [(snapshot.id, snapshot.to_dict()) async for snapshot in query.stream()]
    assert len(values) == len(stored)
    b_vals = []
    for key, value in values:
        assert stored[key] == value
        b_vals.append(value["b"])
    # Make sure the ``b``-values are in DESCENDING order.
    assert sorted(b_vals, reverse=True) == b_vals


async def test_query_stream_w_field_path(query_docs):
    collection, stored, allowed_vals = query_docs
    query = collection.where("stats.sum", ">", 4)
    values = {snapshot.id: snapshot.to_dict() async for snapshot in query.stream()}
    assert len(values) == 10
    ab_pairs2 = set()
    for key, value in values.items():
        assert stored[key] == value
        ab_pairs2.add((value["a"], value["b"]))

    expected_ab_pairs = set(
        [
            (a_val, b_val)
            for a_val in allowed_vals
            for b_val in allowed_vals
            if a_val + b_val > 4
        ]
    )
    assert expected_ab_pairs == ab_pairs2


async def test_query_stream_w_start_end_cursor(query_docs):
    collection, stored, allowed_vals = query_docs
    num_vals = len(allowed_vals)
    query = (
        collection.order_by("a")
        .start_at({"a": num_vals - 2})
        .end_before({"a": num_vals - 1})
    )
    values = [(snapshot.id, snapshot.to_dict()) async for snapshot in query.stream()]
    assert len(values) == num_vals
    for key, value in values:
        assert stored[key] == value
        assert value["a"] == num_vals - 2


async def test_query_stream_wo_results(query_docs):
    collection, stored, allowed_vals = query_docs
    num_vals = len(allowed_vals)
    query = collection.where("b", "==", num_vals + 100)
    values = [i async for i in query.stream()]
    assert len(values) == 0


async def test_query_stream_w_projection(query_docs):
    collection, stored, allowed_vals = query_docs
    num_vals = len(allowed_vals)
    query = collection.where("b", "<=", 1).select(["a", "stats.product"])
    values = {snapshot.id: snapshot.to_dict() async for snapshot in query.stream()}
    assert len(values) == num_vals * 2  # a ANY, b in (0, 1)
    for key, value in values.items():
        expected = {
            "a": stored[key]["a"],
            "stats": {"product": stored[key]["stats"]["product"]},
        }
        assert expected == value


async def test_query_stream_w_multiple_filters(query_docs):
    collection, stored, allowed_vals = query_docs
    query = collection.where("stats.product", ">", 5).where("stats.product", "<", 10)
    values = {snapshot.id: snapshot.to_dict() async for snapshot in query.stream()}
    matching_pairs = [
        (a_val, b_val)
        for a_val in allowed_vals
        for b_val in allowed_vals
        if 5 < a_val * b_val < 10
    ]
    assert len(values) == len(matching_pairs)
    for key, value in values.items():
        assert stored[key] == value
        pair = (value["a"], value["b"])
        assert pair in matching_pairs


async def test_query_stream_w_offset(query_docs):
    collection, stored, allowed_vals = query_docs
    num_vals = len(allowed_vals)
    offset = 3
    query = collection.where("b", "==", 2).offset(offset)
    values = {snapshot.id: snapshot.to_dict() async for snapshot in query.stream()}
    # NOTE: We don't check the ``a``-values, since that would require
    #       an ``order_by('a')``, which combined with the ``b == 2``
    #       filter would necessitate an index.
    assert len(values) == num_vals - offset
    for key, value in values.items():
        assert stored[key] == value
        assert value["b"] == 2


async def test_query_with_order_dot_key(client, cleanup):
    db = client
    collection_id = "collek" + UNIQUE_RESOURCE_ID
    collection = db.collection(collection_id)
    for index in range(100, -1, -1):
        doc = collection.document("test_{:09d}".format(index))
        data = {"count": 10 * index, "wordcount": {"page1": index * 10 + 100}}
        await doc.set(data)
        cleanup(doc.delete)
    query = collection.order_by("wordcount.page1").limit(3)
    data = [doc.to_dict()["wordcount"]["page1"] async for doc in query.stream()]
    assert [100, 110, 120] == data
    async for snapshot in collection.order_by("wordcount.page1").limit(3).stream():
        last_value = snapshot.get("wordcount.page1")
    cursor_with_nested_keys = {"wordcount": {"page1": last_value}}
    found = [
        i
        async for i in collection.order_by("wordcount.page1")
        .start_after(cursor_with_nested_keys)
        .limit(3)
        .stream()
    ]
    found_data = [
        {"count": 30, "wordcount": {"page1": 130}},
        {"count": 40, "wordcount": {"page1": 140}},
        {"count": 50, "wordcount": {"page1": 150}},
    ]
    assert found_data == [snap.to_dict() for snap in found]
    cursor_with_dotted_paths = {"wordcount.page1": last_value}
    cursor_with_key_data = [
        i
        async for i in collection.order_by("wordcount.page1")
        .start_after(cursor_with_dotted_paths)
        .limit(3)
        .stream()
    ]
    assert found_data == [snap.to_dict() for snap in cursor_with_key_data]


async def test_query_unary(client, cleanup):
    collection_name = "unary" + UNIQUE_RESOURCE_ID
    collection = client.collection(collection_name)
    field_name = "foo"

    _, document0 = await collection.add({field_name: None})
    # Add to clean-up.
    cleanup(document0.delete)

    nan_val = float("nan")
    _, document1 = await collection.add({field_name: nan_val})
    # Add to clean-up.
    cleanup(document1.delete)

    # 0. Query for null.
    query0 = collection.where(field_name, "==", None)
    values0 = [i async for i in query0.stream()]
    assert len(values0) == 1
    snapshot0 = values0[0]
    assert snapshot0.reference._path == document0._path
    assert snapshot0.to_dict() == {field_name: None}

    # 1. Query for a NAN.
    query1 = collection.where(field_name, "==", nan_val)
    values1 = [i async for i in query1.stream()]
    assert len(values1) == 1
    snapshot1 = values1[0]
    assert snapshot1.reference._path == document1._path
    data1 = snapshot1.to_dict()
    assert len(data1) == 1
    assert math.isnan(data1[field_name])


async def test_collection_group_queries(client, cleanup):
    collection_group = "b" + UNIQUE_RESOURCE_ID

    doc_paths = [
        "abc/123/" + collection_group + "/cg-doc1",
        "abc/123/" + collection_group + "/cg-doc2",
        collection_group + "/cg-doc3",
        collection_group + "/cg-doc4",
        "def/456/" + collection_group + "/cg-doc5",
        collection_group + "/virtual-doc/nested-coll/not-cg-doc",
        "x" + collection_group + "/not-cg-doc",
        collection_group + "x/not-cg-doc",
        "abc/123/" + collection_group + "x/not-cg-doc",
        "abc/123/x" + collection_group + "/not-cg-doc",
        "abc/" + collection_group,
    ]

    batch = client.batch()
    for doc_path in doc_paths:
        doc_ref = client.document(doc_path)
        batch.set(doc_ref, {"x": 1})
        cleanup(doc_ref.delete)

    await batch.commit()

    query = client.collection_group(collection_group)
    snapshots = [i async for i in query.stream()]
    found = [snapshot.id for snapshot in snapshots]
    expected = ["cg-doc1", "cg-doc2", "cg-doc3", "cg-doc4", "cg-doc5"]
    assert found == expected


async def test_collection_group_queries_startat_endat(client, cleanup):
    collection_group = "b" + UNIQUE_RESOURCE_ID

    doc_paths = [
        "a/a/" + collection_group + "/cg-doc1",
        "a/b/a/b/" + collection_group + "/cg-doc2",
        "a/b/" + collection_group + "/cg-doc3",
        "a/b/c/d/" + collection_group + "/cg-doc4",
        "a/c/" + collection_group + "/cg-doc5",
        collection_group + "/cg-doc6",
        "a/b/nope/nope",
    ]

    batch = client.batch()
    for doc_path in doc_paths:
        doc_ref = client.document(doc_path)
        batch.set(doc_ref, {"x": doc_path})
        cleanup(doc_ref.delete)

    await batch.commit()

    query = (
        client.collection_group(collection_group)
        .order_by("__name__")
        .start_at([client.document("a/b")])
        .end_at([client.document("a/b0")])
    )
    snapshots = [i async for i in query.stream()]
    found = set(snapshot.id for snapshot in snapshots)
    assert found == set(["cg-doc2", "cg-doc3", "cg-doc4"])

    query = (
        client.collection_group(collection_group)
        .order_by("__name__")
        .start_after([client.document("a/b")])
        .end_before([client.document("a/b/" + collection_group + "/cg-doc3")])
    )
    snapshots = [i async for i in query.stream()]
    found = set(snapshot.id for snapshot in snapshots)
    assert found == set(["cg-doc2"])


async def test_collection_group_queries_filters(client, cleanup):
    collection_group = "b" + UNIQUE_RESOURCE_ID

    doc_paths = [
        "a/a/" + collection_group + "/cg-doc1",
        "a/b/a/b/" + collection_group + "/cg-doc2",
        "a/b/" + collection_group + "/cg-doc3",
        "a/b/c/d/" + collection_group + "/cg-doc4",
        "a/c/" + collection_group + "/cg-doc5",
        collection_group + "/cg-doc6",
        "a/b/nope/nope",
    ]

    batch = client.batch()

    for index, doc_path in enumerate(doc_paths):
        doc_ref = client.document(doc_path)
        batch.set(doc_ref, {"x": index})
        cleanup(doc_ref.delete)

    await batch.commit()

    query = (
        client.collection_group(collection_group)
        .where(
            firestore.field_path.FieldPath.document_id(), ">=", client.document("a/b")
        )
        .where(
            firestore.field_path.FieldPath.document_id(), "<=", client.document("a/b0")
        )
    )
    snapshots = [i async for i in query.stream()]
    found = set(snapshot.id for snapshot in snapshots)
    assert found == set(["cg-doc2", "cg-doc3", "cg-doc4"])

    query = (
        client.collection_group(collection_group)
        .where(
            firestore.field_path.FieldPath.document_id(), ">", client.document("a/b")
        )
        .where(
            firestore.field_path.FieldPath.document_id(),
            "<",
            client.document("a/b/{}/cg-doc3".format(collection_group)),
        )
    )
    snapshots = [i async for i in query.stream()]
    found = set(snapshot.id for snapshot in snapshots)
    assert found == set(["cg-doc2"])


@pytest.mark.skipif(
    FIRESTORE_EMULATOR, reason="PartitionQuery not implemented in emulator"
)
async def test_partition_query_no_partitions(client, cleanup):
    collection_group = "b" + UNIQUE_RESOURCE_ID

    # less than minimum partition size
    doc_paths = [
        "abc/123/" + collection_group + "/cg-doc1",
        "abc/123/" + collection_group + "/cg-doc2",
        collection_group + "/cg-doc3",
        collection_group + "/cg-doc4",
        "def/456/" + collection_group + "/cg-doc5",
    ]

    batch = client.batch()
    cleanup_batch = client.batch()
    cleanup(cleanup_batch.commit)
    for doc_path in doc_paths:
        doc_ref = client.document(doc_path)
        batch.set(doc_ref, {"x": 1})
        cleanup_batch.delete(doc_ref)

    await batch.commit()

    query = client.collection_group(collection_group)
    partitions = [i async for i in query.get_partitions(3)]
    streams = [partition.query().stream() for partition in partitions]
    found = [snapshot.id async for snapshot in _chain(*streams)]
    expected = ["cg-doc1", "cg-doc2", "cg-doc3", "cg-doc4", "cg-doc5"]
    assert found == expected


@pytest.mark.skipif(
    FIRESTORE_EMULATOR, reason="PartitionQuery not implemented in emulator"
)
async def test_partition_query(client, cleanup):
    collection_group = "b" + UNIQUE_RESOURCE_ID
    n_docs = 128 * 2 + 127  # Minimum partition size is 128
    parents = itertools.cycle(("", "abc/123/", "def/456/", "ghi/789/"))
    batch = client.batch()
    cleanup_batch = client.batch()
    cleanup(cleanup_batch.commit)
    expected = []
    for i, parent in zip(range(n_docs), parents):
        doc_path = parent + collection_group + f"/cg-doc{i:03d}"
        doc_ref = client.document(doc_path)
        batch.set(doc_ref, {"x": i})
        cleanup_batch.delete(doc_ref)
        expected.append(doc_path)

    await batch.commit()

    query = client.collection_group(collection_group)
    partitions = [i async for i in query.get_partitions(3)]
    streams = [partition.query().stream() for partition in partitions]
    found = [snapshot.reference.path async for snapshot in _chain(*streams)]
    expected.sort()
    assert found == expected


@pytest.mark.skipif(FIRESTORE_EMULATOR, reason="Internal Issue b/137865992")
async def test_get_all(client, cleanup):
    collection_name = "get-all" + UNIQUE_RESOURCE_ID

    document1 = client.document(collection_name, "a")
    document2 = client.document(collection_name, "b")
    document3 = client.document(collection_name, "c")
    # Add to clean-up before API requests (in case ``create()`` fails).
    cleanup(document1.delete)
    cleanup(document3.delete)

    data1 = {"a": {"b": 2, "c": 3}, "d": 4, "e": 0}
    write_result1 = await document1.create(data1)
    data3 = {"a": {"b": 5, "c": 6}, "d": 7, "e": 100}
    write_result3 = await document3.create(data3)

    # 0. Get 3 unique documents, one of which is missing.
    snapshots = [i async for i in client.get_all([document1, document2, document3])]

    assert snapshots[0].exists
    assert snapshots[1].exists
    assert not snapshots[2].exists

    snapshots = [snapshot for snapshot in snapshots if snapshot.exists]
    id_attr = operator.attrgetter("id")
    snapshots.sort(key=id_attr)

    snapshot1, snapshot3 = snapshots
    check_snapshot(snapshot1, document1, data1, write_result1)
    check_snapshot(snapshot3, document3, data3, write_result3)

    # 1. Get 2 colliding documents.
    document1_also = client.document(collection_name, "a")
    snapshots = [i async for i in client.get_all([document1, document1_also])]

    assert len(snapshots) == 1
    assert document1 is not document1_also
    check_snapshot(snapshots[0], document1_also, data1, write_result1)

    # 2. Use ``field_paths`` / projection in ``get_all()``.
    snapshots = [
        i
        async for i in client.get_all([document1, document3], field_paths=["a.b", "d"])
    ]

    assert len(snapshots) == 2
    snapshots.sort(key=id_attr)

    snapshot1, snapshot3 = snapshots
    restricted1 = {"a": {"b": data1["a"]["b"]}, "d": data1["d"]}
    check_snapshot(snapshot1, document1, restricted1, write_result1)
    restricted3 = {"a": {"b": data3["a"]["b"]}, "d": data3["d"]}
    check_snapshot(snapshot3, document3, restricted3, write_result3)


async def test_live_bulk_writer(client, cleanup):
    from google.cloud.firestore_v1.async_client import AsyncClient
    from google.cloud.firestore_v1.bulk_writer import BulkWriter

    db: AsyncClient = client
    bw: BulkWriter = db.bulk_writer()
    col = db.collection(f"bulkitems-async{UNIQUE_RESOURCE_ID}")

    for index in range(50):
        doc_ref = col.document(f"id-{index}")
        bw.create(doc_ref, {"index": index})
        cleanup(doc_ref.delete)

    bw.close()
    assert bw._total_batches_sent >= 3  # retries could lead to more than 3 batches
    assert bw._total_write_operations >= 50  # same retries rule applies again
    assert bw._in_flight_documents == 0
    assert len(bw._operations) == 0

    # And now assert that the documents were in fact written to the database
    assert len(await col.get()) == 50


async def test_batch(client, cleanup):
    collection_name = "batch" + UNIQUE_RESOURCE_ID

    document1 = client.document(collection_name, "abc")
    document2 = client.document(collection_name, "mno")
    document3 = client.document(collection_name, "xyz")
    # Add to clean-up before API request (in case ``create()`` fails).
    cleanup(document1.delete)
    cleanup(document2.delete)
    cleanup(document3.delete)

    data2 = {"some": {"deep": "stuff", "and": "here"}, "water": 100.0}
    await document2.create(data2)
    await document3.create({"other": 19})

    batch = client.batch()
    data1 = {"all": True}
    batch.create(document1, data1)
    new_value = "there"
    batch.update(document2, {"some.and": new_value})
    batch.delete(document3)
    write_results = await batch.commit()

    assert len(write_results) == 3

    write_result1 = write_results[0]
    write_result2 = write_results[1]
    write_result3 = write_results[2]
    assert not write_result3._pb.HasField("update_time")

    snapshot1 = await document1.get()
    assert snapshot1.to_dict() == data1
    assert snapshot1.create_time == write_result1.update_time
    assert snapshot1.update_time == write_result1.update_time

    snapshot2 = await document2.get()
    assert snapshot2.to_dict() != data2
    data2["some"]["and"] = new_value
    assert snapshot2.to_dict() == data2
    assert_timestamp_less(snapshot2.create_time, write_result2.update_time)
    assert snapshot2.update_time == write_result2.update_time

    assert not (await document3.get()).exists


async def _persist_documents(
    client: firestore.AsyncClient,
    collection_name: str,
    documents: List[Dict],
    cleanup: Optional[Callable] = None,
):
    """Assuming `documents` is a recursive list of dictionaries representing
    documents and subcollections, this method writes all of those through
    `client.collection(...).document(...).create()`.

    `documents` must be of this structure:
    ```py
    documents = [
        {
            # Required key
            "data": <dictionary with "name" key>,

            # Optional key
            "subcollections": <same structure as `documents`>,
        },
        ...
    ]
    ```
    """
    for block in documents:
        col_ref = client.collection(collection_name)
        document_id: str = block["data"]["name"]
        doc_ref = col_ref.document(document_id)
        await doc_ref.set(block["data"])
        if cleanup is not None:
            cleanup(doc_ref.delete)

        if "subcollections" in block:
            for subcollection_name, inner_blocks in block["subcollections"].items():
                await _persist_documents(
                    client,
                    f"{collection_name}/{document_id}/{subcollection_name}",
                    inner_blocks,
                )


# documents compatible with `_persist_documents`
philosophers_data_set = [
    {
        "data": {"name": "Socrates", "favoriteCity": "Athens"},
        "subcollections": {
            "pets": [{"data": {"name": "Scruffy"}}, {"data": {"name": "Snowflake"}}],
            "hobbies": [
                {"data": {"name": "pontificating"}},
                {"data": {"name": "journaling"}},
            ],
            "philosophers": [
                {"data": {"name": "Aristotle"}},
                {"data": {"name": "Plato"}},
            ],
        },
    },
    {
        "data": {"name": "Aristotle", "favoriteCity": "Sparta"},
        "subcollections": {
            "pets": [{"data": {"name": "Floof-Boy"}}, {"data": {"name": "Doggy-Dog"}}],
            "hobbies": [
                {"data": {"name": "questioning-stuff"}},
                {"data": {"name": "meditation"}},
            ],
        },
    },
    {
        "data": {"name": "Plato", "favoriteCity": "Corinth"},
        "subcollections": {
            "pets": [
                {"data": {"name": "Cuddles"}},
                {"data": {"name": "Sergeant-Puppers"}},
            ],
            "hobbies": [
                {"data": {"name": "abstraction"}},
                {"data": {"name": "hypotheticals"}},
            ],
        },
    },
]


async def _do_recursive_delete(client, bulk_writer, empty_philosophers=False):

    if empty_philosophers:
        philosophers = doc_paths = []
    else:
        philosophers = [philosophers_data_set[0]]
        doc_paths = [
            "",
            "/pets/Scruffy",
            "/pets/Snowflake",
            "/hobbies/pontificating",
            "/hobbies/journaling",
            "/philosophers/Aristotle",
            "/philosophers/Plato",
        ]

    await _persist_documents(
        client, f"philosophers-async{UNIQUE_RESOURCE_ID}", philosophers
    )

    # Assert all documents were created so that when they're missing after the
    # delete, we're actually testing something.
    collection_ref = client.collection(f"philosophers-async{UNIQUE_RESOURCE_ID}")
    for path in doc_paths:
        snapshot = await collection_ref.document(f"Socrates{path}").get()
        assert snapshot.exists, f"Snapshot at Socrates{path} should have been created"

    # Now delete.
    num_deleted = await client.recursive_delete(collection_ref, bulk_writer=bulk_writer)
    assert num_deleted == len(doc_paths)

    # Now they should all be missing
    for path in doc_paths:
        snapshot = await collection_ref.document(f"Socrates{path}").get()
        assert (
            not snapshot.exists
        ), f"Snapshot at Socrates{path} should have been deleted"


async def test_async_recursive_delete_parallelized(client, cleanup):
    from google.cloud.firestore_v1.bulk_writer import BulkWriterOptions, SendMode

    bw = client.bulk_writer(options=BulkWriterOptions(mode=SendMode.parallel))
    await _do_recursive_delete(client, bw)


async def test_async_recursive_delete_serialized(client, cleanup):
    from google.cloud.firestore_v1.bulk_writer import BulkWriterOptions, SendMode

    bw = client.bulk_writer(options=BulkWriterOptions(mode=SendMode.serial))
    await _do_recursive_delete(client, bw)


async def test_async_recursive_delete_parallelized_empty(client, cleanup):
    from google.cloud.firestore_v1.bulk_writer import BulkWriterOptions, SendMode

    bw = client.bulk_writer(options=BulkWriterOptions(mode=SendMode.parallel))
    await _do_recursive_delete(client, bw, empty_philosophers=True)


async def test_async_recursive_delete_serialized_empty(client, cleanup):
    from google.cloud.firestore_v1.bulk_writer import BulkWriterOptions, SendMode

    bw = client.bulk_writer(options=BulkWriterOptions(mode=SendMode.serial))
    await _do_recursive_delete(client, bw, empty_philosophers=True)


async def test_recursive_query(client, cleanup):
    col_id: str = f"philosophers-recursive-async-query{UNIQUE_RESOURCE_ID}"
    await _persist_documents(client, col_id, philosophers_data_set, cleanup)

    ids = [doc.id for doc in await client.collection_group(col_id).recursive().get()]

    expected_ids = [
        # Aristotle doc and subdocs
        "Aristotle",
        "meditation",
        "questioning-stuff",
        "Doggy-Dog",
        "Floof-Boy",
        # Plato doc and subdocs
        "Plato",
        "abstraction",
        "hypotheticals",
        "Cuddles",
        "Sergeant-Puppers",
        # Socrates doc and subdocs
        "Socrates",
        "journaling",
        "pontificating",
        "Scruffy",
        "Snowflake",
        "Aristotle",
        "Plato",
    ]

    assert len(ids) == len(expected_ids)

    for index in range(len(ids)):
        error_msg = (
            f"Expected '{expected_ids[index]}' at spot {index}, " "got '{ids[index]}'"
        )
        assert ids[index] == expected_ids[index], error_msg


async def test_nested_recursive_query(client, cleanup):
    col_id: str = f"philosophers-nested-recursive-async-query{UNIQUE_RESOURCE_ID}"
    await _persist_documents(client, col_id, philosophers_data_set, cleanup)

    collection_ref = client.collection(col_id)
    aristotle = collection_ref.document("Aristotle")
    ids = [doc.id for doc in await aristotle.collection("pets").recursive().get()]

    expected_ids = [
        # Aristotle pets
        "Doggy-Dog",
        "Floof-Boy",
    ]

    assert len(ids) == len(expected_ids)

    for index in range(len(ids)):
        error_msg = (
            f"Expected '{expected_ids[index]}' at spot {index}, " "got '{ids[index]}'"
        )
        assert ids[index] == expected_ids[index], error_msg


async def test_chunked_query(client, cleanup):
    col = client.collection(f"async-chunked-test{UNIQUE_RESOURCE_ID}")
    for index in range(10):
        doc_ref = col.document(f"document-{index + 1}")
        await doc_ref.set({"index": index})
        cleanup(doc_ref.delete)

    lengths: List[int] = [len(chunk) async for chunk in col._chunkify(3)]
    assert len(lengths) == 4
    assert lengths[0] == 3
    assert lengths[1] == 3
    assert lengths[2] == 3
    assert lengths[3] == 1


async def test_chunked_query_smaller_limit(client, cleanup):
    col = client.collection(f"chunked-test-smaller-limit{UNIQUE_RESOURCE_ID}")
    for index in range(10):
        doc_ref = col.document(f"document-{index + 1}")
        await doc_ref.set({"index": index})
        cleanup(doc_ref.delete)

    lengths: List[int] = [len(chunk) async for chunk in col.limit(5)._chunkify(9)]
    assert len(lengths) == 1
    assert lengths[0] == 5


async def test_chunked_and_recursive(client, cleanup):
    col_id = f"chunked-async-recursive-test{UNIQUE_RESOURCE_ID}"
    documents = [
        {
            "data": {"name": "Root-1"},
            "subcollections": {
                "children": [
                    {"data": {"name": f"Root-1--Child-{index + 1}"}}
                    for index in range(5)
                ]
            },
        },
        {
            "data": {"name": "Root-2"},
            "subcollections": {
                "children": [
                    {"data": {"name": f"Root-2--Child-{index + 1}"}}
                    for index in range(5)
                ]
            },
        },
    ]
    await _persist_documents(client, col_id, documents, cleanup)
    collection_ref = client.collection(col_id)
    iter = collection_ref.recursive()._chunkify(5)

    pages = [page async for page in iter]
    doc_ids = [[doc.id for doc in page] for page in pages]

    page_1_ids = [
        "Root-1",
        "Root-1--Child-1",
        "Root-1--Child-2",
        "Root-1--Child-3",
        "Root-1--Child-4",
    ]
    assert doc_ids[0] == page_1_ids

    page_2_ids = [
        "Root-1--Child-5",
        "Root-2",
        "Root-2--Child-1",
        "Root-2--Child-2",
        "Root-2--Child-3",
    ]
    assert doc_ids[1] == page_2_ids

    page_3_ids = ["Root-2--Child-4", "Root-2--Child-5"]
    assert doc_ids[2] == page_3_ids


async def _chain(*iterators):
    """Asynchronous reimplementation of `itertools.chain`."""
    for iterator in iterators:
        async for value in iterator:
            yield value
