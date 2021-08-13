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

from google.cloud.firestore_v1.types.document import Document
from google.cloud.firestore_v1.types.firestore import RunQueryResponse
import types
import unittest

import mock

from tests.unit.v1 import _test_helpers


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
        return set().union(
            *(
                (
                    name
                    for name, value in class_.__dict__.items()
                    if (
                        not name.startswith("_")
                        and isinstance(value, types.FunctionType)
                    )
                )
                for class_ in (klass,) + klass.__bases__
            )
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

    def test_add_auto_assigned(self):
        from google.cloud.firestore_v1.types import document
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
        create_doc_response = document.Document()
        firestore_api.create_document.return_value = create_doc_response
        client = _test_helpers.make_client()
        client._firestore_api_internal = firestore_api

        # Actually make a collection.
        collection = self._make_one("grand-parent", "parent", "child", client=client)

        # Actually call add() on our collection; include a transform to make
        # sure transforms during adds work.
        document_data = {"been": "here", "now": SERVER_TIMESTAMP}

        patch = mock.patch("google.cloud.firestore_v1.base_collection._auto_id")
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
            request={
                "database": client._database_string,
                "writes": write_pbs,
                "transaction": None,
            },
            metadata=client._rpc_metadata,
        )
        # Since we generate the ID locally, we don't call 'create_document'.
        firestore_api.create_document.assert_not_called()

    @staticmethod
    def _write_pb_for_create(document_path, document_data):
        from google.cloud.firestore_v1.types import common
        from google.cloud.firestore_v1.types import document
        from google.cloud.firestore_v1.types import write
        from google.cloud.firestore_v1 import _helpers

        return write.Write(
            update=document.Document(
                name=document_path, fields=_helpers.encode_dict(document_data)
            ),
            current_document=common.Precondition(exists=False),
        )

    def _add_helper(self, retry=None, timeout=None):
        from google.cloud.firestore_v1.document import DocumentReference
        from google.cloud.firestore_v1 import _helpers as _fs_v1_helpers

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
        client = _test_helpers.make_client()
        client._firestore_api_internal = firestore_api

        # Actually make a collection and call add().
        collection = self._make_one("parent", client=client)
        document_data = {"zorp": 208.75, "i-did-not": b"know that"}
        doc_id = "child"

        kwargs = _fs_v1_helpers.make_retry_timeout_kwargs(retry, timeout)
        update_time, document_ref = collection.add(
            document_data, document_id=doc_id, **kwargs
        )

        # Verify the response and the mocks.
        self.assertIs(update_time, mock.sentinel.update_time)
        self.assertIsInstance(document_ref, DocumentReference)
        self.assertIs(document_ref._client, client)
        self.assertEqual(document_ref._path, (collection.id, doc_id))

        write_pb = self._write_pb_for_create(document_ref._document_path, document_data)
        firestore_api.commit.assert_called_once_with(
            request={
                "database": client._database_string,
                "writes": [write_pb],
                "transaction": None,
            },
            metadata=client._rpc_metadata,
            **kwargs,
        )

    def test_add_explicit_id(self):
        self._add_helper()

    def test_add_w_retry_timeout(self):
        from google.api_core.retry import Retry

        retry = Retry(predicate=object())
        timeout = 123.0
        self._add_helper(retry=retry, timeout=timeout)

    def _list_documents_helper(self, page_size=None, retry=None, timeout=None):
        from google.cloud.firestore_v1 import _helpers as _fs_v1_helpers
        from google.api_core.page_iterator import Iterator
        from google.api_core.page_iterator import Page
        from google.cloud.firestore_v1.document import DocumentReference
        from google.cloud.firestore_v1.services.firestore.client import FirestoreClient
        from google.cloud.firestore_v1.types.document import Document

        class _Iterator(Iterator):
            def __init__(self, pages):
                super(_Iterator, self).__init__(client=None)
                self._pages = pages

            def _next_page(self):
                if self._pages:
                    page, self._pages = self._pages[0], self._pages[1:]
                    return Page(self, page, self.item_to_value)

        client = _test_helpers.make_client()
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
        kwargs = _fs_v1_helpers.make_retry_timeout_kwargs(retry, timeout)

        if page_size is not None:
            documents = list(collection.list_documents(page_size=page_size, **kwargs))
        else:
            documents = list(collection.list_documents(**kwargs))

        # Verify the response and the mocks.
        self.assertEqual(len(documents), len(document_ids))
        for document, document_id in zip(documents, document_ids):
            self.assertIsInstance(document, DocumentReference)
            self.assertEqual(document.parent, collection)
            self.assertEqual(document.id, document_id)

        parent, _ = collection._parent_info()
        api_client.list_documents.assert_called_once_with(
            request={
                "parent": parent,
                "collection_id": collection.id,
                "page_size": page_size,
                "show_missing": True,
                "mask": {"field_paths": None},
            },
            metadata=client._rpc_metadata,
            **kwargs,
        )

    def test_list_documents_wo_page_size(self):
        self._list_documents_helper()

    def test_list_documents_w_retry_timeout(self):
        from google.api_core.retry import Retry

        retry = Retry(predicate=object())
        timeout = 123.0
        self._list_documents_helper(retry=retry, timeout=timeout)

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
    def test_get_w_retry_timeout(self, query_class):
        from google.api_core.retry import Retry

        retry = Retry(predicate=object())
        timeout = 123.0
        collection = self._make_one("collection")
        get_response = collection.get(retry=retry, timeout=timeout)

        query_class.assert_called_once_with(collection)
        query_instance = query_class.return_value

        self.assertIs(get_response, query_instance.get.return_value)
        query_instance.get.assert_called_once_with(
            transaction=None, retry=retry, timeout=timeout,
        )

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
    def test_stream_w_retry_timeout(self, query_class):
        from google.api_core.retry import Retry

        retry = Retry(predicate=object())
        timeout = 123.0
        collection = self._make_one("collection")
        stream_response = collection.stream(retry=retry, timeout=timeout)

        query_class.assert_called_once_with(collection)
        query_instance = query_class.return_value
        self.assertIs(stream_response, query_instance.stream.return_value)
        query_instance.stream.assert_called_once_with(
            transaction=None, retry=retry, timeout=timeout,
        )

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

    def test_recursive(self):
        from google.cloud.firestore_v1.query import Query

        col = self._make_one("collection")
        self.assertIsInstance(col.recursive(), Query)

    def test_chunkify(self):
        client = _test_helpers.make_client()
        col = client.collection("my-collection")

        client._firestore_api_internal = mock.Mock(spec=["run_query"])

        results = []
        for index in range(10):
            results.append(
                RunQueryResponse(
                    document=Document(
                        name=f"projects/project-project/databases/(default)/documents/my-collection/{index}",
                    ),
                ),
            )

        chunks = [
            results[:3],
            results[3:6],
            results[6:9],
            results[9:],
        ]

        def _get_chunk(*args, **kwargs):
            return iter(chunks.pop(0))

        client._firestore_api_internal.run_query.side_effect = _get_chunk

        counter = 0
        expected_lengths = [3, 3, 3, 1]
        for chunk in col._chunkify(3):
            msg = f"Expected chunk of length {expected_lengths[counter]} at index {counter}. Saw {len(chunk)}."
            self.assertEqual(len(chunk), expected_lengths[counter], msg)
            counter += 1
