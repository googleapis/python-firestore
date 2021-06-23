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

import abc
import logging
from typing import Callable, Dict, NoReturn, Optional

from google.cloud.firestore_v1 import _helpers
from google.cloud.firestore_v1.base_document import BaseDocumentReference
from google.cloud.firestore_v1.base_client import BaseClient
from google.cloud.firestore_v1.base_batch import BaseBulkWriteBatch
from google.cloud.firestore_v1.rate_limiter import RateLimiter
from google.cloud.firestore_v1.types.firestore import BatchWriteResponse


logger = logging.getLogger(__name__)


class WriteResult:
    pass


class BaseBulkWriterScheduler(metaclass=abc.ABCMeta):

    def __init__(self, rate_limiter: Optional[RateLimiter] = None):
        self._rate_limiter = rate_limiter or RateLimiter()

    @abc.abstractmethod
    def request_send(self, batch_size: int) -> bool:
        raise NotImplementedError()


class BaseBulkWriterSender(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def send(self, batch: BaseBulkWriteBatch) -> BatchWriteResponse:
        raise NotImplementedError()


class BaseBulkWriter(metaclass=abc.ABCMeta):
    """
    Args:
        client(:class:`~google.cloud.firestore_v1.client.Client`):
            The client that created this BulkWriter.
        scheduler(:class:`~google.cloud.firestore_v1.base_bulk_writer.BaseBulkWriterScheduler`):
            Time keeper that rate-limits writes in accordance with 5/5/5 ramp-up.
        sender(:class:`~google.cloud.firestore_v1.base_bulk_writer.BaseBulkWriterSender`):
            Utility which knows how to put BatchWrite objects on the wire.
    """

    batch_size: int = 20

    def __init__(self,
        client: Optional[BaseClient] = None,
        scheduler: Optional[BaseBulkWriterScheduler] = None,
        sender: Optional[BaseBulkWriterSender] = None,
    ):
        self._client = client
        self._scheduler: BaseBulkWriterScheduler = scheduler or self.build_scheduler()
        self._sender: BaseBulkWriterSender = sender or self.build_sender()
        self._is_open = True
        self._batch: Optional[BaseBulkWriteBatch] = None
        self._reset_batch()

        self._in_flight_batches = set()

        # BulkWriteBatch objects cannot contain > 1 write operation to the same
        # document reference (which is distinguishable by the document path),
        # so here we track seen documents to prevent competing operations.
        self._document_paths = set()

    @abc.abstractmethod
    def build_scheduler(self) -> BaseBulkWriterScheduler:
        raise NotImplementedError()

    @abc.abstractmethod
    def build_sender(self) -> BaseBulkWriterSender:
        raise NotImplementedError()

    def _register_document_reference(self, reference: BaseDocumentReference):
        if reference._document_path in self._document_paths:
            raise ValueError(
                'Cannot add multiple references to same document within a '
                'single BulkWriteBatch'
            )
        self._document_paths.add(reference._document_path)

    def _reset_batch(self):
        self._batch = self._client.bulk_batch()
        self._document_paths = set()

    def flush(self):
        self._send_ready_batch(force=True)

    def close(self):
        self.flush()
        self._is_open = False

    @abc.abstractmethod
    def create(
        self,
        reference: BaseDocumentReference,
        document_data: Dict,
        options: Optional[_helpers.WriteOption] = None
    ) -> WriteResult:
        raise NotImplementedError()

    @abc.abstractmethod
    def delete(
        self,
        reference: BaseDocumentReference,
        options: Optional[_helpers.WriteOption] = None
    ) -> WriteResult:
        raise NotImplementedError()

    @abc.abstractmethod
    def set(
        self,
        reference: BaseDocumentReference,
        document_data: Dict,
        options: Optional[_helpers.WriteOption] = None,
    ) -> WriteResult:
        raise NotImplementedError()

    @abc.abstractmethod
    def update(
        self,
        reference: BaseDocumentReference,
        field_updates: dict,
        options: Optional[_helpers.WriteOption] = None,
    ) -> WriteResult:
        raise NotImplementedError()

    def onWriteResult(self, callback: Callable) -> NoReturn:
        pass

    def onWriteError(self, callback: Callable) -> NoReturn:
        pass

    def flush(self) -> NoReturn:
        pass

    def close(self) -> NoReturn:
        self._is_open = False

    def _verify_not_closed(self):
        if not self._is_open:
            raise Exception("BulkWriter is closed and cannot accept new operations")
