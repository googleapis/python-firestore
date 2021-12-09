# Copyright 2020 Google LLC All rights reserved.
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


def _make_base_document_reference(*args, **kwargs):
    from google.cloud.firestore_v1.base_document import BaseDocumentReference

    return BaseDocumentReference(*args, **kwargs)


def test_basedocumentreference_constructor():
    collection_id1 = "users"
    document_id1 = "alovelace"
    collection_id2 = "platform"
    document_id2 = "*nix"
    client = mock.MagicMock()
    client.__hash__.return_value = 1234

    document = _make_base_document_reference(
        collection_id1, document_id1, collection_id2, document_id2, client=client
    )
    assert document._client is client
    expected_path = "/".join(
        (collection_id1, document_id1, collection_id2, document_id2)
    )
    assert document.path == expected_path


def test_basedocumentreference_constructor_invalid_path_empty():
    with pytest.raises(ValueError):
        _make_base_document_reference()


def test_basedocumentreference_constructor_invalid_path_bad_collection_id():
    with pytest.raises(ValueError):
        _make_base_document_reference(None, "before", "bad-collection-id", "fifteen")


def test_basedocumentreference_constructor_invalid_path_bad_document_id():
    with pytest.raises(ValueError):
        _make_base_document_reference("bad-document-ID", None)


def test_basedocumentreference_constructor_invalid_path_bad_number_args():
    with pytest.raises(ValueError):
        _make_base_document_reference("Just", "A-Collection", "Sub")


def test_basedocumentreference_constructor_invalid_kwarg():
    with pytest.raises(TypeError):
        _make_base_document_reference("Coh-lek-shun", "Dahk-yu-mehnt", burger=18.75)


def test_basedocumentreference___copy__():
    client = _make_client("rain")
    document = _make_base_document_reference("a", "b", client=client)
    # Access the document path so it is copied.
    doc_path = document._document_path
    assert doc_path == document._document_path_internal

    new_document = document.__copy__()
    assert new_document is not document
    assert new_document._client is document._client
    assert new_document._path == document._path
    assert new_document._document_path_internal == document._document_path_internal


def test_basedocumentreference___deepcopy__calls_copy():
    client = mock.sentinel.client
    document = _make_base_document_reference("a", "b", client=client)
    document.__copy__ = mock.Mock(return_value=mock.sentinel.new_doc, spec=[])

    unused_memo = {}
    new_document = document.__deepcopy__(unused_memo)
    assert new_document is mock.sentinel.new_doc
    document.__copy__.assert_called_once_with()


def test_basedocumentreference__eq__same_type():
    document1 = _make_base_document_reference("X", "YY", client=mock.sentinel.client)
    document2 = _make_base_document_reference("X", "ZZ", client=mock.sentinel.client)
    document3 = _make_base_document_reference("X", "YY", client=mock.sentinel.client2)
    document4 = _make_base_document_reference("X", "YY", client=mock.sentinel.client)

    pairs = ((document1, document2), (document1, document3), (document2, document3))
    for candidate1, candidate2 in pairs:
        # We use == explicitly since assertNotEqual would use !=.
        assert not (candidate1 == candidate2)

    # Check the only equal one.
    assert document1 == document4
    assert document1 is not document4


def test_basedocumentreference__eq__other_type():
    document = _make_base_document_reference("X", "YY", client=mock.sentinel.client)
    other = object()
    assert not (document == other)
    assert document.__eq__(other) is NotImplemented


def test_basedocumentreference___hash__():
    client = mock.MagicMock()
    client.__hash__.return_value = 234566789
    document = _make_base_document_reference("X", "YY", client=client)
    assert hash(document) == hash(("X", "YY")) + hash(client)


def test_basedocumentreference__ne__same_type():
    document1 = _make_base_document_reference("X", "YY", client=mock.sentinel.client)
    document2 = _make_base_document_reference("X", "ZZ", client=mock.sentinel.client)
    document3 = _make_base_document_reference("X", "YY", client=mock.sentinel.client2)
    document4 = _make_base_document_reference("X", "YY", client=mock.sentinel.client)

    assert document1 != document2
    assert document1 != document3
    assert document2 != document3

    assert not (document1 != document4)
    assert document1 is not document4


def test_basedocumentreference__ne__other_type():
    document = _make_base_document_reference("X", "YY", client=mock.sentinel.client)
    other = object()
    assert document != other
    assert document.__ne__(other) is NotImplemented


