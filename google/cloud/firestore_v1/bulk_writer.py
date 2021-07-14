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

import collections
import concurrent.futures
import enum
import functools
import logging
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, NoReturn, Optional, Union

from google.cloud.firestore_v1 import _helpers
from google.cloud.firestore_v1.base_document import BaseDocumentReference
from google.cloud.firestore_v1.base_client import BaseClient
from google.cloud.firestore_v1.bulk_batch import BulkWriteBatch
from google.cloud.firestore_v1.rate_limiter import RateLimiter
from google.cloud.firestore_v1.types.firestore import BatchWriteResponse
from google.cloud.firestore_v1.types.write import WriteResult


logger = logging.getLogger(__name__)


class SendMode(enum.Enum):
    """Control flag for whether a BulkWriter should commit batches in the main
    thread or hand that work off to an executor.
    """

    parallel = enum.auto()
    serial = enum.auto()


class AsyncBulkWriterMixin:
    """
    Mixin which contains the methods on `BulkWriter` which must only be
    submitted to the executor (or called by functions submitted to the executor).
    This mixin exists purely for organization and clarity of implementation
    (e.g., there is no metaclass magic).

    The entrypoint to the parallelizable code path is `_send_batch()`, which is
    wrapped in a decorator which ensures that the `SendMode` is honored.
    """

    def _with_send_mode(fn):
        """Decorates a method to ensure it is only called via the executor
        (IFF the SendMode value is SendMode.parallel!).

        Usage:

            @_with_send_mode
            def my_method(self):
                parallel_stuff()

            def something_else(self):
                # Because of the decorator around `my_method`, the following
                # method invocation:
                self.my_method()
                # becomes equivalent to `self._executor.submit(self.my_method)`
                # when the send mode is `SendMode.parallel`.

        Use on entrypoint methods for code paths that *must* be parallelized.
        """

        @functools.wraps(fn)
        def wrapper(self, *args, **kwargs):
            if self._send_mode == SendMode.parallel:
                return self._executor.submit(lambda: fn(self, *args, **kwargs))
            else:
                return fn(self, *args, **kwargs)

        return wrapper

    @_with_send_mode
    def _send_batch(self, batch: BulkWriteBatch):
        """Sends a batch without regard to rate limits, meaning limits must have
        already been checked. To that end, do not call this directly; instead,
        call `_send_next_batch_when_ready`.

        Args:
            batch(:class:`~google.cloud.firestore_v1.base_batch.BulkWriteBatch`)
        """
        _len_batch: int = len(batch)
        self._in_flight_documents += _len_batch
        response: BatchWriteResponse = self._send(batch)
        self._in_flight_documents -= _len_batch

        # Update bookkeeping totals
        self._total_batches_sent += 1
        self._total_write_operations += _len_batch

        self._process_response(batch, response)

    def _process_response(
        self, batch: BulkWriteBatch, response: BatchWriteResponse
    ) -> NoReturn:
        """Invokes submitted callbacks for each batch and each operation within
        each batch. As this is called from `_send_batch()`, this is parallelized
        if we are in that mode.
        """
        batch_references: List[BaseDocumentReference] = list(
            batch._document_references.values(),
        )
        if self._batch_callback:
            self._batch_callback(batch, response, self)
        if self._success_callback:
            for index, result in enumerate(response.write_results):
                if isinstance(result, WriteResult):
                    # if `result.update_time` is None, this was probably a DELETE
                    self._success_callback(batch_references[index], result, self)
                else:
                    # failure callback should go here
                    pass

    def _send(self, batch: BulkWriteBatch) -> BatchWriteResponse:
        """Hook for overwriting the sending of batches. As this is only called
        from `_send_batch()`, this is parallelized if we are in that mode.
        """
        return batch.commit()  # pragma: NO COVER


