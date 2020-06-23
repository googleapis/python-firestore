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
import warnings


from google.cloud.firestore_v1.collection import (
    CollectionReference,
    _auto_id,
    _item_to_document_ref,
)
from google.cloud.firestore_v1 import async_query
from google.cloud.firestore_v1.watch import Watch
from google.cloud.firestore_v1 import async_document


class AsyncCollectionReference(CollectionReference):
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

    def __init__(self, *path, **kwargs):
        super(AsyncCollectionReference, self).__init__(*path, **kwargs)

    async def add(self, document_data, document_id=None):
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
                :class:`~google.cloud.firestore_v1.async_document.AsyncDocumentReference`]:
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
        write_result = await document_ref.create(document_data)
        return write_result.update_time, document_ref

    async def list_documents(self, page_size=None):
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
            parent,
            self.id,
            page_size=page_size,
            show_missing=True,
            metadata=self._client._rpc_metadata,
        )
        iterator.collection = self
        iterator.item_to_value = _item_to_document_ref
        return iterator

    def select(self, field_paths):
        """Create a "select" query with this collection as parent.

        See
        :meth:`~google.cloud.firestore_v1.async_query.AsyncQuery.select` for
        more information on this method.

        Args:
            field_paths (Iterable[str, ...]): An iterable of field paths
                (``.``-delimited list of field names) to use as a projection
                of document fields in the query results.

        Returns:
            :class:`~google.cloud.firestore_v1.async_query.AsyncQuery`:
            A "projected" query.
        """
        query = async_query.AsyncQuery(self)
        return query.select(field_paths)

    def where(self, field_path, op_string, value):
        """Create a "where" query with this collection as parent.

        See
        :meth:`~google.cloud.firestore_v1.async_query.AsyncQuery.where` for
        more information on this method.

        Args:
            field_path (str): A field path (``.``-delimited list of
                field names) for the field to filter on.
            op_string (str): A comparison operation in the form of a string.
                Acceptable values are ``<``, ``<=``, ``==``, ``>=``
                and ``>``.
            value (Any): The value to compare the field against in the filter.
                If ``value`` is :data:`None` or a NaN, then ``==`` is the only
                allowed operation.

        Returns:
            :class:`~google.cloud.firestore_v1.async_query.AsyncQuery`:
            A filtered query.
        """
        query = async_query.AsyncQuery(self)
        return query.where(field_path, op_string, value)

    def order_by(self, field_path, **kwargs):
        """Create an "order by" query with this collection as parent.

        See
        :meth:`~google.cloud.firestore_v1.async_query.AsyncQuery.order_by` for
        more information on this method.

        Args:
            field_path (str): A field path (``.``-delimited list of
                field names) on which to order the query results.
            kwargs (Dict[str, Any]): The keyword arguments to pass along
                to the query. The only supported keyword is ``direction``,
                see :meth:`~google.cloud.firestore_v1.async_query.AsyncQuery.order_by`
                for more information.

        Returns:
            :class:`~google.cloud.firestore_v1.async_query.AsyncQuery`:
            An "order by" query.
        """
        query = async_query.AsyncQuery(self)
        return query.order_by(field_path, **kwargs)

    def limit(self, count):
        """Create a limited query with this collection as parent.

        See
        :meth:`~google.cloud.firestore_v1.async_query.AsyncQuery.limit` for
        more information on this method.

        Args:
            count (int): Maximum number of documents to return that match
                the query.

        Returns:
            :class:`~google.cloud.firestore_v1.async_query.AsyncQuery`:
            A limited query.
        """
        query = async_query.AsyncQuery(self)
        return query.limit(count)

    def offset(self, num_to_skip):
        """Skip to an offset in a query with this collection as parent.

        See
        :meth:`~google.cloud.firestore_v1.async_query.AsyncQuery.offset` for
        more information on this method.

        Args:
            num_to_skip (int): The number of results to skip at the beginning
                of query results. (Must be non-negative.)

        Returns:
            :class:`~google.cloud.firestore_v1.async_query.AsyncQuery`:
            An offset query.
        """
        query = async_query.AsyncQuery(self)
        return query.offset(num_to_skip)

    def start_at(self, document_fields):
        """Start query at a cursor with this collection as parent.

        See
        :meth:`~google.cloud.firestore_v1.async_query.AsyncQuery.start_at` for
        more information on this method.

        Args:
            document_fields (Union[:class:`~google.cloud.firestore_v1.\
                document.DocumentSnapshot`, dict, list, tuple]):
                A document snapshot or a dictionary/list/tuple of fields
                representing a query results cursor. A cursor is a collection
                of values that represent a position in a query result set.

        Returns:
            :class:`~google.cloud.firestore_v1.async_query.AsyncQuery`:
            A query with cursor.
        """
        query = async_query.AsyncQuery(self)
        return query.start_at(document_fields)

    def start_after(self, document_fields):
        """Start query after a cursor with this collection as parent.

        See
        :meth:`~google.cloud.firestore_v1.async_query.AsyncQuery.start_after` for
        more information on this method.

        Args:
            document_fields (Union[:class:`~google.cloud.firestore_v1.\
                document.DocumentSnapshot`, dict, list, tuple]):
                A document snapshot or a dictionary/list/tuple of fields
                representing a query results cursor. A cursor is a collection
                of values that represent a position in a query result set.

        Returns:
            :class:`~google.cloud.firestore_v1.async_query.AsyncQuery`:
            A query with cursor.
        """
        query = async_query.AsyncQuery(self)
        return query.start_after(document_fields)

    def end_before(self, document_fields):
        """End query before a cursor with this collection as parent.

        See
        :meth:`~google.cloud.firestore_v1.async_query.AsyncQuery.end_before` for
        more information on this method.

        Args:
            document_fields (Union[:class:`~google.cloud.firestore_v1.\
                document.DocumentSnapshot`, dict, list, tuple]):
                A document snapshot or a dictionary/list/tuple of fields
                representing a query results cursor. A cursor is a collection
                of values that represent a position in a query result set.

        Returns:
            :class:`~google.cloud.firestore_v1.async_query.AsyncQuery`:
            A query with cursor.
        """
        query = async_query.AsyncQuery(self)
        return query.end_before(document_fields)

    def end_at(self, document_fields):
        """End query at a cursor with this collection as parent.

        See
        :meth:`~google.cloud.firestore_v1.async_query.AsyncQuery.end_at` for
        more information on this method.

        Args:
            document_fields (Union[:class:`~google.cloud.firestore_v1.\
                document.DocumentSnapshot`, dict, list, tuple]):
                A document snapshot or a dictionary/list/tuple of fields
                representing a query results cursor. A cursor is a collection
                of values that represent a position in a query result set.

        Returns:
            :class:`~google.cloud.firestore_v1.async_query.AsyncQuery`:
            A query with cursor.
        """
        query = async_query.AsyncQuery(self)
        return query.end_at(document_fields)

    async def get(self, transaction=None):
        """Deprecated alias for :meth:`stream`."""
        warnings.warn(
            "'Collection.get' is deprecated:  please use 'Collection.stream' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        async for d in self.stream(transaction=transaction):
            yield d

    async def stream(self, transaction=None):
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
        query = async_query.AsyncQuery(self)
        async for d in query.stream(transaction=transaction):
            yield d

    def on_snapshot(self, callback):
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
            async_query.AsyncQuery(self),
            callback,
            async_document.DocumentSnapshot,
            async_document.AsyncDocumentReference,
        )
