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

"""Helpers for efficiently writing large amounts of data to the Google Cloud
Firestore API."""

import asyncio
import functools
import logging
from typing import Dict, Optional

from google.cloud.firestore_v1 import _helpers, base_bulk_writer
from google.cloud.firestore_v1.async_batch import AsyncBulkWriteBatch
from google.cloud.firestore_v1.async_document import AsyncDocumentReference


logger = logging.getLogger(__name__)


class AsyncBulkWriterScheduler(base_bulk_writer.BulkWriterScheduler):

    async def request_send(self, batch_size: int) -> bool:
        while True:
            if not self._rate_limiter.take_tokens(batch_size):
                await asyncio.sleep(0.01)
                continue
            return True


class AsyncBulkWriterSender(base_bulk_writer.BulkWriterSender):

    async def send(self, batch: AsyncBulkWriteBatch):
        await batch.commit()

class AsyncBulkWriter(base_bulk_writer.BaseBulkWriter):

    def build_scheduler(self) -> AsyncBulkWriterScheduler:
        return AsyncBulkWriterScheduler()

    def build_sender(self) -> AsyncBulkWriterSender:
        return AsyncBulkWriterSender()

    async def _send_ready_batch(self, *, force: bool = False):
        """
        Args:
            force (bool): If true, sends any queued records; even if there are
                          not enough to fill a batch.
        """
        if force or len(self._batch) >= self.batch_size:
            logger.debug('Scheduling batch of %d items', len(self._batch))
            await self._scheduler.request_send(len(self._batch))
            logger.debug('Scheduled batch of %d items', len(self._batch))
            result = await self._sender.send(self._batch)
            self._reset_batch()
            return result

    async def create(
        self,
        reference: AsyncDocumentReference,
        document_data: Dict,
        options: Optional[_helpers.WriteOption] = None
    ) -> base_bulk_writer.WriteResult:
        self._verify_not_closed()
        self._batch.create(reference, document_data)
        await self._send_ready_batch()

    async def delete(
        self,
        reference: AsyncDocumentReference,
        options: Optional[_helpers.WriteOption] = None
    ) -> base_bulk_writer.WriteResult:
        self._verify_not_closed()
        self._batch.delete(reference)
        await self._send_ready_batch()

    async def set(
        self,
        reference: AsyncDocumentReference,
        document_data: Dict,
        options: Optional[_helpers.WriteOption] = None,
    ) -> base_bulk_writer.WriteResult:
        self._verify_not_closed()
        self._batch.set(reference, document_data)
        await self._send_ready_batch()

    async def update(
        self,
        reference: AsyncDocumentReference,
        field_updates: dict,
        options: Optional[_helpers.WriteOption] = None,
    ) -> base_bulk_writer.WriteResult:
        self._verify_not_closed()
        self._batch.update(reference, field_updates)
        await self._send_ready_batch()