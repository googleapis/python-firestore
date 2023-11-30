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

"""Classes for representing queries for the Google Cloud Firestore API.

A :class:`~google.cloud.firestore_v1.query.Query` can be created directly from
a :class:`~google.cloud.firestore_v1.collection.Collection` and that can be
a more common way to create a query than direct usage of the constructor.
"""
from __future__ import annotations

from google.cloud import firestore_v1
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.api_core import exceptions
from google.api_core import gapic_v1
from google.api_core import retry as retries

from google.cloud.firestore_v1.base_query import (
    BaseCollectionGroup,
    BaseQuery,
    QueryPartition,
    _query_response_to_snapshot,
    _collection_group_query_response_to_snapshot,
    _enum_from_direction,
)
from google.cloud.firestore_v1 import aggregation

from google.cloud.firestore_v1 import document
from google.cloud.firestore_v1.watch import Watch
from typing import Any, Callable, Generator, List, Optional, Type, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: NO COVER
    from google.cloud.firestore_v1.field_path import FieldPath


class Query(BaseQuery):
    """Represents a query to the Firestore API.

    Instances of this class are considered immutable: all methods that
    would modify an instance instead return a new instance.

    Args:
        parent (:class:`~google.cloud.firestore_v1.collection.CollectionReference`):
            The collection that this query applies to.
        projection (Optional[:class:`google.cloud.proto.firestore.v1.\
            query.StructuredQuery.Projection`]):
            A projection of document fields to limit the query results to.
        field_filters (Optional[Tuple[:class:`google.cloud.proto.firestore.v1.\
            query.StructuredQuery.FieldFilter`, ...]]):
            The filters to be applied in the query.
        orders (Optional[Tuple[:class:`google.cloud.proto.firestore.v1.\
            query.StructuredQuery.Order`, ...]]):
            The "order by" entries to use in the query.
        limit (Optional[int]):
            The maximum number of documents the query is allowed to return.
        offset (Optional[int]):
            The number of results to skip.
        start_at (Optional[Tuple[dict, bool]]):
            Two-tuple of :

            * a mapping of fields. Any field that is present in this mapping
              must also be present in ``orders``
            * an ``after`` flag

            The fields and the flag combine to form a cursor used as
            a starting point in a query result set. If the ``after``
            flag is :data:`True`, the results will start just after any
            documents which have fields matching the cursor, otherwise
            any matching documents will be included in the result set.
            When the query is formed, the document values
            will be used in the order given by ``orders``.
        end_at (Optional[Tuple[dict, bool]]):
            Two-tuple of:

            * a mapping of fields. Any field that is present in this mapping
              must also be present in ``orders``
            * a ``before`` flag

            The fields and the flag combine to form a cursor used as
            an ending point in a query result set. If the ``before``
            flag is :data:`True`, the results will end just before any
            documents which have fields matching the cursor, otherwise
            any matching documents will be included in the result set.
            When the query is formed, the document values
            will be used in the order given by ``orders``.
        all_descendants (Optional[bool]):
            When false, selects only collections that are immediate children
            of the `parent` specified in the containing `RunQueryRequest`.
            When true, selects all descendant collections.
    """

    def __init__(
        self,
        parent,
        projection=None,
        field_filters=(),
        orders=(),
        limit=None,
        limit_to_last=False,
        offset=None,
        start_at=None,
        end_at=None,
        all_descendants=False,
        recursive=False,
    ) -> None:
        super(Query, self).__init__(
            parent=parent,
            projection=projection,
            field_filters=field_filters,
            orders=orders,
            limit=limit,
            limit_to_last=limit_to_last,
            offset=offset,
            start_at=start_at,
            end_at=end_at,
            all_descendants=all_descendants,
            recursive=recursive,
        )

    def get(
        self,
        transaction=None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
    ) -> List[DocumentSnapshot]:
        """Read the documents in the collection that match this query.

        This sends a ``RunQuery`` RPC and returns a list of documents
        returned in the stream of ``RunQueryResponse`` messages.

        Args:
            transaction
                (Optional[:class:`~google.cloud.firestore_v1.transaction.Transaction`]):
                An existing transaction that this query will run in.
                If a ``transaction`` is used and it already has write operations
                added, this method cannot be used (i.e. read-after-write is not
                allowed).
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.  Defaults to a system-specified policy.
            timeout (float): The timeout for this request.  Defaults to a
                system-specified value.

        Returns:
            list: The documents in the collection that match this query.
        """
        is_limited_to_last = self._limit_to_last

        if self._limit_to_last:
            # In order to fetch up to `self._limit` results from the end of the
            # query flip the defined ordering on the query to start from the
            # end, retrieving up to `self._limit` results from the backend.
            for order in self._orders:
                order.direction = _enum_from_direction(
                    self.DESCENDING
                    if order.direction.name == self.ASCENDING
                    else self.ASCENDING
                )
            self._limit_to_last = False

        result = self.stream(transaction=transaction, retry=retry, timeout=timeout)
        if is_limited_to_last:
            result = reversed(list(result))

        return list(result)

    def _chunkify(
        self, chunk_size: int
    ) -> Generator[List[DocumentSnapshot], None, None]:
        max_to_return: Optional[int] = self._limit
        num_returned: int = 0
        original: Query = self._copy()
        last_document: Optional[DocumentSnapshot] = None

        while True:
            # Optionally trim the `chunk_size` down to honor a previously
            # applied limits as set by `self.limit()`
            _chunk_size: int = original._resolve_chunk_size(num_returned, chunk_size)

            # Apply the optionally pruned limit and the cursor, if we are past
            # the first page.
            _q = original.limit(_chunk_size)

            if last_document:
                _q = _q.start_after(last_document)

            snapshots = _q.get()

            if snapshots:
                last_document = snapshots[-1]

            num_returned += len(snapshots)

            yield snapshots

            # Terminate the iterator if we have reached either of two end
            # conditions:
            #   1. There are no more documents, or
            #   2. We have reached the desired overall limit
            if len(snapshots) < _chunk_size or (
                max_to_return and num_returned >= max_to_return
            ):
                return

    def _get_stream_iterator(self, transaction, retry, timeout):
        """Helper method for :meth:`stream`."""
        request, expected_prefix, kwargs = self._prep_stream(
            transaction,
            retry,
            timeout,
        )

        response_iterator = self._client._firestore_api.run_query(
            request=request,
            metadata=self._client._rpc_metadata,
            **kwargs,
        )

        return response_iterator, expected_prefix

    def _retry_query_after_exception(self, exc, retry, transaction):
        """Helper method for :meth:`stream`."""
        if transaction is None:  # no snapshot-based retry inside transaction
            if retry is gapic_v1.method.DEFAULT:
                transport = self._client._firestore_api._transport
                gapic_callable = transport.run_query
                retry = gapic_callable._retry
            return retry._predicate(exc)

        return False

    def count(
        self, alias: str | None = None
    ) -> Type["firestore_v1.aggregation.AggregationQuery"]:
        """
        Adds a count over the query.

        :type alias: Optional[str]
        :param alias: Optional name of the field to store the result of the aggregation into.
            If not provided, Firestore will pick a default name following the format field_<incremental_id++>.
        """
        return aggregation.AggregationQuery(self).count(alias=alias)

    def sum(
        self, field_ref: str | FieldPath, alias: str | None = None
    ) -> Type["firestore_v1.aggregation.AggregationQuery"]:
        """
        Adds a sum over the query.

        :type field_ref: Union[str, google.cloud.firestore_v1.field_path.FieldPath]
        :param field_ref: The field to aggregate across.

        :type alias: Optional[str]
        :param alias: Optional name of the field to store the result of the aggregation into.
            If not provided, Firestore will pick a default name following the format field_<incremental_id++>.
        """
        return aggregation.AggregationQuery(self).sum(field_ref, alias=alias)

    def avg(
        self, field_ref: str | FieldPath, alias: str | None = None
    ) -> Type["firestore_v1.aggregation.AggregationQuery"]:
        """
        Adds an avg over the query.

        :type field_ref: [Union[str, google.cloud.firestore_v1.field_path.FieldPath]
        :param field_ref: The field to aggregate across.

        :type alias: Optional[str]
        :param alias: Optional name of the field to store the result of the aggregation into.
            If not provided, Firestore will pick a default name following the format field_<incremental_id++>.
        """
        return aggregation.AggregationQuery(self).avg(field_ref, alias=alias)

    def stream(
        self,
        transaction=None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
    ) -> Generator[document.DocumentSnapshot, Any, None]:
        """Read the documents in the collection that match this query.

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
            transaction
                (Optional[:class:`~google.cloud.firestore_v1.transaction.Transaction`]):
                An existing transaction that this query will run in.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.  Defaults to a system-specified policy.
            timeout (float): The timeout for this request.  Defaults to a
                system-specified value.

        Yields:
            :class:`~google.cloud.firestore_v1.document.DocumentSnapshot`:
            The next document that fulfills the query.
        """
        response_iterator, expected_prefix = self._get_stream_iterator(
            transaction,
            retry,
            timeout,
        )

        last_snapshot = None

        while True:
            try:
                response = next(response_iterator, None)
            except exceptions.GoogleAPICallError as exc:
                if self._retry_query_after_exception(exc, retry, transaction):
                    new_query = self.start_after(last_snapshot)
                    response_iterator, _ = new_query._get_stream_iterator(
                        transaction,
                        retry,
                        timeout,
                    )
                    continue
                else:
                    raise

            if response is None:  # EOI
                break

            if self._all_descendants:
                snapshot = _collection_group_query_response_to_snapshot(
                    response, self._parent
                )
            else:
                snapshot = _query_response_to_snapshot(
                    response, self._parent, expected_prefix
                )
            if snapshot is not None:
                last_snapshot = snapshot
                yield snapshot

    def on_snapshot(self, callback: Callable) -> Watch:
        """Monitor the documents in this collection that match this query.

        This starts a watch on this query using a background thread. The
        provided callback is run on the snapshot of the documents.

        Args:
            callback(Callable[[:class:`~google.cloud.firestore.query.QuerySnapshot`], NoneType]):
                a callback to run when a change occurs.

        Example:

        .. code-block:: python

            from google.cloud import firestore_v1

            db = firestore_v1.Client()
            query_ref = db.collection(u'users').where("user", "==", u'Ada')

            def on_snapshot(docs, changes, read_time):
                for doc in docs:
                    print(u'{} => {}'.format(doc.id, doc.to_dict()))

            # Watch this query
            query_watch = query_ref.on_snapshot(on_snapshot)

            # Terminate this watch
            query_watch.unsubscribe()
        """
        return Watch.for_query(self, callback, document.DocumentSnapshot)

    @staticmethod
    def _get_collection_reference_class() -> (
        Type["firestore_v1.collection.CollectionReference"]
    ):
        from google.cloud.firestore_v1.collection import CollectionReference

        return CollectionReference