def test_basedocumentreference__document_path_property():
    project = "hi-its-me-ok-bye"
    client = _make_client(project=project)

    collection_id = "then"
    document_id = "090909iii"
    document = _make_base_document_reference(collection_id, document_id, client=client)
    doc_path = document._document_path
    expected = "projects/{}/databases/{}/documents/{}/{}".format(
        project, client._database, collection_id, document_id
    )
    assert doc_path == expected
    assert document._document_path_internal is doc_path

    # Make sure value is cached.
    document._document_path_internal = mock.sentinel.cached
    assert document._document_path is mock.sentinel.cached


def test_basedocumentreference__document_path_property_no_client():
    document = _make_base_document_reference("hi", "bye")
    assert document._client is None
    with pytest.raises(ValueError):
        getattr(document, "_document_path")

    assert document._document_path_internal is None


def test_basedocumentreference_id_property():
    document_id = "867-5309"
    document = _make_base_document_reference("Co-lek-shun", document_id)
    assert document.id == document_id


def test_basedocumentreference_parent_property():
    from google.cloud.firestore_v1.collection import CollectionReference

    collection_id = "grocery-store"
    document_id = "market"
    client = _make_client()
    document = _make_base_document_reference(collection_id, document_id, client=client)

    parent = document.parent
    assert isinstance(parent, CollectionReference)
    assert parent._client is client
    assert parent._path == (collection_id,)


def test_basedocumentreference_collection_factory():
    from google.cloud.firestore_v1.collection import CollectionReference

    collection_id = "grocery-store"
    document_id = "market"
    new_collection = "fruits"
    client = _make_client()
    document = _make_base_document_reference(collection_id, document_id, client=client)

    child = document.collection(new_collection)
    assert isinstance(child, CollectionReference)
    assert child._client is client
    assert child._path == (collection_id, document_id, new_collection)


def _make_document_snapshot(*args, **kwargs):
    from google.cloud.firestore_v1.document import DocumentSnapshot

    return DocumentSnapshot(*args, **kwargs)


def _make_w_ref(ref_path=("a", "b"), data={}, exists=True):
    client = mock.sentinel.client
    reference = _make_base_document_reference(*ref_path, client=client)
    return _make_document_snapshot(
        reference,
        data,
        exists,
        mock.sentinel.read_time,
        mock.sentinel.create_time,
        mock.sentinel.update_time,
    )


def test_documentsnapshot_constructor():
    client = mock.sentinel.client
    reference = _make_base_document_reference("hi", "bye", client=client)
    data = {"zoop": 83}
    snapshot = _make_document_snapshot(
        reference,
        data,
        True,
        mock.sentinel.read_time,
        mock.sentinel.create_time,
        mock.sentinel.update_time,
    )
    assert snapshot._reference is reference
    assert snapshot._data == data
    assert snapshot._data is not data  # Make sure copied
    assert snapshot._exists
    assert snapshot.read_time is mock.sentinel.read_time
    assert snapshot.create_time is mock.sentinel.create_time
    assert snapshot.update_time is mock.sentinel.update_time


def test_documentsnapshot___eq___other_type():
    snapshot = _make_w_ref()
    other = object()
    assert not (snapshot == other)


def test_documentsnapshot___eq___different_reference_same_data():
    snapshot = _make_w_ref(("a", "b"))
    other = _make_w_ref(("c", "d"))
    assert not (snapshot == other)


def test_documentsnapshot___eq___same_reference_different_data():
    snapshot = _make_w_ref(("a", "b"))
    other = _make_w_ref(("a", "b"), {"foo": "bar"})
    assert not (snapshot == other)


def test_documentsnapshot___eq___same_reference_same_data():
    snapshot = _make_w_ref(("a", "b"), {"foo": "bar"})
    other = _make_w_ref(("a", "b"), {"foo": "bar"})
    assert snapshot == other


def test_documentsnapshot___hash__():
    import datetime
    from proto.datetime_helpers import DatetimeWithNanoseconds

    client = mock.MagicMock()
    client.__hash__.return_value = 234566789
    reference = _make_base_document_reference("hi", "bye", client=client)
    data = {"zoop": 83}
    update_time = DatetimeWithNanoseconds(
        2021, 10, 4, 17, 43, 27, nanosecond=123456789, tzinfo=datetime.timezone.utc
    )
    snapshot = _make_document_snapshot(
        reference, data, True, None, mock.sentinel.create_time, update_time
    )
    assert hash(snapshot) == hash(reference) + hash(update_time)


