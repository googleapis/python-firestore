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


from google.cloud.firestore_v1.base_batch import BaseWriteBatch


class AsyncWriteBatch(BaseWriteBatch):
    """Accumulate write operations to be sent in a batch.

    This has the same set of methods for write operations that
    :class:`~google.cloud.firestore_v1.async_document.AsyncDocumentReference` does,
    e.g. :meth:`~google.cloud.firestore_v1.async_document.AsyncDocumentReference.create`.

    Args:
        client (:class:`~google.cloud.firestore_v1.async_client.AsyncClient`):
            The client that created this batch.
    """

    def __init__(self, client):
        super(AsyncWriteBatch, self).__init__(client=client)

    async def commit(self):
        """Commit the changes accumulated in this batch.

        Returns:
            List[:class:`google.cloud.proto.firestore.v1.write_pb2.WriteResult`, ...]:
            The write results corresponding to the changes committed, returned
            in the same order as the changes were applied to this batch. A
            write result contains an ``update_time`` field.
        """
        commit_response = self._client._firestore_api.commit(
            self._client._database_string,
            self._write_pbs,
            transaction=None,
            metadata=self._client._rpc_metadata,
        )

        self._write_pbs = []
        self.write_results = results = list(commit_response.write_results)
        self.commit_time = commit_response.commit_time
        return results

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            await self.commit()