class CollectionGroup(Query, BaseCollectionGroup):
    """Represents a Collection Group in the Firestore API.

    This is a specialization of :class:`.Query` that includes all documents in the
    database that are contained in a collection or subcollection of the given
    parent.

    Args:
        parent (:class:`~google.cloud.firestore_v1.collection.CollectionReference`):
            The collection that this query applies to.
    """

    def __init__(
        self,
        parent,
        projection=None,
        field_filters=(),
        orders=(),
        limit=None,
        limit_to_last=False,
        offset=None,
        start_at=None,
        end_at=None,
        all_descendants=True,
        recursive=False,
    ) -> None:
        super(CollectionGroup, self).__init__(
            parent=parent,
            projection=projection,
            field_filters=field_filters,
            orders=orders,
            limit=limit,
            limit_to_last=limit_to_last,
            offset=offset,
            start_at=start_at,
            end_at=end_at,
            all_descendants=all_descendants,
            recursive=recursive,
        )

    @staticmethod
    def _get_query_class():
        return Query

    def get_partitions(
        self,
        partition_count,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
    ) -> Generator[QueryPartition, None, None]:
        """Partition a query for parallelization.

        Partitions a query by returning partition cursors that can be used to run the
        query in parallel. The returned partition cursors are split points that can be
        used as starting/end points for the query results.

        Args:
            partition_count (int): The desired maximum number of partition points. The
                number must be strictly positive. The actual number of partitions
                returned may be fewer.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.  Defaults to a system-specified policy.
            timeout (float): The timeout for this request.  Defaults to a
                system-specified value.
        """
        request, kwargs = self._prep_get_partitions(partition_count, retry, timeout)

        pager = self._client._firestore_api.partition_query(
            request=request,
            metadata=self._client._rpc_metadata,
            **kwargs,
        )

        start_at = None
        for cursor_pb in pager:
            cursor = self._client.document(cursor_pb.values[0].reference_value)
            yield QueryPartition(self, start_at, cursor)
            start_at = cursor

        yield QueryPartition(self, start_at, None)
