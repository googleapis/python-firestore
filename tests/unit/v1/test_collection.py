# Copyright 2017 Google LLC All rights reserved.
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
import unittest

import mock
import six


class TestCollectionReference(unittest.TestCase):
    @staticmethod
    def _get_target_class():
        from google.cloud.firestore_v1.collection import CollectionReference

        return CollectionReference

    def _make_one(self, *args, **kwargs):
        klass = self._get_target_class()
        return klass(*args, **kwargs)

    @staticmethod
    def _get_public_methods(klass):
        return set(
            name
            for name, value in six.iteritems(klass.__dict__)
            if (not name.startswith("_") and isinstance(value, types.FunctionType))
        )

    def test_query_method_matching(self):
        from google.cloud.firestore_v1.query import Query

        query_methods = self._get_public_methods(Query)
        klass = self._get_target_class()
        collection_methods = self._get_public_methods(klass)
        # Make sure every query method is present on
        # ``CollectionReference``.
        self.assertLessEqual(query_methods, collection_methods)

    def test_constructor(self):
        collection_id1 = "rooms"
        document_id = "roomA"
        collection_id2 = "messages"
        client = mock.sentinel.client

        collection = self._make_one(
            collection_id1, document_id, collection_id2, client=client
        )
        self.assertIs(collection._client, client)
        expected_path = (collection_id1, document_id, collection_id2)
        self.assertEqual(collection._path, expected_path)

    def test_constructor_invalid_path(self):
        with self.assertRaises(ValueError):
            self._make_one()
        with self.assertRaises(ValueError):
            self._make_one(99, "doc", "bad-collection-id")
        with self.assertRaises(ValueError):
            self._make_one("bad-document-ID", None, "sub-collection")
        with self.assertRaises(ValueError):
            self._make_one("Just", "A-Document")

    def test_constructor_invalid_kwarg(self):
        with self.assertRaises(TypeError):
            self._make_one("Coh-lek-shun", donut=True)

    def test___eq___other_type(self):
        client = mock.sentinel.client
        collection = self._make_one("name", client=client)
        other = object()
        self.assertFalse(collection == other)

    def test___eq___different_path_same_client(self):
        client = mock.sentinel.client
        collection = self._make_one("name", client=client)
        other = self._make_one("other", client=client)
        self.assertFalse(collection == other)

    def test___eq___same_path_different_client(self):
        client = mock.sentinel.client
        other_client = mock.sentinel.other_client
        collection = self._make_one("name", client=client)
        other = self._make_one("name", client=other_client)
        self.assertFalse(collection == other)

    def test___eq___same_path_same_client(self):
        client = mock.sentinel.client
        collection = self._make_one("name", client=client)
        other = self._make_one("name", client=client)
        self.assertTrue(collection == other)

    def test_id_property(self):
        collection_id = "hi-bob"
        collection = self._make_one(collection_id)
        self.assertEqual(collection.id, collection_id)

    def test_parent_property(self):
        from google.cloud.firestore_v1.document import DocumentReference

        collection_id1 = "grocery-store"
        document_id = "market"
        collection_id2 = "darth"
        client = _make_client()
        collection = self._make_one(
            collection_id1, document_id, collection_id2, client=client
        )

        parent = collection.parent
        self.assertIsInstance(parent, DocumentReference)
        self.assertIs(parent._client, client)
        self.assertEqual(parent._path, (collection_id1, document_id))

    def test_parent_property_top_level(self):
        collection = self._make_one("tahp-leh-vull")
        self.assertIsNone(collection.parent)

    def test_document_factory_explicit_id(self):
        from google.cloud.firestore_v1.document import DocumentReference

        collection_id = "grocery-store"
        document_id = "market"
        client = _make_client()
        collection = self._make_one(collection_id, client=client)

        child = collection.document(document_id)
        self.assertIsInstance(child, DocumentReference)
        self.assertIs(child._client, client)
        self.assertEqual(child._path, (collection_id, document_id))

    @mock.patch(
        "google.cloud.firestore_v1.collection._auto_id",
        return_value="zorpzorpthreezorp012",
    )
    def test_document_factory_auto_id(self, mock_auto_id):
        from google.cloud.firestore_v1.document import DocumentReference

        collection_name = "space-town"
        client = _make_client()
        collection = self._make_one(collection_name, client=client)

        child = collection.document()
        self.assertIsInstance(child, DocumentReference)
        self.assertIs(child._client, client)
        self.assertEqual(child._path, (collection_name, mock_auto_id.return_value))

        mock_auto_id.assert_called_once_with()

    def test__parent_info_top_level(self):
        client = _make_client()
        collection_id = "soap"
        collection = self._make_one(collection_id, client=client)

        parent_path, expected_prefix = collection._parent_info()

        expected_path = "projects/{}/databases/{}/documents".format(
            client.project, client._database
        )
        self.assertEqual(parent_path, expected_path)
        prefix = "{}/{}".format(expected_path, collection_id)
        self.assertEqual(expected_prefix, prefix)

    def test__parent_info_nested(self):
        collection_id1 = "bar"
        document_id = "baz"
        collection_id2 = "chunk"
        client = _make_client()
        collection = self._make_one(
            collection_id1, document_id, collection_id2, client=client
        )

        parent_path, expected_prefix = collection._parent_info()

        expected_path = "projects/{}/databases/{}/documents/{}/{}".format(
            client.project, client._database, collection_id1, document_id
        )
        self.assertEqual(parent_path, expected_path)
        prefix = "{}/{}".format(expected_path, collection_id2)
        self.assertEqual(expected_prefix, prefix)

    def test_add_auto_assigned(self):
        from google.cloud.firestore_v1.proto import document_pb2
        from google.cloud.firestore_v1.document import DocumentReference
        from google.cloud.firestore_v1 import SERVER_TIMESTAMP
        from google.cloud.firestore_v1._helpers import pbs_for_create

        # Create a minimal fake GAPIC add attach it to a real client.
        firestore_api = mock.Mock(spec=["create_document", "commit"])
        write_result = mock.Mock(
            update_time=mock.sentinel.update_time, spec=["update_time"]
        )
        commit_response = mock.Mock(
            write_results=[write_result],
            spec=["write_results", "commit_time"],
            commit_time=mock.sentinel.commit_time,
        )
        firestore_api.commit.return_value = commit_response
        create_doc_response = document_pb2.Document()
        firestore_api.create_document.return_value = create_doc_response
        client = _make_client()
        client._firestore_api_internal = firestore_api

        # Actually make a collection.
        collection = self._make_one("grand-parent", "parent", "child", client=client)

        # Actually call add() on our collection; include a transform to make
        # sure transforms during adds work.
        document_data = {"been": "here", "now": SERVER_TIMESTAMP}

        patch = mock.patch("google.cloud.firestore_v1.collection._auto_id")
        random_doc_id = "DEADBEEF"
        with patch as patched:
            patched.return_value = random_doc_id
            update_time, document_ref = collection.add(document_data)

        # Verify the response and the mocks.
        self.assertIs(update_time, mock.sentinel.update_time)
        self.assertIsInstance(document_ref, DocumentReference)
        self.assertIs(document_ref._client, client)
        expected_path = collection._path + (random_doc_id,)
        self.assertEqual(document_ref._path, expected_path)

        write_pbs = pbs_for_create(document_ref._document_path, document_data)
        firestore_api.commit.assert_called_once_with(
            client._database_string,
            write_pbs,
            transaction=None,
            metadata=client._rpc_metadata,
        )
        # Since we generate the ID locally, we don't call 'create_document'.
        firestore_api.create_document.assert_not_called()

    @staticmethod
    def _write_pb_for_create(document_path, document_data):
        from google.cloud.firestore_v1.proto import common_pb2
        from google.cloud.firestore_v1.proto import document_pb2
        from google.cloud.firestore_v1.proto import write_pb2
        from google.cloud.firestore_v1 import _helpers

        return write_pb2.Write(
            update=document_pb2.Document(
                name=document_path, fields=_helpers.encode_dict(document_data)
            ),
            current_document=common_pb2.Precondition(exists=False),
        )

    def test_add_explicit_id(self):
        from google.cloud.firestore_v1.document import DocumentReference

        # Create a minimal fake GAPIC with a dummy response.
        firestore_api = mock.Mock(spec=["commit"])
        write_result = mock.Mock(
            update_time=mock.sentinel.update_time, spec=["update_time"]
        )
        commit_response = mock.Mock(
            write_results=[write_result],
            spec=["write_results", "commit_time"],
            commit_time=mock.sentinel.commit_time,
        )
        firestore_api.commit.return_value = commit_response

        # Attach the fake GAPIC to a real client.
        client = _make_client()
        client._firestore_api_internal = firestore_api

        # Actually make a collection and call add().
        collection = self._make_one("parent", client=client)
        document_data = {"zorp": 208.75, "i-did-not": b"know that"}
        doc_id = "child"
        update_time, document_ref = collection.add(document_data, document_id=doc_id)

        # Verify the response and the mocks.
        self.assertIs(update_time, mock.sentinel.update_time)
        self.assertIsInstance(document_ref, DocumentReference)
        self.assertIs(document_ref._client, client)
        self.assertEqual(document_ref._path, (collection.id, doc_id))

        write_pb = self._write_pb_for_create(document_ref._document_path, document_data)
        firestore_api.commit.assert_called_once_with(
            client._database_string,
            [write_pb],
            transaction=None,
            metadata=client._rpc_metadata,
        )

    def test_select(self):
        from google.cloud.firestore_v1.query import Query

        collection = self._make_one("collection")
        field_paths = ["a", "b"]
        query = collection.select(field_paths)

        self.assertIsInstance(query, Query)
        self.assertIs(query._parent, collection)
        projection_paths = [
            field_ref.field_path for field_ref in query._projection.fields
        ]
        self.assertEqual(projection_paths, field_paths)

    @staticmethod
    def _make_field_filter_pb(field_path, op_string, value):
        from google.cloud.firestore_v1.proto import query_pb2
        from google.cloud.firestore_v1 import _helpers
        from google.cloud.firestore_v1.query import _enum_from_op_string

        return query_pb2.StructuredQuery.FieldFilter(
            field=query_pb2.StructuredQuery.FieldReference(field_path=field_path),
            op=_enum_from_op_string(op_string),
            value=_helpers.encode_value(value),
        )

    def test_where(self):
        from google.cloud.firestore_v1.query import Query

        collection = self._make_one("collection")
        field_path = "foo"
        op_string = "=="
        value = 45
        query = collection.where(field_path, op_string, value)

        self.assertIsInstance(query, Query)
        self.assertIs(query._parent, collection)
        self.assertEqual(len(query._field_filters), 1)
        field_filter_pb = query._field_filters[0]
        self.assertEqual(
            field_filter_pb, self._make_field_filter_pb(field_path, op_string, value)
        )

    @staticmethod
    def _make_order_pb(field_path, direction):
        from google.cloud.firestore_v1.proto import query_pb2
        from google.cloud.firestore_v1.query import _enum_from_direction

        return query_pb2.StructuredQuery.Order(
            field=query_pb2.StructuredQuery.FieldReference(field_path=field_path),
            direction=_enum_from_direction(direction),
        )

    def test_order_by(self):
        from google.cloud.firestore_v1.query import Query

        collection = self._make_one("collection")
        field_path = "foo"
        direction = Query.DESCENDING
        query = collection.order_by(field_path, direction=direction)

        self.assertIsInstance(query, Query)
        self.assertIs(query._parent, collection)
        self.assertEqual(len(query._orders), 1)
        order_pb = query._orders[0]
        self.assertEqual(order_pb, self._make_order_pb(field_path, direction))

    def test_limit(self):
        from google.cloud.firestore_v1.query import Query

        collection = self._make_one("collection")
        limit = 15
        query = collection.limit(limit)

        self.assertIsInstance(query, Query)
        self.assertIs(query._parent, collection)
        self.assertEqual(query._limit, limit)

    def test_limit_to_last(self):
        from google.cloud.firestore_v1.query import Query

        LIMIT = 15
        collection = self._make_one("collection")
        query = collection.limit_to_last(LIMIT)

        self.assertIsInstance(query, Query)
        self.assertIs(query._parent, collection)
        self.assertEqual(query._limit, LIMIT)
        self.assertTrue(query._limit_to_last)

    def test_offset(self):
        from google.cloud.firestore_v1.query import Query

        collection = self._make_one("collection")
        offset = 113
        query = collection.offset(offset)

        self.assertIsInstance(query, Query)
        self.assertIs(query._parent, collection)
        self.assertEqual(query._offset, offset)

    def test_start_at(self):
        from google.cloud.firestore_v1.query import Query

        collection = self._make_one("collection")
        doc_fields = {"a": "b"}
        query = collection.start_at(doc_fields)

        self.assertIsInstance(query, Query)
        self.assertIs(query._parent, collection)
        self.assertEqual(query._start_at, (doc_fields, True))

    def test_start_after(self):
        from google.cloud.firestore_v1.query import Query

        collection = self._make_one("collection")
        doc_fields = {"d": "foo", "e": 10}
        query = collection.start_after(doc_fields)

        self.assertIsInstance(query, Query)
        self.assertIs(query._parent, collection)
        self.assertEqual(query._start_at, (doc_fields, False))

    def test_end_before(self):
        from google.cloud.firestore_v1.query import Query

        collection = self._make_one("collection")
        doc_fields = {"bar": 10.5}
        query = collection.end_before(doc_fields)

        self.assertIsInstance(query, Query)
        self.assertIs(query._parent, collection)
        self.assertEqual(query._end_at, (doc_fields, True))

    def test_end_at(self):
        from google.cloud.firestore_v1.query import Query

        collection = self._make_one("collection")
        doc_fields = {"opportunity": True, "reason": 9}
        query = collection.end_at(doc_fields)

        self.assertIsInstance(query, Query)
        self.assertIs(query._parent, collection)
        self.assertEqual(query._end_at, (doc_fields, False))

    def _list_documents_helper(self, page_size=None):
        from google.api_core.page_iterator import Iterator
        from google.api_core.page_iterator import Page
        from google.cloud.firestore_v1.document import DocumentReference
        from google.cloud.firestore_v1.gapic.firestore_client import FirestoreClient
        from google.cloud.firestore_v1.proto.document_pb2 import Document

        class _Iterator(Iterator):
            def __init__(self, pages):
                super(_Iterator, self).__init__(client=None)
                self._pages = pages

            def _next_page(self):
                if self._pages:
                    page, self._pages = self._pages[0], self._pages[1:]
                    return Page(self, page, self.item_to_value)

        client = _make_client()
        template = client._database_string + "/documents/{}"
        document_ids = ["doc-1", "doc-2"]
        documents = [
            Document(name=template.format(document_id)) for document_id in document_ids
        ]
        iterator = _Iterator(pages=[documents])
        api_client = mock.create_autospec(FirestoreClient)
        api_client.list_documents.return_value = iterator
        client._firestore_api_internal = api_client
        collection = self._make_one("collection", client=client)

        if page_size is not None:
            documents = list(collection.list_documents(page_size=page_size))
        else:
            documents = list(collection.list_documents())

        # Verify the response and the mocks.
        self.assertEqual(len(documents), len(document_ids))
        for document, document_id in zip(documents, document_ids):
            self.assertIsInstance(document, DocumentReference)
            self.assertEqual(document.parent, collection)
            self.assertEqual(document.id, document_id)

        parent, _ = collection._parent_info()
        api_client.list_documents.assert_called_once_with(
            parent,
            collection.id,
            page_size=page_size,
            show_missing=True,
            metadata=client._rpc_metadata,
        )

    def test_list_documents_wo_page_size(self):
        self._list_documents_helper()

    def test_list_documents_w_page_size(self):
        self._list_documents_helper(page_size=25)

    @mock.patch("google.cloud.firestore_v1.query.Query", autospec=True)
    def test_get(self, query_class):
        collection = self._make_one("collection")
        get_response = collection.get()

        query_class.assert_called_once_with(collection)
        query_instance = query_class.return_value

        self.assertIs(get_response, query_instance.get.return_value)
        query_instance.get.assert_called_once_with(transaction=None)

    @mock.patch("google.cloud.firestore_v1.query.Query", autospec=True)
    def test_get_with_transaction(self, query_class):
        collection = self._make_one("collection")
        transaction = mock.sentinel.txn
        get_response = collection.get(transaction=transaction)

        query_class.assert_called_once_with(collection)
        query_instance = query_class.return_value

        self.assertIs(get_response, query_instance.get.return_value)
        query_instance.get.assert_called_once_with(transaction=transaction)

    @mock.patch("google.cloud.firestore_v1.query.Query", autospec=True)
    def test_stream(self, query_class):
        collection = self._make_one("collection")
        stream_response = collection.stream()

        query_class.assert_called_once_with(collection)
        query_instance = query_class.return_value
        self.assertIs(stream_response, query_instance.stream.return_value)
        query_instance.stream.assert_called_once_with(transaction=None)

    @mock.patch("google.cloud.firestore_v1.query.Query", autospec=True)
    def test_stream_with_transaction(self, query_class):
        collection = self._make_one("collection")
        transaction = mock.sentinel.txn
        stream_response = collection.stream(transaction=transaction)

        query_class.assert_called_once_with(collection)
        query_instance = query_class.return_value
        self.assertIs(stream_response, query_instance.stream.return_value)
        query_instance.stream.assert_called_once_with(transaction=transaction)

    @mock.patch("google.cloud.firestore_v1.collection.Watch", autospec=True)
    def test_on_snapshot(self, watch):
        collection = self._make_one("collection")
        collection.on_snapshot(None)
        watch.for_query.assert_called_once()


class Test__auto_id(unittest.TestCase):
    @staticmethod
    def _call_fut():
        from google.cloud.firestore_v1.collection import _auto_id

        return _auto_id()

    @mock.patch("random.choice")
    def test_it(self, mock_rand_choice):
        from google.cloud.firestore_v1.collection import _AUTO_ID_CHARS

        mock_result = "0123456789abcdefghij"
        mock_rand_choice.side_effect = list(mock_result)
        result = self._call_fut()
        self.assertEqual(result, mock_result)

        mock_calls = [mock.call(_AUTO_ID_CHARS)] * 20
        self.assertEqual(mock_rand_choice.mock_calls, mock_calls)


def _make_credentials():
    import google.auth.credentials

    return mock.Mock(spec=google.auth.credentials.Credentials)


def _make_client():
    from google.cloud.firestore_v1.client import Client

    credentials = _make_credentials()
    return Client(project="project-project", credentials=credentials)
