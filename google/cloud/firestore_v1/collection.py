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

"""Classes for representing collections for the Google Cloud Firestore API."""
from google.cloud.firestore_v1.base_collection import (
    BaseCollectionReference,
    _auto_id,
    _item_to_document_ref,
)
from google.cloud.firestore_v1 import query as query_mod
from google.cloud.firestore_v1.watch import Watch
from google.cloud.firestore_v1 import document
from typing import Any, Generator, Tuple


class CollectionReference(BaseCollectionReference):
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
        super(CollectionReference, self).__init__(*path, **kwargs)

    def _query(self) -> query_mod.Query:
        """Query factory.

        Returns:
            :class:`~google.cloud.firestore_v1.query.Query`
        """
        return query_mod.Query(self)

    def add(self, document_data, document_id=None) -> Tuple[Any, Any]:
        """Create a document in the Firestore database with the provided data.

        Args:
            document_data (dict): Property names and values to use for
                creating the document.
            document_id (Optional[str]): The document identifier within the
                current collection. If not provided, an ID will be
                automatically assigned by the server (the assigned ID will be
                a random 20 character string composed of digits,
                uppercase and lowercase letters).

        Returns:
            Tuple[:class:`google.protobuf.timestamp_pb2.Timestamp`, \
                :class:`~google.cloud.firestore_v1.document.DocumentReference`]:
                Pair of

                * The ``update_time`` when the document was created/overwritten.
                * A document reference for the created document.

        Raises:
            ~google.cloud.exceptions.Conflict: If ``document_id`` is provided
                and the document already exists.
        """
        if document_id is None:
            document_id = _auto_id()

        document_ref = self.document(document_id)
        write_result = document_ref.create(document_data)
        return write_result.update_time, document_ref

    def list_documents(self, page_size=None) -> Generator[Any, Any, None]:
        """List all subdocuments of the current collection.

        Args:
            page_size (Optional[int]]): The maximum number of documents
            in each page of results from this request. Non-positive values
            are ignored. Defaults to a sensible value set by the API.

        Returns:
            Sequence[:class:`~google.cloud.firestore_v1.collection.DocumentReference`]:
                iterator of subdocuments of the current collection. If the
                collection does not exist at the time of `snapshot`, the
                iterator will be empty
        """
        parent, _ = self._parent_info()

        iterator = self._client._firestore_api.list_documents(
            request={
                "parent": parent,
                "collection_id": self.id,
                "page_size": page_size,
                "show_missing": True,
            },
            metadata=self._client._rpc_metadata,
        )
        return (_item_to_document_ref(self, i) for i in iterator)

    def get(self, transaction=None) -> list:
        """Read the documents in this collection.

        This sends a ``RunQuery`` RPC and returns a list of documents
        returned in the stream of ``RunQueryResponse`` messages.

        Args:
            transaction
                (Optional[:class:`~google.cloud.firestore_v1.transaction.Transaction`]):
                An existing transaction that this query will run in.

        If a ``transaction`` is used and it already has write operations
        added, this method cannot be used (i.e. read-after-write is not
        allowed).

        Returns:
            list: The documents in this collection that match the query.
        """
        query = query_mod.Query(self)
        return query.get(transaction=transaction)

    def stream(
        self, transaction=None
    ) -> Generator[document.DocumentSnapshot, Any, None]:
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

        Yields:
            :class:`~google.cloud.firestore_v1.document.DocumentSnapshot`:
            The next document that fulfills the query.
        """
        query = query_mod.Query(self)
        return query.stream(transaction=transaction)

    def on_snapshot(self, callback) -> Watch:
        """Monitor the documents in this collection.

        This starts a watch on this collection using a background thread. The
        provided callback is run on the snapshot of the documents.

        Args:
            callback (Callable[[:class:`~google.cloud.firestore.collection.CollectionSnapshot`], NoneType]):
                a callback to run when a change occurs.

        Example:
            from google.cloud import firestore_v1

            db = firestore_v1.Client()
            collection_ref = db.collection(u'users')

            def on_snapshot(collection_snapshot, changes, read_time):
                for doc in collection_snapshot.documents:
                    print(u'{} => {}'.format(doc.id, doc.to_dict()))

            # Watch this collection
            collection_watch = collection_ref.on_snapshot(on_snapshot)

            # Terminate this watch
            collection_watch.unsubscribe()
        """
        return Watch.for_query(
            self._query(),
            callback,
            document.DocumentSnapshot,
            document.DocumentReference,
        )
