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
import asyncio
import collections
import concurrent.futures
import logging
import time
from typing import Callable, Dict, List, NoReturn, Optional, Union

from google.cloud.firestore_v1 import _helpers
from google.cloud.firestore_v1.base_document import BaseDocumentReference
from google.cloud.firestore_v1.base_client import BaseClient
from google.cloud.firestore_v1.batch import BulkWriteBatch
from google.cloud.firestore_v1.rate_limiter import RateLimiter
from google.cloud.firestore_v1.types.firestore import BatchWriteResponse
from google.cloud.firestore_v1.types.write import WriteResult


logger = logging.getLogger(__name__)


class BaseBulkWriterScheduler(metaclass=abc.ABCMeta):

    def __init__(self, rate_limiter: Optional[RateLimiter] = None):
        self._rate_limiter = rate_limiter or RateLimiter()

    @abc.abstractmethod
    def request_send(self, batch_size: int) -> bool:
        raise NotImplementedError()

    @property
    def max_in_flight(self):
        return self._rate_limiter._maximum_tokens

class AsyncBulkWriterScheduler(BaseBulkWriterScheduler):

    async def request_send(self, batch_size: int) -> bool:
        while True:
            if not self._rate_limiter.take_tokens(batch_size):
                await asyncio.sleep(0.01)
                continue
            return True

class BulkWriterScheduler(BaseBulkWriterScheduler):
    """
    Handles the purely time-based limits on how many batches can be sent
    within a given period of time (as spelled out by the `_rate_limiter`).

    All other concerns, like max concurrent batches in flight, or batches that
    depend on the completion of other batches, are handled elsewhere.
    """

    def request_send(self, batch_size: int) -> bool:
        while True:
            if not self._rate_limiter.take_tokens(batch_size):
                time.sleep(0.01)
                continue
            return True


class BulkWriterSender:
    def send(self, batch: BulkWriteBatch) -> BatchWriteResponse:
        return batch.commit()


def executor_only(fn):
    def wrapper(self):
        return self._executor.submit(fn)
    return wrapper


class AsyncBulkWriterMixin:
    """
    Mixin which contains all of the methods on `BulkWriter` which must only be
    executed inside of the executor. This mixin has no functional impact on
    `BulkWriter` and exists purely for organization and clarity of the
    implementation.

    BulkWriter contains a mix of methods safe for the main thread and methods
    which must be parallelized by the executor. All methods directly on BulkWriter
    are safe to call directly, but methods found here on `AsyncBulkWriterMixin`
    must either be called via `self._executor.submit(my_callable)`, or be called
    by such a method.

    The call chain for these methods is:

        bulk_writer.create()  # Safe for main thread
        -> self._maybe_enqueue_current_batch()  # Called by `create()`, and
                                                # safe for the main thread.
        -> self._enqueue_current_batch()        # Called by `_maybe_enqueue()`, 
                                                # and safe for the main thread.
        -> self._send_next_batch_when_ready()   # Called by `enqueue_current_batch()`,
                                                # and, as it can wait on the clock,
                                                # is required to be invoked via
                                                # the executor.
        -> self._send_batch(batch)              # Called by `_send_next_batch_when_ready()`,
                                                # and, as that method should already
                                                # be parallelized, this will also
                                                # release the GIL while it waits
                                                # on network I/O.
    """

    def _send_next_batch_when_ready(self):
        """Entrypoint to send a batch. After passing all rate limiting checks,
        this actually puts a batch on the wire.

        For optimal performance, this method *must* be submitted to the
        executor instead of being called directly.
        """
        if not self._queued_batches:
            return

        _batch = self._queued_batches.pop()

        # Block until the clock says we can send, which is fine since we are
        # already parallelized by the executor.
        self._scheduler.request_send(len(_batch))

        while self._in_flight_documents >= self._scheduler.max_in_flight:
            # Block until there is breathing room in the in-flight queue, which
            # is fine since we are already parallelized by the executor.
            time.sleep(0.01)
        
        # Once all prerequisities are satisfied, we can finally send.
        self._send_batch(_batch)

    def _send_batch(self, batch: BulkWriteBatch):
        """Sends a batch without regard to rate limits, meaning limits must have
        already been checked. To that end, do not call this directly; instead,
        call `_send_next_batch_when_ready`.
        
        Args:
            batch(:class:`~google.cloud.firestore_v1.base_batch.BulkWriteBatch`):
        """
        _len_batch: int = len(batch)
        self._in_flight_documents += _len_batch
        response: BatchWriteResponse = self._sender.send(batch)
        self._in_flight_documents -= _len_batch

        # Update bookkeeping totals
        self._total_batches_sent += 1
        self._total_write_operations += _len_batch
        
        # The successful sending of a batch frees up the BulkWriter to send
        # another one, so here we restart the process
        if self._executor and not self._executor._shutdown:
            self._executor.submit(self._send_next_batch_when_ready)

        batch_references: List[BaseDocumentReference] = list(
            batch._document_references.values(),
        )
        if self._success_callback:
            for index, result in enumerate(response):
                if isinstance(result, WriteResult):
                    self._success_callback(batch_references[index], result)


