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
import aiounittest

from typing import List, NoReturn, Optional, Tuple, Type


from google.cloud.firestore_v1._helpers import build_timestamp
from google.cloud.firestore_v1.async_client import AsyncClient
from google.cloud.firestore_v1.base_document import BaseDocumentReference
from google.cloud.firestore_v1.client import Client
from google.cloud.firestore_v1.base_client import BaseClient
from google.cloud.firestore_v1.bulk_batch import BulkWriteBatch
from google.cloud.firestore_v1.bulk_writer import (
    BulkWriter,
    BulkWriterOptions,
    SendMode,
)
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
        self._fail_indices: List[int] = []

    def _send(self, batch: BulkWriteBatch) -> BatchWriteResponse:
        """Generate a fake `BatchWriteResponse` for the supplied batch instead
        of actually submitting it to the server.
        """
        return BatchWriteResponse(
            write_results=[
                WriteResult(update_time=build_timestamp())
                if index not in self._fail_indices
                else WriteResult()
                for index, el in enumerate(batch._document_references.values())
            ]
        )

    def _process_response(
        self, batch: BulkWriteBatch, response: BatchWriteResponse
    ) -> NoReturn:
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
        self, collection_name: Optional[str] = "col", id: Optional[str] = None,
    ) -> Type:
        return self.client.collection(collection_name).document(id)

    def _doc_iter(self, num: int, ids: Optional[List[str]] = None):
        for _ in range(num):
            id: Optional[str] = ids[_] if ids else None
            yield self._get_document_reference(id=id), {"does.not": "matter"}

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
        total_batches = sum([el[1] for el in counts])
        batches_word = "batches" if total_batches != 1 else "batch"
        self.assertEqual(
            len(bw._responses),
            total_batches,
            f"Expected to have sent {total_batches} {batches_word}, but only sent {len(bw._responses)}",
        )
        docs_count = {}
        resp: BatchWriteResponse
        for _, resp in bw._responses:
            docs_count.setdefault(len(resp.write_results), 0)
            docs_count[len(resp.write_results)] += 1

        self.assertEqual(len(docs_count), len(counts))
        for size, num_sent in counts:
            self.assertEqual(docs_count[size], num_sent)

    def test_create_calls_send_correctly(self):
        bw = NoSendBulkWriter(self.client)
        for ref, data in self._doc_iter(101):
            bw.create(ref, data)
        bw.flush()
        # Full batches with 20 items should have been sent 5 times, and a 1-item
        # batch should have been sent once.
        self._verify_bw_activity(bw, [(20, 5,), (1, 1,)])

    def test_delete_calls_send_correctly(self):
        bw = NoSendBulkWriter(self.client)
        for ref, _ in self._doc_iter(101):
            bw.delete(ref)
        bw.flush()
        # Full batches with 20 items should have been sent 5 times, and a 1-item
        # batch should have been sent once.
        self._verify_bw_activity(bw, [(20, 5,), (1, 1,)])

    def test_delete_separates_batch(self):
        bw = NoSendBulkWriter(self.client)
        ref = self._get_document_reference(id="asdf")
        bw.create(ref, {})
        bw.delete(ref)
        bw.flush()
        # Full batches with 20 items should have been sent 5 times, and a 1-item
        # batch should have been sent once.
        self._verify_bw_activity(bw, [(1, 2,)])

    def test_set_calls_send_correctly(self):
        bw = NoSendBulkWriter(self.client)
        for ref, data in self._doc_iter(101):
            bw.set(ref, data)
        bw.flush()
        # Full batches with 20 items should have been sent 5 times, and a 1-item
        # batch should have been sent once.
        self._verify_bw_activity(bw, [(20, 5,), (1, 1,)])

    def test_update_calls_send_correctly(self):
        bw = NoSendBulkWriter(self.client)
        for ref, data in self._doc_iter(101):
            bw.update(ref, data)
        bw.flush()
        # Full batches with 20 items should have been sent 5 times, and a 1-item
        # batch should have been sent once.
        self._verify_bw_activity(bw, [(20, 5,), (1, 1,)])

    def test_update_separates_batch(self):
        bw = NoSendBulkWriter(self.client)
        ref = self._get_document_reference(id="asdf")
        bw.create(ref, {})
        bw.update(ref, {"field": "value"})
        bw.flush()
        # Full batches with 20 items should have been sent 5 times, and a 1-item
        # batch should have been sent once.
        self._verify_bw_activity(bw, [(1, 2,)])

    def test_invokes_callbacks_successfully(self):
        bw = NoSendBulkWriter(self.client)
        # First document in each batch will "fail"
        bw._fail_indices = [0]
        bw._sent_batches = 0
        bw._sent_documents = 0

        def _on_batch(batch, response, bulk_writer):
            assert isinstance(batch, BulkWriteBatch)
            assert isinstance(response, BatchWriteResponse)
            assert isinstance(bulk_writer, BulkWriter)
            bulk_writer._sent_batches += 1

        def _on_write(ref, result, bulk_writer):
            assert isinstance(ref, BaseDocumentReference)
            assert isinstance(result, WriteResult)
            assert isinstance(bulk_writer, BulkWriter)
            # Technically, a missing `update` time only means the operation did
            # not involve an update, aka, was probably a `delete`. But this allows
            # us to test that the data we expect was passed through to each callback.
            if result.update_time is not None:
                bulk_writer._sent_documents += 1

        bw.on_write_result(_on_write)
        bw.on_batch_result(_on_batch)
        for ref, data in self._doc_iter(101):
            bw.create(ref, data)
        bw.flush()
        self.assertEqual(bw._sent_batches, 6)
        self.assertEqual(bw._sent_documents, 101 - 6)

    def test_serial_calls_send_correctly(self):
        bw = NoSendBulkWriter(
            self.client, options=BulkWriterOptions(mode=SendMode.serial)
        )
        for ref, data in self._doc_iter(101):
            bw.create(ref, data)
        bw.flush()
        # Full batches with 20 items should have been sent 5 times, and a 1-item
        # batch should have been sent once.
        self._verify_bw_activity(bw, [(20, 5,), (1, 1,)])

    def test_separates_same_document(self):
        bw = NoSendBulkWriter(self.client)
        for ref, data in self._doc_iter(2, ["same-id", "same-id"]):
            bw.create(ref, data)
        bw.flush()
        # Seeing the same document twice should lead to separate batches
        # Expect to have sent 1-item batches twice.
        self._verify_bw_activity(bw, [(1, 2,)])

    def test_separates_same_document_different_operation(self):
        bw = NoSendBulkWriter(self.client)
        for ref, data in self._doc_iter(1, ["same-id"]):
            bw.create(ref, data)
            bw.set(ref, data)
        bw.flush()
        # Seeing the same document twice should lead to separate batches.
        # Expect to have sent 1-item batches twice.
        self._verify_bw_activity(bw, [(1, 2,)])

    def test_ensure_sending_repeatedly_callable(self):
        bw = NoSendBulkWriter(self.client)
        bw._is_sending = True
        bw._ensure_sending()

    def test_flush_close_repeatedly_callable(self):
        bw = NoSendBulkWriter(self.client)
        bw.flush()
        bw.flush()
        bw.close()

    def test_flush_sends_in_progress(self):
        bw = NoSendBulkWriter(self.client)
        bw.create(self._get_document_reference(), {"whatever": "you want"})
        bw.flush()
        self._verify_bw_activity(bw, [(1, 1,)])

    def test_flush_sends_all_queued_batches(self):
        bw = NoSendBulkWriter(self.client)
        for _ in range(2):
            bw.create(self._get_document_reference(), {"whatever": "you want"})
            bw._queued_batches.append(bw._batch)
            bw._reset_batch()
        bw.flush()
        self._verify_bw_activity(bw, [(1, 2,)])

    def test_cannot_add_after_close(self):
        bw = NoSendBulkWriter(self.client)
        bw.close()
        self.assertRaises(Exception, bw._verify_not_closed)


class TestSyncBulkWriter(_SyncClientMixin, _BaseBulkWriterTests, unittest.TestCase):
    """All BulkWriters are opaquely async, but this one simulates a BulkWriter
    dealing with synchronous DocumentReferences."""


class TestAsyncBulkWriter(
    _AsyncClientMixin, _BaseBulkWriterTests, aiounittest.AsyncTestCase
):
    """All BulkWriters are opaquely async, but this one simulates a BulkWriter
    dealing with AsyncDocumentReferences."""


class TestScheduling(unittest.TestCase):
    def test_max_in_flight_honored(self):
        bw = NoSendBulkWriter(Client())
        # Calling this method sets up all the internal timekeeping machinery
        bw._rate_limiter.take_tokens(20)

        # Now we pretend that all tokens have been consumed. This will force us
        # to wait actual, real world milliseconds before being cleared to send more
        bw._rate_limiter._available_tokens = 0

        st = datetime.datetime.now()

        # Make a real request, subject to the actual real world clock.
        # As this request is 1/10th the per second limit, we should wait ~100ms
        bw._request_send(50)

        self.assertGreater(
            datetime.datetime.now() - st, datetime.timedelta(milliseconds=90),
        )
