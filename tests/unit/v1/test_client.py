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

import datetime
import types
import unittest

import mock


class TestClient(unittest.TestCase):

    PROJECT = "my-prahjekt"

    @staticmethod
    def _get_target_class():
        from google.cloud.firestore_v1.client import Client

        return Client

    def _make_one(self, *args, **kwargs):
        klass = self._get_target_class()
        return klass(*args, **kwargs)

    def _make_default_one(self):
        credentials = _make_credentials()
        return self._make_one(project=self.PROJECT, credentials=credentials)

    def test_constructor(self):
        from google.cloud.firestore_v1.client import _CLIENT_INFO
        from google.cloud.firestore_v1.client import DEFAULT_DATABASE

        credentials = _make_credentials()
        client = self._make_one(project=self.PROJECT, credentials=credentials)
        self.assertEqual(client.project, self.PROJECT)
        self.assertEqual(client._credentials, credentials)
        self.assertEqual(client._database, DEFAULT_DATABASE)
        self.assertIs(client._client_info, _CLIENT_INFO)
        self.assertIsNone(client._emulator_host)

    def test_constructor_with_emulator_host(self):
        from google.cloud.firestore_v1.base_client import _FIRESTORE_EMULATOR_HOST

        credentials = _make_credentials()
        emulator_host = "localhost:8081"
        with mock.patch("os.getenv") as getenv:
            getenv.return_value = emulator_host
            client = self._make_one(project=self.PROJECT, credentials=credentials)
            self.assertEqual(client._emulator_host, emulator_host)
            getenv.assert_called_once_with(_FIRESTORE_EMULATOR_HOST)

    def test_constructor_explicit(self):
        credentials = _make_credentials()
        database = "now-db"
        client_info = mock.Mock()
        client_options = mock.Mock()
        client = self._make_one(
            project=self.PROJECT,
            credentials=credentials,
            database=database,
            client_info=client_info,
            client_options=client_options,
        )
        self.assertEqual(client.project, self.PROJECT)
        self.assertEqual(client._credentials, credentials)
        self.assertEqual(client._database, database)
        self.assertIs(client._client_info, client_info)
        self.assertIs(client._client_options, client_options)

    def test_constructor_w_client_options(self):
        credentials = _make_credentials()
        client = self._make_one(
            project=self.PROJECT,
            credentials=credentials,
            client_options={"api_endpoint": "foo-firestore.googleapis.com"},
        )
        self.assertEqual(client._target, "foo-firestore.googleapis.com")

    def test_collection_factory(self):
        from google.cloud.firestore_v1.collection import CollectionReference

        collection_id = "users"
        client = self._make_default_one()
        collection = client.collection(collection_id)

        self.assertEqual(collection._path, (collection_id,))
        self.assertIs(collection._client, client)
        self.assertIsInstance(collection, CollectionReference)

    def test_collection_factory_nested(self):
        from google.cloud.firestore_v1.collection import CollectionReference

        client = self._make_default_one()
        parts = ("users", "alovelace", "beep")
        collection_path = "/".join(parts)
        collection1 = client.collection(collection_path)

        self.assertEqual(collection1._path, parts)
        self.assertIs(collection1._client, client)
        self.assertIsInstance(collection1, CollectionReference)

        # Make sure using segments gives the same result.
        collection2 = client.collection(*parts)
        self.assertEqual(collection2._path, parts)
        self.assertIs(collection2._client, client)
        self.assertIsInstance(collection2, CollectionReference)

    def test__get_collection_reference(self):
        from google.cloud.firestore_v1.collection import CollectionReference

        client = self._make_default_one()
        collection = client._get_collection_reference("collectionId")

        self.assertIs(collection._client, client)
        self.assertIsInstance(collection, CollectionReference)

    def test_collection_group(self):
        client = self._make_default_one()
        query = client.collection_group("collectionId").where("foo", "==", u"bar")

        assert query._all_descendants
        assert query._field_filters[0].field.field_path == "foo"
        assert query._field_filters[0].value.string_value == u"bar"
        assert query._field_filters[0].op == query._field_filters[0].Operator.EQUAL
        assert query._parent.id == "collectionId"

    def test_collection_group_no_slashes(self):
        client = self._make_default_one()
        with self.assertRaises(ValueError):
            client.collection_group("foo/bar")

    def test_document_factory(self):
        from google.cloud.firestore_v1.document import DocumentReference

        parts = ("rooms", "roomA")
        client = self._make_default_one()
        doc_path = "/".join(parts)
        document1 = client.document(doc_path)

        self.assertEqual(document1._path, parts)
        self.assertIs(document1._client, client)
        self.assertIsInstance(document1, DocumentReference)

        # Make sure using segments gives the same result.
        document2 = client.document(*parts)
        self.assertEqual(document2._path, parts)
        self.assertIs(document2._client, client)
        self.assertIsInstance(document2, DocumentReference)

    def test_document_factory_w_absolute_path(self):
        from google.cloud.firestore_v1.document import DocumentReference

        parts = ("rooms", "roomA")
        client = self._make_default_one()
        doc_path = "/".join(parts)
        to_match = client.document(doc_path)
        document1 = client.document(to_match._document_path)

        self.assertEqual(document1._path, parts)
        self.assertIs(document1._client, client)
        self.assertIsInstance(document1, DocumentReference)

    def test_document_factory_w_nested_path(self):
        from google.cloud.firestore_v1.document import DocumentReference

        client = self._make_default_one()
        parts = ("rooms", "roomA", "shoes", "dressy")
        doc_path = "/".join(parts)
        document1 = client.document(doc_path)

        self.assertEqual(document1._path, parts)
        self.assertIs(document1._client, client)
        self.assertIsInstance(document1, DocumentReference)

        # Make sure using segments gives the same result.
        document2 = client.document(*parts)
        self.assertEqual(document2._path, parts)
        self.assertIs(document2._client, client)
        self.assertIsInstance(document2, DocumentReference)

    def test_collections(self):
        from google.api_core.page_iterator import Iterator
        from google.api_core.page_iterator import Page
        from google.cloud.firestore_v1.collection import CollectionReference

        collection_ids = ["users", "projects"]
        client = self._make_default_one()
        firestore_api = mock.Mock(spec=["list_collection_ids"])
        client._firestore_api_internal = firestore_api

        # TODO(microgen): list_collection_ids isn't a pager.
        # https://github.com/googleapis/gapic-generator-python/issues/516
        class _Iterator(Iterator):
            def __init__(self, pages):
                super(_Iterator, self).__init__(client=None)
                self._pages = pages
                self.collection_ids = pages[0]

            def _next_page(self):
                if self._pages:
                    page, self._pages = self._pages[0], self._pages[1:]
                    return Page(self, page, self.item_to_value)

        iterator = _Iterator(pages=[collection_ids])
        firestore_api.list_collection_ids.return_value = iterator

        collections = list(client.collections())

        self.assertEqual(len(collections), len(collection_ids))
        for collection, collection_id in zip(collections, collection_ids):
            self.assertIsInstance(collection, CollectionReference)
            self.assertEqual(collection.parent, None)
            self.assertEqual(collection.id, collection_id)

        base_path = client._database_string + "/documents"
        firestore_api.list_collection_ids.assert_called_once_with(
            request={"parent": base_path}, metadata=client._rpc_metadata
        )

    def _get_all_helper(self, client, references, document_pbs, **kwargs):
        # Create a minimal fake GAPIC with a dummy response.
        firestore_api = mock.Mock(spec=["batch_get_documents"])
        response_iterator = iter(document_pbs)
        firestore_api.batch_get_documents.return_value = response_iterator

        # Attach the fake GAPIC to a real client.
        client._firestore_api_internal = firestore_api

        # Actually call get_all().
        snapshots = client.get_all(references, **kwargs)
        self.assertIsInstance(snapshots, types.GeneratorType)

        return list(snapshots)

    def _info_for_get_all(self, data1, data2):
        client = self._make_default_one()
        document1 = client.document("pineapple", "lamp1")
        document2 = client.document("pineapple", "lamp2")

        # Make response protobufs.
        document_pb1, read_time = _doc_get_info(document1._document_path, data1)
        response1 = _make_batch_response(found=document_pb1, read_time=read_time)

        document, read_time = _doc_get_info(document2._document_path, data2)
        response2 = _make_batch_response(found=document, read_time=read_time)

        return client, document1, document2, response1, response2

    def test_get_all(self):
        from google.cloud.firestore_v1.types import common
        from google.cloud.firestore_v1.document import DocumentSnapshot

        data1 = {"a": u"cheese"}
        data2 = {"b": True, "c": 18}
        info = self._info_for_get_all(data1, data2)
        client, document1, document2, response1, response2 = info

        # Exercise the mocked ``batch_get_documents``.
        field_paths = ["a", "b"]
        snapshots = self._get_all_helper(
            client,
            [document1, document2],
            [response1, response2],
            field_paths=field_paths,
        )
        self.assertEqual(len(snapshots), 2)

        snapshot1 = snapshots[0]
        self.assertIsInstance(snapshot1, DocumentSnapshot)
        self.assertIs(snapshot1._reference, document1)
        self.assertEqual(snapshot1._data, data1)

        snapshot2 = snapshots[1]
        self.assertIsInstance(snapshot2, DocumentSnapshot)
        self.assertIs(snapshot2._reference, document2)
        self.assertEqual(snapshot2._data, data2)

        # Verify the call to the mock.
        doc_paths = [document1._document_path, document2._document_path]
        mask = common.DocumentMask(field_paths=field_paths)
        client._firestore_api.batch_get_documents.assert_called_once_with(
            request={
                "database": client._database_string,
                "documents": doc_paths,
                "mask": mask,
                "transaction": None,
            },
            metadata=client._rpc_metadata,
        )

    def test_get_all_with_transaction(self):
        from google.cloud.firestore_v1.document import DocumentSnapshot

        data = {"so-much": 484}
        info = self._info_for_get_all(data, {})
        client, document, _, response, _ = info
        transaction = client.transaction()
        txn_id = b"the-man-is-non-stop"
        transaction._id = txn_id

        # Exercise the mocked ``batch_get_documents``.
        snapshots = self._get_all_helper(
            client, [document], [response], transaction=transaction
        )
        self.assertEqual(len(snapshots), 1)

        snapshot = snapshots[0]
        self.assertIsInstance(snapshot, DocumentSnapshot)
        self.assertIs(snapshot._reference, document)
        self.assertEqual(snapshot._data, data)

        # Verify the call to the mock.
        doc_paths = [document._document_path]
        client._firestore_api.batch_get_documents.assert_called_once_with(
            request={
                "database": client._database_string,
                "documents": doc_paths,
                "mask": None,
                "transaction": txn_id,
            },
            metadata=client._rpc_metadata,
        )

    def test_get_all_unknown_result(self):
        from google.cloud.firestore_v1.base_client import _BAD_DOC_TEMPLATE

        info = self._info_for_get_all({"z": 28.5}, {})
        client, document, _, _, response = info

        # Exercise the mocked ``batch_get_documents``.
        with self.assertRaises(ValueError) as exc_info:
            self._get_all_helper(client, [document], [response])

        err_msg = _BAD_DOC_TEMPLATE.format(response.found.name)
        self.assertEqual(exc_info.exception.args, (err_msg,))

        # Verify the call to the mock.
        doc_paths = [document._document_path]
        client._firestore_api.batch_get_documents.assert_called_once_with(
            request={
                "database": client._database_string,
                "documents": doc_paths,
                "mask": None,
                "transaction": None,
            },
            metadata=client._rpc_metadata,
        )

    def test_get_all_wrong_order(self):
        from google.cloud.firestore_v1.document import DocumentSnapshot

        data1 = {"up": 10}
        data2 = {"down": -10}
        info = self._info_for_get_all(data1, data2)
        client, document1, document2, response1, response2 = info
        document3 = client.document("pineapple", "lamp3")
        response3 = _make_batch_response(missing=document3._document_path)

        # Exercise the mocked ``batch_get_documents``.
        snapshots = self._get_all_helper(
            client, [document1, document2, document3], [response2, response1, response3]
        )

        self.assertEqual(len(snapshots), 3)

        snapshot1 = snapshots[0]
        self.assertIsInstance(snapshot1, DocumentSnapshot)
        self.assertIs(snapshot1._reference, document2)
        self.assertEqual(snapshot1._data, data2)

        snapshot2 = snapshots[1]
        self.assertIsInstance(snapshot2, DocumentSnapshot)
        self.assertIs(snapshot2._reference, document1)
        self.assertEqual(snapshot2._data, data1)

        self.assertFalse(snapshots[2].exists)

        # Verify the call to the mock.
        doc_paths = [
            document1._document_path,
            document2._document_path,
            document3._document_path,
        ]
        client._firestore_api.batch_get_documents.assert_called_once_with(
            request={
                "database": client._database_string,
                "documents": doc_paths,
                "mask": None,
                "transaction": None,
            },
            metadata=client._rpc_metadata,
        )

    def test_batch(self):
        from google.cloud.firestore_v1.batch import WriteBatch

        client = self._make_default_one()
        batch = client.batch()
        self.assertIsInstance(batch, WriteBatch)
        self.assertIs(batch._client, client)
        self.assertEqual(batch._write_pbs, [])

    def test_transaction(self):
        from google.cloud.firestore_v1.transaction import Transaction

        client = self._make_default_one()
        transaction = client.transaction(max_attempts=3, read_only=True)
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction._write_pbs, [])
        self.assertEqual(transaction._max_attempts, 3)
        self.assertTrue(transaction._read_only)
        self.assertIsNone(transaction._id)


def _make_credentials():
    import google.auth.credentials

    return mock.Mock(spec=google.auth.credentials.Credentials)


def _make_batch_response(**kwargs):
    from google.cloud.firestore_v1.types import firestore

    return firestore.BatchGetDocumentsResponse(**kwargs)


def _doc_get_info(ref_string, values):
    from google.cloud.firestore_v1.types import document
    from google.cloud._helpers import _datetime_to_pb_timestamp
    from google.cloud.firestore_v1 import _helpers

    now = datetime.datetime.utcnow()
    read_time = _datetime_to_pb_timestamp(now)
    delta = datetime.timedelta(seconds=100)
    update_time = _datetime_to_pb_timestamp(now - delta)
    create_time = _datetime_to_pb_timestamp(now - 2 * delta)

    document_pb = document.Document(
        name=ref_string,
        fields=_helpers.encode_dict(values),
        create_time=create_time,
        update_time=update_time,
    )

    return document_pb, read_time
