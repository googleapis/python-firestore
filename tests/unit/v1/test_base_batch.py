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


class TestBaseWriteBatch(unittest.TestCase):
    @staticmethod
    def _get_target_class():
        from google.cloud.firestore_v1.base_batch import BaseWriteBatch

        return BaseWriteBatch

    def _make_one(self, *args, **kwargs):
        klass = self._get_target_class()
        return klass(*args, **kwargs)

    def test_constructor(self):
        batch = self._make_one(mock.sentinel.client)
        self.assertIs(batch._client, mock.sentinel.client)
        self.assertEqual(batch._write_pbs, [])
        self.assertIsNone(batch.write_results)
        self.assertIsNone(batch.commit_time)

    def test__add_write_pbs(self):
        batch = self._make_one(mock.sentinel.client)
        self.assertEqual(batch._write_pbs, [])
        batch._add_write_pbs([mock.sentinel.write1, mock.sentinel.write2])
        self.assertEqual(batch._write_pbs, [mock.sentinel.write1, mock.sentinel.write2])

    def test_create(self):
        from google.cloud.firestore_v1.proto import common_pb2
        from google.cloud.firestore_v1.proto import document_pb2
        from google.cloud.firestore_v1.proto import write_pb2

        client = _make_client()
        batch = self._make_one(client)
        self.assertEqual(batch._write_pbs, [])

        reference = client.document("this", "one")
        document_data = {"a": 10, "b": 2.5}
        ret_val = batch.create(reference, document_data)
        self.assertIsNone(ret_val)
        new_write_pb = write_pb2.Write(
            update=document_pb2.Document(
                name=reference._document_path,
                fields={
                    "a": _value_pb(integer_value=document_data["a"]),
                    "b": _value_pb(double_value=document_data["b"]),
                },
            ),
            current_document=common_pb2.Precondition(exists=False),
        )
        self.assertEqual(batch._write_pbs, [new_write_pb])

    def test_set(self):
        from google.cloud.firestore_v1.proto import document_pb2
        from google.cloud.firestore_v1.proto import write_pb2

        client = _make_client()
        batch = self._make_one(client)
        self.assertEqual(batch._write_pbs, [])

        reference = client.document("another", "one")
        field = "zapzap"
        value = u"meadows and flowers"
        document_data = {field: value}
        ret_val = batch.set(reference, document_data)
        self.assertIsNone(ret_val)
        new_write_pb = write_pb2.Write(
            update=document_pb2.Document(
                name=reference._document_path,
                fields={field: _value_pb(string_value=value)},
            )
        )
        self.assertEqual(batch._write_pbs, [new_write_pb])

    def test_set_merge(self):
        from google.cloud.firestore_v1.proto import document_pb2
        from google.cloud.firestore_v1.proto import write_pb2

        client = _make_client()
        batch = self._make_one(client)
        self.assertEqual(batch._write_pbs, [])

        reference = client.document("another", "one")
        field = "zapzap"
        value = u"meadows and flowers"
        document_data = {field: value}
        ret_val = batch.set(reference, document_data, merge=True)
        self.assertIsNone(ret_val)
        new_write_pb = write_pb2.Write(
            update=document_pb2.Document(
                name=reference._document_path,
                fields={field: _value_pb(string_value=value)},
            ),
            update_mask={"field_paths": [field]},
        )
        self.assertEqual(batch._write_pbs, [new_write_pb])

    def test_update(self):
        from google.cloud.firestore_v1.proto import common_pb2
        from google.cloud.firestore_v1.proto import document_pb2
        from google.cloud.firestore_v1.proto import write_pb2

        client = _make_client()
        batch = self._make_one(client)
        self.assertEqual(batch._write_pbs, [])

        reference = client.document("cats", "cradle")
        field_path = "head.foot"
        value = u"knees toes shoulders"
        field_updates = {field_path: value}

        ret_val = batch.update(reference, field_updates)
        self.assertIsNone(ret_val)

        map_pb = document_pb2.MapValue(fields={"foot": _value_pb(string_value=value)})
        new_write_pb = write_pb2.Write(
            update=document_pb2.Document(
                name=reference._document_path,
                fields={"head": _value_pb(map_value=map_pb)},
            ),
            update_mask=common_pb2.DocumentMask(field_paths=[field_path]),
            current_document=common_pb2.Precondition(exists=True),
        )
        self.assertEqual(batch._write_pbs, [new_write_pb])

    def test_delete(self):
        from google.cloud.firestore_v1.proto import write_pb2

        client = _make_client()
        batch = self._make_one(client)
        self.assertEqual(batch._write_pbs, [])

        reference = client.document("early", "mornin", "dawn", "now")
        ret_val = batch.delete(reference)
        self.assertIsNone(ret_val)
        new_write_pb = write_pb2.Write(delete=reference._document_path)
        self.assertEqual(batch._write_pbs, [new_write_pb])


def _value_pb(**kwargs):
    from google.cloud.firestore_v1.proto.document_pb2 import Value

    return Value(**kwargs)


def _make_credentials():
    import google.auth.credentials

    return mock.Mock(spec=google.auth.credentials.Credentials)


def _make_client(project="seventy-nine"):
    from google.cloud.firestore_v1.client import Client

    credentials = _make_credentials()
    return Client(project=project, credentials=credentials)
