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

"""Classes for representing collections for the Google Cloud Firestore API."""

from google.api_core import gapic_v1  # type: ignore
from google.api_core import retry as retries  # type: ignore

from google.cloud.firestore_v1.base_collection import (
    BaseCollectionReference,
    _item_to_document_ref,
)
from google.cloud.firestore_v1 import (
    async_query,
    async_document,
)

from google.cloud.firestore_v1.document import DocumentReference

from typing import AsyncIterator
from typing import Any, AsyncGenerator, Tuple

# Types needed only for Type Hints
from google.cloud.firestore_v1.transaction import Transaction


class AsyncCollectionReference(BaseCollectionReference):
    """A reference to a collection in a Firestore database.

    The collection may already exist or this class can facilitate creation
    of documents within the collection.

    Args:
        path (Tuple[str, ...]): The components in the collection path.
            This is a series of strings representing each collection and
            sub-collection ID, as well as the document IDs for any documents
            that contain a sub-collection.
        kwargs (dict): The keyword arguments for the constructor. The only
            supported keyword is ``client`` and it must be a
            :class:`~google.cloud.firestore_v1.client.Client` if provided. It
            represents the client that created this collection reference.

    Raises:
        ValueError: if

            * the ``path`` is empty
            * there are an even number of elements
            * a collection ID in ``path`` is not a string
            * a document ID in ``path`` is not a string
        TypeError: If a keyword other than ``client`` is used.
    """

    def __init__(self, *path, **kwargs) -> None:
        super(AsyncCollectionReference, self).__init__(*path, **kwargs)

    def _query(self) -> async_query.AsyncQuery:
        """Query factory.

        Returns:
            :class:`~google.cloud.firestore_v1.query.Query`
        """
        return async_query.AsyncQuery(self)

    async def add(
        self,
        document_data: dict,
        document_id: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
    ) -> Tuple[Any, Any]:
        """Create a document in the Firestore database with the provided data.

        Args:
            document_data (dict): Property names and values to use for
                creating the document.
            document_id (Optional[str]): The document identifier within the
                current collection. If not provided, an ID will be
                automatically assigned by the server (the assigned ID will be
                a random 20 character string composed of digits,
                uppercase and lowercase letters).
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.  Defaults to a system-specified policy.
            timeout (float): The timeout for this request.  Defaults to a
                system-specified value.

        Returns:
            Tuple[:class:`google.protobuf.timestamp_pb2.Timestamp`, \
                :class:`~google.cloud.firestore_v1.async_document.AsyncDocumentReference`]:
                Pair of

                * The ``update_time`` when the document was created/overwritten.
                * A document reference for the created document.

        Raises:
            ~google.cloud.exceptions.Conflict: If ``document_id`` is provided
                and the document already exists.
        """
        document_ref, kwargs = self._prep_add(
            document_data, document_id, retry, timeout,
        )
        write_result = await document_ref.create(document_data, **kwargs)
        return write_result.update_time, document_ref

    async def list_documents(
        self,
        page_size: int = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
    ) -> AsyncGenerator[DocumentReference, None]:
        """List all subdocuments of the current collection.

        Args:
            page_size (Optional[int]]): The maximum number of documents
                in each page of results from this request. Non-positive values
                are ignored. Defaults to a sensible value set by the API.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.  Defaults to a system-specified policy.
            timeout (float): The timeout for this request.  Defaults to a
                system-specified value.

        Returns:
            Sequence[:class:`~google.cloud.firestore_v1.collection.DocumentReference`]:
                iterator of subdocuments of the current collection. If the
                collection does not exist at the time of `snapshot`, the
                iterator will be empty
        """
        request, kwargs = self._prep_list_documents(page_size, retry, timeout)

        iterator = await self._client._firestore_api.list_documents(
            request=request, metadata=self._client._rpc_metadata, **kwargs,
        )
        async for i in iterator:
            yield _item_to_document_ref(self, i)

    async def get(
        self,
        transaction: Transaction = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
    ) -> list:
        """Read the documents in this collection.

        This sends a ``RunQuery`` RPC and returns a list of documents
        returned in the stream of ``RunQueryResponse`` messages.

        Args:
            transaction
                (Optional[:class:`~google.cloud.firestore_v1.transaction.Transaction`]):
                An existing transaction that this query will run in.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.  Defaults to a system-specified policy.
            timeout (float): The timeout for this request.  Defaults to a
                system-specified value.

        If a ``transaction`` is used and it already has write operations
        added, this method cannot be used (i.e. read-after-write is not
        allowed).

        Returns:
            list: The documents in this collection that match the query.
        """
        query, kwargs = self._prep_get_or_stream(retry, timeout)

        return await query.get(transaction=transaction, **kwargs)

    async def stream(
        self,
        transaction: Transaction = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
    ) -> AsyncIterator[async_document.DocumentSnapshot]:
        """Read the documents in this collection.

        This sends a ``RunQuery`` RPC and then returns an iterator which
        consumes each document returned in the stream of ``RunQueryResponse``
        messages.

        .. note::

           The underlying stream of responses will time out after
           the ``max_rpc_timeout_millis`` value set in the GAPIC
           client configuration for the ``RunQuery`` API.  Snapshots
           not consumed from the iterator before that point will be lost.

        If a ``transaction`` is used and it already has write operations
        added, this method cannot be used (i.e. read-after-write is not
        allowed).

        Args:
            transaction (Optional[:class:`~google.cloud.firestore_v1.transaction.\
                Transaction`]):
                An existing transaction that the query will run in.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.  Defaults to a system-specified policy.
            timeout (float): The timeout for this request.  Defaults to a
                system-specified value.

        Yields:
            :class:`~google.cloud.firestore_v1.document.DocumentSnapshot`:
            The next document that fulfills the query.
        """
        query, kwargs = self._prep_get_or_stream(retry, timeout)

        async for d in query.stream(transaction=transaction, **kwargs):
            yield d  # pytype: disable=name-error