class BaseBulkWriter(AsyncBulkWriterMixin, metaclass=abc.ABCMeta):
    """
    Args:
        client(:class:`~google.cloud.firestore_v1.client.Client`):
            The client that created this BulkWriter.
        scheduler(:class:`~google.cloud.firestore_v1.bulk_writer.BulkWriterScheduler`):
            Time keeper that rate-limits writes in accordance with 5/5/5 ramp-up.
        sender(:class:`~google.cloud.firestore_v1.bulk_writer.BulkWriterSender`):
            Utility which knows how to put BatchWrite objects on the wire.
    """

    batch_size: int = 20

    def __init__(self,
        client: Optional[BaseClient] = None,
        scheduler: Optional[BulkWriterScheduler] = None,
        sender: Optional[BulkWriterSender] = None,
    ):
        self._client = client
        self._instantiate_executor()
        self._scheduler: BaseBulkWriterScheduler = scheduler or BulkWriterScheduler()
        self._sender: BulkWriterSender = sender or BulkWriterSender()
        # Redundantly set this variable for IDE type hints
        self._batch: BulkWriteBatch = self._reset_batch()
        self._queued_batches = collections.deque([])
        self._is_open = True
        
        self._success_callback: Optional[Callable[[BaseDocumentReference, WriteResult], NoReturn]] = None
        self._error_callback: Optional[Callable] = None

        self._in_flight_documents: int = 0

        # Keep track of progress as batches and write operations are completed
        self._total_batches_sent: int = 0
        self._total_write_operations: int = 0

    def _reset_batch(self) -> BulkWriteBatch:
        self._batch = self._client.bulk_batch()
        return self._batch

    def _instantiate_executor(self):
        self._executor = concurrent.futures.ThreadPoolExecutor()

    def flush(self):
        if len(self._batch) > 0:
            self._enqueue_current_batch()
        self._executor.shutdown()
        # Completely release this resource, allowing our sending methods to
        # easily detect if `flush` has been called and we should re-instantiate
        # the executor. The reason for this is that `flush` hangs until everything
        # is sent (and calling `shutdown` is the easiest) way to do that, yet,
        # it should not completely end the life of this BulkWriter. That role
        # is filled by the `close` method.
        self._executor = None

    def close(self):
        self._is_open = False
        self.flush()

    def _maybe_enqueue_current_batch(self):
        """
        Checks to see whether the in-progress batch is full and, if it is,
        adds it to the sending queue.

        Args:
            force (bool): If true, sends the current batch even if it is only
                partially full.
        """
        if len(self._batch) >= self.batch_size:
            self._enqueue_current_batch()
    
    def _enqueue_current_batch(self):
        """Adds the current batch to the back of the sending line, resets the
        local instance, and begins the process of actually sending whatever
        batch is in the front of the line, which will often be a different batch.
        """
        # Put our batch in the back of the sending line
        self._queued_batches.append(self._batch)

        # Reset the local instance
        self._reset_batch()

        # Reset the executor if the user called `flush` and then resumed submission
        # of write operations.
        if not self._executor or self._executor._shutdown:
            self._instantiate_executor()

        # Lastly, trigger the sending of the batch in the front of the line.
        self._executor.submit(self._send_next_batch_when_ready)
    
    def create(
        self,
        reference: BaseDocumentReference,
        document_data: Dict,
    ) -> NoReturn:
        self._verify_not_closed()
        
        if reference in self._batch:
            self._enqueue_current_batch()

        self._batch.create(reference, document_data)
        self._maybe_enqueue_current_batch()

    def delete(
        self,
        reference: BaseDocumentReference,
        option: Optional[_helpers.WriteOption] = None
    ) -> NoReturn:
        self._verify_not_closed()
        
        if reference in self._batch:
            self._enqueue_current_batch()

        self._batch.delete(reference, option=option)
        self._maybe_enqueue_current_batch()

    def set(
        self,
        reference: BaseDocumentReference,
        document_data: Dict,
        merge: Union[bool, list] = False,
    ) -> NoReturn:
        self._verify_not_closed()
        
        if reference in self._batch:
            self._enqueue_current_batch()

        self._batch.set(reference, document_data, merge=merge)
        self._maybe_enqueue_current_batch()

    def update(
        self,
        reference: BaseDocumentReference,
        field_updates: dict,
        option: Optional[_helpers.WriteOption] = None,
    ) -> NoReturn:
        self._verify_not_closed()
        
        if reference in self._batch:
            self._enqueue_current_batch()

        self._batch.update(reference, field_updates, option=option)
        self._maybe_enqueue_current_batch()

    def on_write_result(self, callback: Callable[[BaseDocumentReference, WriteResult], NoReturn]) -> NoReturn:
        self._success_callback = callback

    def on_write_error(self, callback: Callable) -> NoReturn:
        self._error_callback = callback

    def _verify_not_closed(self):
        if not self._is_open:
            raise Exception("BulkWriter is closed and cannot accept new operations")
