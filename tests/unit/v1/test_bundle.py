# Copyright 2021 Google LLC All rights reserved.
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

import unittest

import mock
from google.cloud.firestore_bundle.bundle import FirestoreBundle
from google.cloud.firestore_v1.async_collection import AsyncCollectionReference
from google.cloud.firestore_v1.base_query import BaseQuery
from google.cloud.firestore_v1.collection import CollectionReference
from google.cloud.firestore_v1.services.firestore.async_client import (
    FirestoreAsyncClient,
)
from google.cloud.firestore_v1.services.firestore.client import FirestoreClient
from google.cloud.firestore_v1.types.document import Document
from google.cloud.firestore_v1.types.firestore import RunQueryResponse
from tests.unit.v1 import _test_helpers
from tests.unit.v1 import test__helpers


class _CollectionQueryMixin:

    # Path to each document where we don't specify custom collection names or
    # document Ids
    doc_key: str = "projects/project-project/databases/(default)/documents/col/doc"

    @staticmethod
    def build_results_iterable(items):
        raise NotImplementedError()

    @staticmethod
    def get_collection_class():
        raise NotImplementedError()

    @staticmethod
    def get_internal_client_mock():
        raise NotImplementedError()

    @staticmethod
    def get_client():
        raise NotImplementedError()

    def _bundled_collection_helper(self) -> CollectionReference:
        """Builder of a mocked Query for the sake of testing Bundles.

        Bundling queries involves loading the actual documents for cold storage,
        and this method arranges all of the necessary mocks so that unit tests
        can think they are evaluating a live query.
        """
        client = self.get_client()
        template = client._database_string + "/documents/col/{}"
        document_ids = ["doc-1", "doc-2"]
        documents = [
            RunQueryResponse(
                transaction=b"",
                document=Document(name=template.format(document_id)),
                read_time=_test_helpers.build_timestamp(),
            )
            for document_id in document_ids
        ]
        iterator = self.build_results_iterable(documents)
        api_client = self.get_internal_client_mock()
        api_client.run_query.return_value = iterator
        client._firestore_api_internal = api_client
        return self.get_collection_class()("col", client=client)

    def _bundled_query_helper(self) -> BaseQuery:
        return self._bundled_collection_helper()._query()


class TestBundle(_CollectionQueryMixin, unittest.TestCase):
    @staticmethod
    def build_results_iterable(items):
        return iter(items)

    @staticmethod
    def get_client():
        return _test_helpers.make_client()

    @staticmethod
    def get_internal_client_mock():
        return mock.create_autospec(FirestoreClient)

    @classmethod
    def get_collection_class(cls):
        return CollectionReference

    def test_add_document(self):
        bundle = FirestoreBundle("test")
        doc = _test_helpers.build_document_snapshot(client=_test_helpers.make_client())
        bundle.add_document(doc)
        self.assertEqual(bundle.documents[self.doc_key].snapshot, doc)

    def test_add_document_with_name(self):
        bundle = FirestoreBundle("test")
        doc = _test_helpers.build_document_snapshot(client=_test_helpers.make_client())
        bundle.add_document(doc, query_name="awesome name")
        bundled_doc = bundle.documents.get(self.doc_key)
        self.assertEqual(bundled_doc.snapshot, doc)
        self.assertEqual(bundled_doc.metadata.queries, ["awesome name"])

        # Now add it again with a second name
        bundle.add_document(doc, query_name="less good name, but still okay")
        bundled_doc = bundle.documents.get(self.doc_key)
        self.assertEqual(bundled_doc.snapshot, doc)
        self.assertEqual(
            bundled_doc.metadata.queries,
            ["awesome name", "less good name, but still okay"],
        )

    def test_add_document_with_different_read_times(self):
        bundle = FirestoreBundle("test")
        doc = _test_helpers.build_document_snapshot(
            client=_test_helpers.make_client(),
            data={"version": 1},
            read_time=_test_helpers.build_test_timestamp(second=1),
        )
        # Create another reference to the same document, but with new
        # data and a more recent `read_time`
        doc_refreshed = _test_helpers.build_document_snapshot(
            client=_test_helpers.make_client(),
            data={"version": 2},
            read_time=_test_helpers.build_test_timestamp(second=2),
        )

        bundle.add_document(doc)
        self.assertEqual(
            bundle.documents[self.doc_key].snapshot._data, {"version": 1},
        )
        bundle.add_document(doc_refreshed)
        self.assertEqual(
            bundle.documents[self.doc_key].snapshot._data, {"version": 2},
        )

    def test_add_query(self):
        query = self._bundled_query_helper()
        bundle = FirestoreBundle("test")
        bundle.add_named_query("asdf", query)
        self.assertIsNotNone(bundle.named_queries.get("asdf"))
        self.assertIsNotNone(
            bundle.documents[
                "projects/project-project/databases/(default)/documents/col/doc-1"
            ]
        )
        self.assertIsNotNone(
            bundle.documents[
                "projects/project-project/databases/(default)/documents/col/doc-2"
            ]
        )

    def test_adding_collection_raises_error(self):
        col = self._bundled_collection_helper()
        bundle = FirestoreBundle("test")
        self.assertRaises(ValueError, bundle.add_named_query, "asdf", col)


class TestAsyncBundle(_CollectionQueryMixin, unittest.TestCase):
    @staticmethod
    def get_client():
        return _test_helpers.make_async_client()

    @staticmethod
    def build_results_iterable(items):
        return test__helpers.AsyncIter(items)

    @staticmethod
    def get_internal_client_mock():
        return test__helpers.AsyncMock(spec=["run_query"])

    @classmethod
    def get_collection_class(cls):
        return AsyncCollectionReference

    def test_async_query(self):
        # Create an async query, but this test does not need to be
        # marked as async by pytest because `bundle.add_named_query()`
        # seemlessly handles accepting async iterables.
        async_query = self._bundled_query_helper()
        bundle = FirestoreBundle("test")
        bundle.add_named_query("asdf", async_query)
        self.assertIsNotNone(bundle.named_queries.get("asdf"))
        self.assertIsNotNone(
            bundle.documents[
                "projects/project-project/databases/(default)/documents/col/doc-1"
            ]
        )
        self.assertIsNotNone(
            bundle.documents[
                "projects/project-project/databases/(default)/documents/col/doc-2"
            ]
        )
