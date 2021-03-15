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

"""Classes for representing bundles for the Google Cloud Firestore API."""

import datetime
import json

from google.cloud.firestore_bundle.types.bundle import (
    BundledDocumentMetadata,
    BundledQuery,
    BundleElement,
    BundleMetadata,
    NamedQuery,
)
from google.cloud._helpers import _datetime_to_pb_timestamp, UTC  # type: ignore
from google.cloud.firestore_bundle._helpers import limit_type_of_query
from google.cloud.firestore_v1.async_query import AsyncQuery
from google.cloud.firestore_v1.base_client import BaseClient
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.base_query import BaseQuery
from google.cloud.firestore_v1.document import DocumentReference
from google.cloud.firestore_v1.query import Query
from google.cloud.firestore_v1 import _helpers
from google.protobuf.timestamp_pb2 import Timestamp  # type: ignore
from typing import (
    Dict,
    Iterable,
    List,
    Optional,
    Union,
)


class FirestoreBundle:
    """A group of serialized documents and queries, suitable for
    longterm storage.

    If any queries are added to this bundle, all associated documents will be
    loaded and stored in memory for serialization.

    Usage:

        from google.cloud.firestore import Client
        from google.cloud.firestore_bundle.bundle import FirestoreBundle
        from google.cloud.firestore import _helpers

        db = Client()
        bundle = FirestoreBundle('my-bundle')
        bundle.add('all-users', db.collection('users')._query())
        bundle.add(
            'top-ten-hamburgers',
            db.collection('hamburgers').limit(limit=10)._query(),
        )
        serialized: str = bundle.build()

        # Store somewhere like your GCS or your device's file system

        # Some time later after loading `serialized` again
        bundle = _helpers.deserialize_bundle(serialized)

        users: Iterable[DocumentSnapshot] = bundle.get_documents(
            query_name='all-users',
        )

    Args:
        name (str): The Id of the bundle.
    """

    BUNDLE_SCHEMA_VERSION: int = 1

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.documents: Dict[str, "_BundledDocument"] = {}
        self.named_queries: Dict[str, NamedQuery] = {}
        self.latest_read_time: Timestamp = Timestamp(seconds=0, nanos=0)
        self._deserialized_metadata: Optional[BundledDocumentMetadata] = None

    def add(
        self,
        document_or_query_name: Union[DocumentSnapshot, str],
        query: Optional[Query] = None,
    ) -> "FirestoreBundle":
        """Adds a document or entire query to the bundle.

        This function is offered for convenience / API parity with other SDKs.
        Most users will get better outcomes from using the more specific,
        `add_document` or `add_named_query` methods.

        Args:
            document_or_query_name (Union[DocumentSnapshot, str]): If supplied
                as a `DocumentSnapshot`, this parameter routes control flow to
                `add_document`, and the second parameter must be None. However,
                if supplied as a `str`, then this parameter routes control flow
                to `add_named_query`, and the second parameter must be supplied.
            query_snapshot (Optional[Query]): Query to fully load and save to
                the bundle. This parameter is required if the first parameter is
                a string, and is required to be `None` if the first parameter
                is a `DocumentSnapshot`.

        Example:

            from google.cloud import firestore

            db = firestore.Client()
            collection_ref = db.collection(u'users')

            bundle = firestore.FirestoreBundle('my-bundle')

            # Add an entire query. This will load and save every matching
            # document.
            bundle.add('all the users', collection_ref._query())

            # Add a single document.
            bundle.add(collection_ref.documents('some_id').get())

        Returns:
            FirestoreBundle: self

        """
        if isinstance(document_or_query_name, DocumentSnapshot):
            assert query is None
            self.add_document(document_or_query_name)
        elif isinstance(document_or_query_name, str):
            assert query is not None
            self.add_named_query(document_or_query_name, query)
        else:
            raise ValueError(
                "Bundle.add accepts either a standalone DocumentSnapshot or "
                "a name (string) and a Query."
            )
        return self

    def add_document(
        self, snapshot: DocumentSnapshot, query_name: Optional[str] = None,
    ) -> "FirestoreBundle":
        """Adds a document to the bundle.

        Args:
            snapshot (DocumentSnapshot): The fully-loaded Firestore document to
                be preserved.
            query_name (Optional[str]): If provided, also establishes a link
                between the provided document and the referenced query.

        Example:

            from google.cloud import firestore

            db = firestore.Client()
            collection_ref = db.collection(u'users')

            bundle = firestore.FirestoreBundle('my bundle')
            bundle.add_document(collection_ref.documents('some_id').get())

        Returns:
            FirestoreBundle: self
        """
        original_document: Optional[_BundledDocument]
        original_queries: Optional[List[str]] = []
        full_document_path: str = snapshot.reference._document_path

        original_document = self.documents.get(full_document_path)
        if original_document:
            original_queries = original_document.metadata.queries  # type: ignore

        should_use_snaphot: bool = (
            original_document is None
            # equivalent to:
            #   `if snapshot.read_time > original_document.snapshot.read_time`
            or _helpers.compare_timestamps(
                snapshot.read_time, original_document.snapshot.read_time,
            )
            >= 0
        )

        if should_use_snaphot:
            self.documents[full_document_path] = _BundledDocument(
                snapshot=snapshot,
                metadata=BundledDocumentMetadata(
                    name=full_document_path,
                    read_time=snapshot.read_time,
                    exists=snapshot.exists,
                    queries=original_queries,
                ),
            )

        if query_name:
            bundled_document = self.documents.get(full_document_path)
            bundled_document.metadata.queries.append(query_name)  # type: ignore

        self._update_last_read_time(snapshot.read_time)
        # Flush this if it was cached
        self._deserialized_metadata = None
        return self

    def add_named_query(self, name: str, query: BaseQuery) -> "FirestoreBundle":
        """Adds a query to the bundle, referenced by the provided name.

        Args:
            name (str): The name by which the provided query should be referenced.
            query (Query): Query of documents to be fully loaded and stored in
                the bundle for future access.

        Example:

            from google.cloud import firestore

            db = firestore.Client()
            collection_ref = db.collection(u'users')

            bundle = firestore.FirestoreBundle('my bundle')
            bundle.add_named_query('all the users', collection_ref._query())

        Returns:
            FirestoreBundle: self

        Raises:
            ValueError: If anything other than a BaseQuery (e.g., a Collection)
                is supplied. If you have a Collection, call its `_query()`
                method to get what this method expects.
            ValueError: If the supplied name has already been added.
        """
        if not isinstance(query, BaseQuery):
            raise ValueError(
                "Attempted to add named query of type: "
                f"{type(query).__name__}. Expected BaseQuery.",
            )

        if self.named_queries.get(name):
            raise ValueError(f"Query name conflict: {name} has already been added.")

        # Execute the query and save each resulting document
        _read_time = self._save_documents_from_query(name, query)

        # Actually save the query to our local object cache
        self._save_named_query(name, query, _read_time)
        # Flush this if it was cached
        self._deserialized_metadata = None
        return self

    def _save_documents_from_query(self, name, query: BaseQuery) -> datetime.datetime:
        _read_time = datetime.datetime.min.replace(tzinfo=UTC)
        if isinstance(query, AsyncQuery):
            import asyncio

            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._process_async_query(name, query))

        # `query` is now known to be a non-async `BaseQuery`
        doc: DocumentSnapshot
        for doc in query.stream():  # type: ignore
            self.add_document(doc, query_name=name)
            _read_time = doc.read_time
        return _read_time

    def _save_named_query(
        self, name: str, query: BaseQuery, read_time: datetime.datetime,
    ) -> None:
        self.named_queries[name] = self._build_named_query(
            name=name, snapshot=query, read_time=_helpers.build_timestamp(read_time),
        )
        self._update_last_read_time(read_time)

    async def _process_async_query(
        self, name: str, snapshot: AsyncQuery,
    ) -> datetime.datetime:
        doc: DocumentSnapshot
        _read_time = datetime.datetime.min.replace(tzinfo=UTC)
        async for doc in snapshot.stream():
            self.add_document(doc, query_name=name)
            _read_time = doc.read_time
        return _read_time

    def _build_named_query(
        self, name: str, snapshot: BaseQuery, read_time: Timestamp,
    ) -> NamedQuery:
        return NamedQuery(
            name=name,
            bundled_query=BundledQuery(
                parent=name,
                structured_query=snapshot._to_protobuf()._pb,
                limit_type=limit_type_of_query(snapshot),
            ),
            read_time=read_time,
        )

    def _update_last_read_time(
        self, read_time: Union[datetime.datetime, Timestamp]
    ) -> None:
        _ts: Timestamp = (
            read_time
            if isinstance(read_time, Timestamp)
            else _datetime_to_pb_timestamp(read_time)
        )

        # if `_ts` is greater than `self.latest_read_time`
        if _helpers.compare_timestamps(_ts, self.latest_read_time) == 1:
            self.latest_read_time = _ts

    def _add_bundle_element(self, bundle_element: BundleElement, *, client: BaseClient, type: str):  # type: ignore
        """Applies BundleElements to this FirestoreBundle instance as a part of
        deserializing a FirestoreBundle string.
        """
        from google.cloud.firestore_v1.types.document import Document

        if getattr(self, "_doc_metadata_map", None) is None:
            self._doc_metadata_map = {}
        if type == "metadata":
            self._deserialized_metadata = bundle_element.metadata  # type: ignore
        elif type == "named_query":
            self.named_queries[bundle_element.named_query.name] = bundle_element.named_query  # type: ignore
        elif type == "document_metadata":
            self._doc_metadata_map[
                bundle_element.document_metadata.name
            ] = bundle_element.document_metadata
        elif type == "document":
            doc_ref_value = _helpers.DocumentReferenceValue(
                bundle_element.document.name
            )
            snapshot = DocumentSnapshot(
                data=_helpers.decode_dict(
                    Document(mapping=bundle_element.document).fields, client
                ),
                exists=True,
                reference=DocumentReference(
                    doc_ref_value.collection_name,
                    doc_ref_value.document_id,
                    client=client,
                ),
                read_time=self._doc_metadata_map[
                    bundle_element.document.name
                ].read_time,
                create_time=bundle_element.document.create_time,  # type: ignore
                update_time=bundle_element.document.update_time,  # type: ignore
            )
            self.add_document(snapshot)

            bundled_document = self.documents.get(snapshot.reference._document_path)
            for query_name in self._doc_metadata_map[
                bundle_element.document.name
            ].queries:
                bundled_document.metadata.queries.append(query_name)  # type: ignore
        else:
            raise ValueError(f"Unexpected type of BundleElement: {type}")

    def build(self) -> str:
        """Iterates over the bundle's stored documents and queries and produces
        a single length-prefixed json string suitable for long-term storage.

        Example:

            from google.cloud import firestore

            db = firestore.Client()
            collection_ref = db.collection(u'users')

            bundle = firestore.FirestoreBundle('my bundle')
            bundle.add('app-users', collection_ref._query())

            serialized_bundle: str = bundle.build()

            # Now upload `serialized_bundle` to Google Cloud Storage, store it
            # in Memorystore, or any other storage solution.

        Returns:
            str: The length-prefixed string representation of this bundle'
                contents.
        """
        buffer: str = ""

        named_query: NamedQuery
        for named_query in self.named_queries.values():
            buffer += self._compile_bundle_element(
                BundleElement(named_query=named_query)
            )

        bundled_document: "_BundledDocument"  # type: ignore
        document_count: int = 0
        for bundled_document in self.documents.values():
            buffer += self._compile_bundle_element(
                BundleElement(document_metadata=bundled_document.metadata)
            )
            document_count += 1
            buffer += self._compile_bundle_element(
                BundleElement(document=bundled_document.snapshot._to_protobuf()._pb,)
            )

        metadata: BundleElement = BundleElement(
            metadata=self._deserialized_metadata
            or BundleMetadata(
                id=self.name,
                create_time=_helpers.build_timestamp(),
                version=FirestoreBundle.BUNDLE_SCHEMA_VERSION,
                total_documents=document_count,
                total_bytes=len(buffer.encode("utf-8")),
            )
        )
        return f"{self._compile_bundle_element(metadata)}{buffer}"

    def _compile_bundle_element(self, bundle_element: BundleElement) -> str:
        serialized_be: str = json.dumps(BundleElement.to_dict(bundle_element))
        return f"{len(serialized_be)}{serialized_be}"

    def get_documents(
        self, *, query_name: Optional[str] = None
    ) -> Iterable[DocumentSnapshot]:
        bundled_doc: "_BundledDocument"
        for bundled_doc in self.documents.values():
            if query_name and query_name not in bundled_doc.metadata.queries:
                continue
            yield bundled_doc.snapshot

    def get_document(self, document_id: str) -> Optional[DocumentSnapshot]:
        bundled_doc = self.documents.get(document_id)
        if bundled_doc:
            return bundled_doc.snapshot


class _BundledDocument:
    """Convenience class to hold both the metadata and the actual content
    of a document to be bundled."""

    def __init__(
        self, snapshot: DocumentSnapshot, metadata: BundledDocumentMetadata,
    ) -> None:
        self.snapshot = snapshot
        self.metadata = metadata
