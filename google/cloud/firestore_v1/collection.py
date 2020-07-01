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
import random

import six

from google.cloud.firestore_v1 import _helpers
from google.cloud.firestore_v1 import query as query_mod
from google.cloud.firestore_v1.watch import Watch
from google.cloud.firestore_v1 import document

_AUTO_ID_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


class CollectionReference(object):
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
        _helpers.verify_path(path, is_collection=True)
        self._path = path
        self._client = kwargs.pop("client", None)
        if kwargs:
            raise TypeError(
                "Received unexpected arguments", kwargs, "Only `client` is supported"
            )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._path == other._path and self._client == other._client

    @property
    def id(self):
        """The collection identifier.

        Returns:
            str: The last component of the path.
        """
        return self._path[-1]

    @property
    def parent(self):
        """Document that owns the current collection.

        Returns:
            Optional[:class:`~google.cloud.firestore_v1.document.DocumentReference`]:
            The parent document, if the current collection is not a
            top-level collection.
        """
        if len(self._path) == 1:
            return None
        else:
            parent_path = self._path[:-1]
        return self._client.document(*parent_path)

    def document(self, document_id=None):
        """Create a sub-document underneath the current collection.

        Args:
            document_id (Optional[str]): The document identifier
                within the current collection. If not provided, will default
                to a random 20 character string composed of digits,
                uppercase and lowercase and letters.

        Returns:
            :class:`~google.cloud.firestore_v1.document.DocumentReference`:
            The child document.
        """
        if document_id is None:
            document_id = _auto_id()

        child_path = self._path + (document_id,)
        return self._client.document(*child_path)

    def _parent_info(self):
        """Get fully-qualified parent path and prefix for this collection.

        Returns:
            Tuple[str, str]: Pair of

            * the fully-qualified (with database and project) path to the
              parent of this collection (will either be the database path
              or a document path).
            * the prefix to a document in this collection.
        """
        parent_doc = self.parent
        if parent_doc is None:
            parent_path = _helpers.DOCUMENT_PATH_DELIMITER.join(
                (self._client._database_string, "documents")
            )
        else:
            parent_path = parent_doc._document_path

        expected_prefix = _helpers.DOCUMENT_PATH_DELIMITER.join((parent_path, self.id))
        return parent_path, expected_prefix

    def add(self, document_data, document_id=None):
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

    def list_documents(self, page_size=None):
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
        :meth:`~google.cloud.firestore_v1.query.Query.select` for
        more information on this method.

        Args:
            field_paths (Iterable[str, ...]): An iterable of field paths
                (``.``-delimited list of field names) to use as a projection
                of document fields in the query results.

        Returns:
            :class:`~google.cloud.firestore_v1.query.Query`:
            A "projected" query.
        """
        query = query_mod.Query(self)
        return query.select(field_paths)

    def where(self, field_path, op_string, value):
        """Create a "where" query with this collection as parent.

        See
        :meth:`~google.cloud.firestore_v1.query.Query.where` for
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
            :class:`~google.cloud.firestore_v1.query.Query`:
            A filtered query.
        """
        query = query_mod.Query(self)
        return query.where(field_path, op_string, value)

    def order_by(self, field_path, **kwargs):
        """Create an "order by" query with this collection as parent.

        See
        :meth:`~google.cloud.firestore_v1.query.Query.order_by` for
        more information on this method.

        Args:
            field_path (str): A field path (``.``-delimited list of
                field names) on which to order the query results.
            kwargs (Dict[str, Any]): The keyword arguments to pass along
                to the query. The only supported keyword is ``direction``,
                see :meth:`~google.cloud.firestore_v1.query.Query.order_by`
                for more information.

        Returns:
            :class:`~google.cloud.firestore_v1.query.Query`:
            An "order by" query.
        """
        query = query_mod.Query(self)
        return query.order_by(field_path, **kwargs)

    def limit(self, count):
        """Create a limited query with this collection as parent.

        .. note::

           `limit` and `limit_to_last` are mutually exclusive.
           Setting `limit` will drop previously set `limit_to_last`.

        See
        :meth:`~google.cloud.firestore_v1.query.Query.limit` for
        more information on this method.

        Args:
            count (int): Maximum number of documents to return that match
                the query.

        Returns:
            :class:`~google.cloud.firestore_v1.query.Query`:
            A limited query.
        """
        query = query_mod.Query(self)
        return query.limit(count)

    def limit_to_last(self, count):
        """Create a limited to last query with this collection as parent.

        .. note::

           `limit` and `limit_to_last` are mutually exclusive.
           Setting `limit_to_last` will drop previously set `limit`.

        See
        :meth:`~google.cloud.firestore_v1.query.Query.limit_to_last`
        for more information on this method.

        Args:
            count (int): Maximum number of documents to return that
                match the query.

        Returns:
            :class:`~google.cloud.firestore_v1.query.Query`:
            A limited to last query.
        """
        query = query_mod.Query(self)
        return query.limit_to_last(count)

    def offset(self, num_to_skip):
        """Skip to an offset in a query with this collection as parent.

        See
        :meth:`~google.cloud.firestore_v1.query.Query.offset` for
        more information on this method.

        Args:
            num_to_skip (int): The number of results to skip at the beginning
                of query results. (Must be non-negative.)

        Returns:
            :class:`~google.cloud.firestore_v1.query.Query`:
            An offset query.
        """
        query = query_mod.Query(self)
        return query.offset(num_to_skip)

    def start_at(self, document_fields):
        """Start query at a cursor with this collection as parent.

        See
        :meth:`~google.cloud.firestore_v1.query.Query.start_at` for
        more information on this method.

        Args:
            document_fields (Union[:class:`~google.cloud.firestore_v1.\
                document.DocumentSnapshot`, dict, list, tuple]):
                A document snapshot or a dictionary/list/tuple of fields
                representing a query results cursor. A cursor is a collection
                of values that represent a position in a query result set.

        Returns:
            :class:`~google.cloud.firestore_v1.query.Query`:
            A query with cursor.
        """
        query = query_mod.Query(self)
        return query.start_at(document_fields)

    def start_after(self, document_fields):
        """Start query after a cursor with this collection as parent.

        See
        :meth:`~google.cloud.firestore_v1.query.Query.start_after` for
        more information on this method.

        Args:
            document_fields (Union[:class:`~google.cloud.firestore_v1.\
                document.DocumentSnapshot`, dict, list, tuple]):
                A document snapshot or a dictionary/list/tuple of fields
                representing a query results cursor. A cursor is a collection
                of values that represent a position in a query result set.

        Returns:
            :class:`~google.cloud.firestore_v1.query.Query`:
            A query with cursor.
        """
        query = query_mod.Query(self)
        return query.start_after(document_fields)

    def end_before(self, document_fields):
        """End query before a cursor with this collection as parent.

        See
        :meth:`~google.cloud.firestore_v1.query.Query.end_before` for
        more information on this method.

        Args:
            document_fields (Union[:class:`~google.cloud.firestore_v1.\
                document.DocumentSnapshot`, dict, list, tuple]):
                A document snapshot or a dictionary/list/tuple of fields
                representing a query results cursor. A cursor is a collection
                of values that represent a position in a query result set.

        Returns:
            :class:`~google.cloud.firestore_v1.query.Query`:
            A query with cursor.
        """
        query = query_mod.Query(self)
        return query.end_before(document_fields)

    def end_at(self, document_fields):
        """End query at a cursor with this collection as parent.

        See
        :meth:`~google.cloud.firestore_v1.query.Query.end_at` for
        more information on this method.

        Args:
            document_fields (Union[:class:`~google.cloud.firestore_v1.\
                document.DocumentSnapshot`, dict, list, tuple]):
                A document snapshot or a dictionary/list/tuple of fields
                representing a query results cursor. A cursor is a collection
                of values that represent a position in a query result set.

        Returns:
            :class:`~google.cloud.firestore_v1.query.Query`:
            A query with cursor.
        """
        query = query_mod.Query(self)
        return query.end_at(document_fields)

    def get(self, transaction=None):
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

    def stream(self, transaction=None):
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
            query_mod.Query(self),
            callback,
            document.DocumentSnapshot,
            document.DocumentReference,
        )


def _auto_id():
    """Generate a "random" automatically generated ID.

    Returns:
        str: A 20 character string composed of digits, uppercase and
        lowercase and letters.
    """
    return "".join(random.choice(_AUTO_ID_CHARS) for _ in six.moves.xrange(20))


def _item_to_document_ref(iterator, item):
    """Convert Document resource to document ref.

    Args:
        iterator (google.api_core.page_iterator.GRPCIterator):
            iterator response
        item (dict): document resource
    """
    document_id = item.name.split(_helpers.DOCUMENT_PATH_DELIMITER)[-1]
    return iterator.collection.document(document_id)
