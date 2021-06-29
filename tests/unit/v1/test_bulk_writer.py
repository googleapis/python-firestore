# # Copyright 2021 Google LLC All rights reserved.
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
import unittest

from typing import List, NoReturn, Optional, Tuple, Type

import mock  # type: ignore
import pytest

import google
from google.cloud.firestore_v1._helpers import build_timestamp
from google.cloud.firestore_v1.async_client import AsyncClient
from google.cloud.firestore_v1.base_document import BaseDocumentReference
from google.cloud.firestore_v1.client import Client
from google.cloud.firestore_v1.document import DocumentReference
from google.cloud.firestore_v1.base_client import BaseClient
from google.cloud.firestore_v1.bulk_batch import BulkWriteBatch
from google.cloud.firestore_v1.bulk_writer import BulkWriter, BulkWriterScheduler
from google.cloud.firestore_v1.types.firestore import BatchWriteResponse
from google.cloud.firestore_v1.types.write import WriteResult
from tests.unit.v1._test_helpers import FakeThreadPoolExecutor


class NoSendBulkWriter(BulkWriter):
    """Test-friendly BulkWriter subclass whose `_send` method returns faked
    BatchWriteResponse instances and whose _process_response` method stores
    those faked instances for later evaluation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._responses: List[Tuple[BulkWriteBatch, BatchWriteResponse]] = []

    def _send(self, batch: BulkWriteBatch) -> BatchWriteResponse:
        return BatchWriteResponse(
            write_results=[
                WriteResult(update_time=build_timestamp())
                for el in batch._document_references.values()
            ]
        )
    
    def _process_response(self, batch: BulkWriteBatch, response: BatchWriteResponse) -> NoReturn:
        super()._process_response(batch, response)
        self._responses.append((batch, response,))
    
    def _instantiate_executor(self):
        return FakeThreadPoolExecutor()



class _SyncClientMixin:
    """Mixin which helps a `_BaseBulkWriterTests` subclass simulate usage of
    synchronous Clients, Collections, DocumentReferences, etc."""
    def _get_client_class(self) -> Type:
        return Client


class _AsyncClientMixin:
    """Mixin which helps a `_BaseBulkWriterTests` subclass simulate usage of
    AsyncClients, AsyncCollections, AsyncDocumentReferences, etc."""
    def _get_client_class(self) -> Type:
        return AsyncClient


class _BaseBulkWriterTests:
    def setUp(self):
        self.client: BaseClient = self._get_client_class()()

    def _get_document_reference(
        self,
        collection_name: Optional[str] = 'col',
        id: Optional[str] = None,
    ) -> Type:
        return self.client.collection(collection_name).document(id)

    def _doc_iter(self, num: int, ids: Optional[List[str]] = None):
        for _ in range(num):
            id: Optional[str] = ids[_] if ids else None
            yield self._get_document_reference(id=id), {"doesn't": 'matter'}
        
    def _verify_bw_activity(self, bw: BulkWriter, counts: List[Tuple[int, int]]):
        """
        Args:
            bw: (BulkWriter)
                The BulkWriter instance to inspect.
            counts: (tuple) A sequence of integer pairs, with 0-index integers
                representing the size of sent batches, and 1-index integers
                representing the number of times batches of that size should
                have been sent.
        """
        self.assertEqual(len(bw._responses), sum([el[1] for el in counts]))
        docs_count = {}
        resp: BatchWriteResponse
        for _, resp in bw._responses:
            docs_count.setdefault(len(resp.write_results), 0)
            docs_count[len(resp.write_results)] += 1
        
        self.assertEqual(len(docs_count), len(counts))
        for size, num_sent in counts:
            self.assertEqual(docs_count[size], num_sent)

    def test_calls_send_correctly(self):
        bw = NoSendBulkWriter(self.client)
        for ref, data in self._doc_iter(101):
            bw.create(ref, data)
        bw.flush()
        # Full batches with 20 items should have been sent 5 times, and a 1-item
        # batch should have been sent once.
        self._verify_bw_activity(bw, [(20, 5,), (1, 1,),])

    def test_separates_same_document(self):
        bw = NoSendBulkWriter(self.client)
        for ref, data in self._doc_iter(2, ['same-id', 'same-id']):
            bw.create(ref, data)
        bw.flush()
        # Seeing the same document twice should lead to separate batches
        self._verify_bw_activity(bw, [(1, 2,),])

    def test_separates_same_document_different_operation(self):
        bw = NoSendBulkWriter(self.client)
        for ref, data in self._doc_iter(1, ['same-id']):
            bw.create(ref, data)
            bw.set(ref, data)
        bw.flush()
        # Seeing the same document twice should lead to separate batches
        self._verify_bw_activity(bw, [(1, 2,),])


class TestSyncBulkWriter(_SyncClientMixin, _BaseBulkWriterTests, unittest.TestCase):
    """All BulkWriters are opaquely async, but this one simulates a BulkWriter
    dealing with synchronous DocumentReferences."""
    pass


class TestAsyncBulkWriter(_AsyncClientMixin, _BaseBulkWriterTests, ):
    """All BulkWriters are opaquely async, but this one simulates a BulkWriter
    dealing with AsyncDocumentReferences."""
    pass


class TestBulkWriterScheduler(unittest.TestCase):

    @mock.patch.object(google.cloud.firestore_v1.rate_limiter, "utcnow")
    def test_max_in_flight(self, mocked_now):
        six_minutes_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=6)
        mocked_now.return_value = six_minutes_ago
        
        scheduler = BulkWriterScheduler()
        self.assertEqual(scheduler.max_in_flight, 500)
        
        scheduler.request_send(20)

        now = datetime.datetime.utcnow()
        mocked_now.return_value = now

        scheduler.request_send(20)
        self.assertEqual(scheduler.max_in_flight, 750)