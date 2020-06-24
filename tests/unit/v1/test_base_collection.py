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

import unittest

import mock


class TestCollectionReference(unittest.TestCase):
    @staticmethod
    def _get_target_class():
        from google.cloud.firestore_v1.base_collection import BaseCollectionReference

        return BaseCollectionReference

    def _make_one(self, *args, **kwargs):
        klass = self._get_target_class()
        return klass(*args, **kwargs)

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
        "google.cloud.firestore_v1.base_collection._auto_id",
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


class Test__auto_id(unittest.TestCase):
    @staticmethod
    def _call_fut():
        from google.cloud.firestore_v1.base_collection import _auto_id

        return _auto_id()

    @mock.patch("random.choice")
    def test_it(self, mock_rand_choice):
        from google.cloud.firestore_v1.base_collection import _AUTO_ID_CHARS

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