class BulkWriter(AsyncBulkWriterMixin):
    """
    Accumulate and efficiently save large amounts of document write operations
    to the server.

    BulkWriter can handle large data migrations or updates, buffering records
    in memory and submitting them to the server in batches of 20.

    The submission of batches is internally parallelized with a ThreadPoolExecutor,
    meaning end developers do not need to manage an event loop or worry about asyncio
    to see parallelization speed ups (which can easily 10x throughput). Because
    of this, there is no companion `AsyncBulkWriter` class, as is usually seen
    with other utility classes.

    Usage:

        # Instantiate the BulkWriter. This works from either `Client` or
        # `AsyncClient`.
        db = firestore.Client()
        bulk_writer = db.bulk_writer()

        # Attach an optional success listener. This will be called once per
        # document.
        bulk_writer.on_write_result(
            lambda reference, result: print(f'Saved {reference._document_path}')
        )

        # Queue an arbitrary amount of write operations.
        # `my_new_records` is a list of (DocumentReference, dict,) tuple-pairs
        # that you supply.
        reference: DocumentReference
        data: dict
        for reference, data in my_new_records:
            bulk_writer.create(reference, data)

        # Block until all pooled writes are complete.
        bulk_writer.flush()

    Args:
        client(:class:`~google.cloud.firestore_v1.client.Client`):
            The client that created this BulkWriter.
    """

    batch_size: int = 20

    def __init__(
        self,
        client: Optional[BaseClient] = None,
        options: Optional["BulkWriterOptions"] = None,
    ):
        self._client = client
        self._options = options or BulkWriterOptions()
        self._send_mode = self._options.mode
        # Redundantly set this variable for IDE type hints
        self._batch: BulkWriteBatch = self._reset_batch()
        self._queued_batches = collections.deque([])
        self._is_open: bool = True
        self._is_sending: bool = False

        self._success_callback: Optional[
            Callable[[BaseDocumentReference, WriteResult, "BulkWriter"], NoReturn]
        ] = None
        self._batch_callback: Optional[
            Callable[[BulkWriteBatch, BatchWriteResponse, "BulkWriter"], NoReturn]
        ] = None
        self._error_callback: Optional[Callable] = None

        self._in_flight_documents: int = 0
        self._rate_limiter = RateLimiter(
            initial_tokens=self._options.initial_ops_per_second,
            global_max_tokens=self._options.max_ops_per_second,
        )

        # Keep track of progress as batches and write operations are completed
        self._total_batches_sent: int = 0
        self._total_write_operations: int = 0

        self._ensure_executor()

    def _reset_batch(self) -> BulkWriteBatch:
        self._batch = BulkWriteBatch(self._client)
        return self._batch

    def _ensure_executor(self):
        self._executor = (
            getattr(self, "_executor", None) or self._instantiate_executor()
        )

    def _ensure_sending(self):
        if not self._is_sending:
            self._ensure_executor()
            self._send_until_queue_is_empty()

    def _instantiate_executor(self):
        return concurrent.futures.ThreadPoolExecutor()

    def flush(self):
        """
        Block until all pooled write operations are complete and then resume
        accepting new write operations.
        """
        # Calling `flush` consecutively is a no-op.
        if not self._executor:
            return

        if len(self._batch) > 0:
            self._enqueue_current_batch()

        while self._queued_batches:
            self._ensure_sending()
            time.sleep(0.1)

        self._is_sending = False
        self._executor.shutdown()
        # Completely release this resource, allowing our sending methods to
        # easily detect if `flush` has been called and we should re-instantiate
        # the executor. The reason for this is that `flush` hangs until everything
        # is sent (and calling `shutdown` is the easiest way to do that), yet,
        # it should not completely end the life of this BulkWriter. That role
        # is filled by the `close` method.
        self._executor = None

    def close(self):
        """
        Block until all pooled write operations are complete and then reject
        any futher write operations.
        """
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

        # The sending loop powers off upon reaching the end of the queue, so
        # here we make sure that is running.
        self._ensure_sending()

        # Reset the local instance
        self._reset_batch()

    def _send_until_queue_is_empty(self):
        """First domino in the sending codepath. This does not need to be
        parallelized for two reasons:

            1) Putting this on a worker thread could lead to two running in parallel
            and thus unpredictable commit ordering or failure to adhere to
            rate limits.
            2) This method only blocks when `self._request_send()` does not immediately
            return, and in that case, the BulkWriter's ramp-up / throttling logic
            has determined that it is attempting to exceed the maximum write speed,
            and so parallelizing this method would not increase performance anyway.

        Once `self._request_send()` returns, this method calls `self._send_batch()`,
        which parallelizes itself if that is our SendMode value.

        And once `self._send_batch()` is called (which does not wait if we are
        sending in parallel), this method calls itself; thus continuing to work
        through all queued batches.

        Note that for sufficiently large data migrations, this can block the
        submission of additional write operations (e.g., the CRUD methods);
        but again, that is only if the maximum write speed is being exceeded,
        and thus this scenario does not actually further reduce performance.
        """
        self._is_sending = True
        # For FIFO order, add to the right of this deque (via `append`) and take
        # from the left.
        next_batch = self._queued_batches.popleft()

        # Block until we are cleared for takeoff, which is fine because this
        # returns instantly unless the rate limiting logic determines that we
        # are attempting to exceed the maximum write speed.
        self._request_send(len(next_batch))

        # Handle some bookkeeping, and ultimately put these bits on the wire.
        # This call is optionally parallelized by `@_with_send_mode`.
        self._send_batch(next_batch)

        if self._queued_batches:
            # As long as there are more items to send, send the next one.
            self._send_until_queue_is_empty()
        else:
            self._is_sending = False

    def _request_send(self, batch_size: int) -> bool:
        # Set up this boolean to avoid repeatedly taking tokens if we're only
        # waiting on the `max_in_flight` limit.
        can_send_batch: bool = False

        while True:
            # To avoid bottlenecks on the server, an additional limit is that no
            # more write operations can be "in flight" (sent but still awaiting
            # response) at any given point than the maximum number of writes per
            # second.
            under_threshold: bool = (
                self._in_flight_documents <= self._rate_limiter._maximum_tokens
            )
            # Ask for tokens each pass through this loop until they are granted,
            # and then stop.
            can_send_batch = can_send_batch or self._rate_limiter.take_tokens(
                batch_size
            )
            if not under_threshold or not can_send_batch:
                # Try again until both checks are true.
                time.sleep(0.01)
                continue

            return True

    def create(
        self, reference: BaseDocumentReference, document_data: Dict,
    ) -> NoReturn:
        """Adds a `create` pb to the in-progress batch.

        If the in-progress batch already contains a write operation involving
        this document reference, the batch will be sealed and added to the commit
        queue, and a new batch will be created with this operation as its first
        entry.

        If this create operation results in the in-progress batch reaching full
        capacity, then the batch will be similarly added to the commit queue, and
        a new batch will be created for future operations.

        Args:
            reference (:class:`~google.cloud.firestore_v1.base_document.BaseDocumentReference`):
                Pointer to the document that should be created.
            document_data (dict):
                Raw data to save to the server.
        """
        self._verify_not_closed()

        if reference in self._batch:
            self._enqueue_current_batch()

        self._batch.create(reference, document_data)
        self._maybe_enqueue_current_batch()

    def delete(
        self,
        reference: BaseDocumentReference,
        option: Optional[_helpers.WriteOption] = None,
    ) -> NoReturn:
        """Adds a `delete` pb to the in-progress batch.

        If the in-progress batch already contains a write operation involving
        this document reference, the batch will be sealed and added to the commit
        queue, and a new batch will be created with this operation as its first
        entry.

        If this delete operation results in the in-progress batch reaching full
        capacity, then the batch will be similarly added to the commit queue, and
        a new batch will be created for future operations.

        Args:
            reference (:class:`~google.cloud.firestore_v1.base_document.BaseDocumentReference`):
                Pointer to the document that should be created.
            option (:class:`~google.cloud.firestore_v1._helpers.WriteOption`):
                Optional flag to modify the nature of this write.
        """
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
        """Adds a `set` pb to the in-progress batch.

        If the in-progress batch already contains a write operation involving
        this document reference, the batch will be sealed and added to the commit
        queue, and a new batch will be created with this operation as its first
        entry.

        If this set operation results in the in-progress batch reaching full
        capacity, then the batch will be similarly added to the commit queue, and
        a new batch will be created for future operations.

        Args:
            reference (:class:`~google.cloud.firestore_v1.base_document.BaseDocumentReference`):
                Pointer to the document that should be created.
            document_data (dict):
                Raw data to save to the server.
            merge (bool):
                Whether or not to completely overwrite any existing data with
                the supplied data.
        """
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
        """Adds an `update` pb to the in-progress batch.

        If the in-progress batch already contains a write operation involving
        this document reference, the batch will be sealed and added to the commit
        queue, and a new batch will be created with this operation as its first
        entry.

        If this update operation results in the in-progress batch reaching full
        capacity, then the batch will be similarly added to the commit queue, and
        a new batch will be created for future operations.

        Args:
            reference (:class:`~google.cloud.firestore_v1.base_document.BaseDocumentReference`):
                Pointer to the document that should be created.
            field_updates (dict):
                Key paths to specific nested data that should be upated.
            option (:class:`~google.cloud.firestore_v1._helpers.WriteOption`):
                Optional flag to modify the nature of this write.
        """
        self._verify_not_closed()

        if reference in self._batch:
            self._enqueue_current_batch()

        self._batch.update(reference, field_updates, option=option)
        self._maybe_enqueue_current_batch()

    def on_write_result(
        self,
        callback: Callable[
            [BaseDocumentReference, WriteResult, "BulkWriter"], NoReturn
        ],
    ) -> NoReturn:
        """Sets a callback that will be invoked once for every successful operation."""
        self._success_callback = callback

    def on_batch_result(
        self,
        callback: Callable[
            [BulkWriteBatch, BatchWriteResponse, "BulkWriter"], NoReturn
        ],
    ) -> NoReturn:
        """Sets a callback that will be invoked once for every successful batch."""
        self._batch_callback = callback

    def on_write_error(self, callback: Callable) -> NoReturn:
        """Sets a callback that will be invoked once for every batch that contains
        an error."""
        self._error_callback = callback  # pragma: NO COVER

    def _verify_not_closed(self):
        if not self._is_open:
            raise Exception("BulkWriter is closed and cannot accept new operations")


@dataclass
class BulkWriterOptions:
    initial_ops_per_second: int = 500
    max_ops_per_second: int = 500
    mode: SendMode = SendMode.parallel
