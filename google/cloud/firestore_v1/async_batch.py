# Copyright 2020 Google LLC All rights reserved.
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

"""Helpers for batch requests to the Google Cloud Firestore API."""


from google.api_core import gapic_v1  # type: ignore
from google.api_core import retry as retries  # type: ignore

from google.cloud.firestore_v1.base_batch import BaseWriteBatch


class AsyncWriteBatch(BaseWriteBatch):
    """Accumulate write operations to be sent in a batch.

    This has the same set of methods for write operations that
    :class:`~google.cloud.firestore_v1.async_document.AsyncDocumentReference` does,
    e.g. :meth:`~google.cloud.firestore_v1.async_document.AsyncDocumentReference.create`.

    Args:
        client (:class:`~google.cloud.firestore_v1.async_client.AsyncClient`):
            The client that created this batch.
        write_ctx (bool):
            Controls whether this instance should call `commit` or `write` upon
            exiting as a context manager. This parameter has no impact if you
            do not use the instance as a context manager.
    """

    def __init__(self, client, *, write_ctx: bool = False) -> None:
        super(AsyncWriteBatch, self).__init__(client=client, write_ctx=write_ctx)

    async def write(
        self, retry: retries.Retry = gapic_v1.method.DEFAULT, timeout: float = None
    ) -> list:
        """Writes the changes accumulated in this batch.

        Write operations are not guaranteed to be applied in order and must not
        contain multiple writes to any given document. Preferred over `commit`
        for performance reasons if these conditions are acceptable.

        Args:
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.  Defaults to a system-specified policy.
            timeout (float): The timeout for this request.  Defaults to a
                system-specified value.

        Returns:
            List[:class:`google.cloud.proto.firestore.v1.write.BatchWriteResult`, ...]:
            The write results corresponding to the changes committed, returned
            in the same order as the changes were applied to this batch. A
            write result contains an ``update_time`` field.
        """
        request, kwargs = self._prep_write(retry, timeout)

        save_response = await self._client._firestore_api.batch_write(
            request=request, metadata=self._client._rpc_metadata, **kwargs,
        )

        self._write_pbs = []
        self.write_results = results = list(save_response.write_results)

        return results

    async def commit(
        self, retry: retries.Retry = gapic_v1.method.DEFAULT, timeout: float = None,
    ) -> list:
        """Commit the changes accumulated in this batch.

        Args:
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.  Defaults to a system-specified policy.
            timeout (float): The timeout for this request.  Defaults to a
                system-specified value.

        Returns:
            List[:class:`google.cloud.proto.firestore.v1.write.WriteResult`, ...]:
            The write results corresponding to the changes committed, returned
            in the same order as the changes were applied to this batch. A
            write result contains an ``update_time`` field.
        """
        request, kwargs = self._prep_commit(retry, timeout)

        commit_response = await self._client._firestore_api.commit(
            request=request, metadata=self._client._rpc_metadata, **kwargs,
        )

        self._write_pbs = []
        self.write_results = results = list(commit_response.write_results)
        self.commit_time = commit_response.commit_time

        return results

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            await (self.write() if self._write_ctx else self.commit())