def test_documentsnapshot__client_property():
    reference = _make_base_document_reference(
        "ok", "fine", "now", "fore", client=mock.sentinel.client
    )
    snapshot = _make_document_snapshot(reference, {}, False, None, None, None)
    assert snapshot._client is mock.sentinel.client


def test_documentsnapshot_exists_property():
    reference = mock.sentinel.reference

    snapshot1 = _make_document_snapshot(reference, {}, False, None, None, None)
    assert not snapshot1.exists
    snapshot2 = _make_document_snapshot(reference, {}, True, None, None, None)
    assert snapshot2.exists


def test_documentsnapshot_id_property():
    document_id = "around"
    reference = _make_base_document_reference(
        "look", document_id, client=mock.sentinel.client
    )
    snapshot = _make_document_snapshot(reference, {}, True, None, None, None)
    assert snapshot.id == document_id
    assert reference.id == document_id


def test_documentsnapshot_reference_property():
    snapshot = _make_document_snapshot(
        mock.sentinel.reference, {}, True, None, None, None
    )
    assert snapshot.reference is mock.sentinel.reference


def test_documentsnapshot_get():
    data = {"one": {"bold": "move"}}
    snapshot = _make_document_snapshot(None, data, True, None, None, None)

    first_read = snapshot.get("one")
    second_read = snapshot.get("one")
    assert first_read == data.get("one")
    assert first_read is not data.get("one")
    assert first_read == second_read
    assert first_read is not second_read

    with pytest.raises(KeyError):
        snapshot.get("two")


def test_documentsnapshot_nonexistent_snapshot():
    snapshot = _make_document_snapshot(None, None, False, None, None, None)
    assert snapshot.get("one") is None


def test_documentsnapshot_to_dict():
    data = {"a": 10, "b": ["definitely", "mutable"], "c": {"45": 50}}
    snapshot = _make_document_snapshot(None, data, True, None, None, None)
    as_dict = snapshot.to_dict()
    assert as_dict == data
    assert as_dict is not data
    # Check that the data remains unchanged.
    as_dict["b"].append("hi")
    assert data == snapshot.to_dict()
    assert data != as_dict


def test_documentsnapshot_non_existent():
    snapshot = _make_document_snapshot(None, None, False, None, None, None)
    as_dict = snapshot.to_dict()
    assert as_dict is None


def test__get_document_path():
    from google.cloud.firestore_v1.base_document import _get_document_path

    project = "prah-jekt"
    client = _make_client(project=project)
    path = ("Some", "Document", "Child", "Shockument")
    document_path = _get_document_path(client, path)

    expected = "projects/{}/databases/{}/documents/{}".format(
        project, client._database, "/".join(path)
    )
    assert document_path == expected


def test__consume_single_get_success():
    from google.cloud.firestore_v1.base_document import _consume_single_get

    response_iterator = iter([mock.sentinel.result])
    result = _consume_single_get(response_iterator)
    assert result is mock.sentinel.result


def test__consume_single_get_failure_not_enough():
    from google.cloud.firestore_v1.base_document import _consume_single_get

    response_iterator = iter([])
    with pytest.raises(ValueError):
        _consume_single_get(response_iterator)


def test__consume_single_get_failure_too_many():
    from google.cloud.firestore_v1.base_document import _consume_single_get

    response_iterator = iter([None, None])
    with pytest.raises(ValueError):
        _consume_single_get(response_iterator)


def test__first_write_result_success():
    from google.protobuf import timestamp_pb2
    from google.cloud.firestore_v1.types import write
    from google.cloud.firestore_v1.base_document import _first_write_result

    single_result = write.WriteResult(
        update_time=timestamp_pb2.Timestamp(seconds=1368767504, nanos=458000123)
    )
    write_results = [single_result]
    result = _first_write_result(write_results)
    assert result is single_result


def test__first_write_result_failure_not_enough():
    from google.cloud.firestore_v1.base_document import _first_write_result

    write_results = []
    with pytest.raises(ValueError):
        _first_write_result(write_results)


def test__first_write_result_more_than_one():
    from google.cloud.firestore_v1.types import write
    from google.cloud.firestore_v1.base_document import _first_write_result

    result1 = write.WriteResult()
    result2 = write.WriteResult()
    write_results = [result1, result2]
    result = _first_write_result(write_results)
    assert result is result1


def _make_credentials():
    import google.auth.credentials

    return mock.Mock(spec=google.auth.credentials.Credentials)


def _make_client(project="project-project"):
    from google.cloud.firestore_v1.client import Client

    credentials = _make_credentials()
    return Client(project=project, credentials=credentials)
