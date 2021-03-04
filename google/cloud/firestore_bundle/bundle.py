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
from google.cloud.firestore_v1.types.query import StructuredQuery

from google.cloud.firestore_bundle.types.bundle import (
    BundledDocumentMetadata,
    BundledQuery,
    BundleElement,
    BundleMetadata,
    NamedQuery,
)
from google.cloud._helpers import _datetime_to_pb_timestamp, UTC  # type: ignore
from google.cloud.firestore_v1.async_query import AsyncQuery
from google.cloud.firestore_v1.async_collection import AsyncCollectionReference
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.base_query import BaseQuery
from google.cloud.firestore_v1.base_collection import BaseCollectionReference
from google.cloud.firestore_v1.collection import CollectionReference
from google.cloud.firestore_v1.query import Query
from google.cloud.firestore_v1 import _helpers
from google.protobuf.timestamp_pb2 import Timestamp  # type: ignore
from typing import (
    Dict,
    List,
    Optional,
    Union,
)


class FirestoreBundle:

    BUNDLE_SCHEMA_VERSION: int = 1

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.documents: Dict[str, "_BundledDocument"] = {}
        self.named_queries: Dict[str, NamedQuery] = {}
        self.latest_read_time: Timestamp = Timestamp(seconds=0, nanos=0)

    def add(
        self,
        document_or_query_name: Union[DocumentSnapshot, str],
        query_snapshot: Optional[Query] = None,
    ):
        if isinstance(document_or_query_name, DocumentSnapshot):
            assert query_snapshot is None
            self.add_document(document_or_query_name)
        elif isinstance(document_or_query_name, str):
            assert query_snapshot is not None
            self.add_named_query(document_or_query_name, query_snapshot)
        else:
            raise ValueError(
                "Bundle.add accepts either a standalone DocumentSnapshot, or "
                "a name (string) and a Query."
            )
        return self

    def add_document(
        self, snapshot: DocumentSnapshot, query_name: Optional[str] = None,
    ) -> None:
        original_document: Optional[_BundledDocument]
        original_queries: Optional[List[str]] = []
        _id: str = snapshot.reference._document_path

        original_document = self.documents.get(_id)
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
            self.documents[_id] = _BundledDocument(
                snapshot=snapshot,
                metadata=BundledDocumentMetadata(
                    name=snapshot.id,
                    read_time=snapshot.read_time,
                    exists=snapshot.exists,
                    queries=original_queries,
                ),
            )

        if query_name:
            bundled_document = self.documents.get(_id)
            bundled_document.metadata.queries.append(query_name)  # type: ignore

        self._update_last_read_time(snapshot.read_time)

    def add_named_query(self, name: str, snapshot: BaseQuery,) -> None:
        if not isinstance(snapshot, BaseQuery):
            raise ValueError(
                "Attempted to add named query of type: "
                f"{type(snapshot).__name__}. Expected BaseQuery.",
            )

        if self.named_queries.get(name):
            raise ValueError(f"Query name conflict: {name} has already been added.")

        _read_time = datetime.datetime.min.replace(tzinfo=UTC)
        if isinstance(snapshot, AsyncQuery):
            import asyncio

            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._process_async_query(name, snapshot))

        elif isinstance(snapshot, BaseQuery):
            doc: DocumentSnapshot
            for doc in snapshot.stream():
                self.add_document(doc, query_name=name)
                _read_time = doc.read_time

        self.named_queries[name] = self._build_named_query(
            name=name,
            snapshot=snapshot,
            read_time=_helpers.build_timestamp(_read_time),
        )
        self._update_last_read_time(_read_time)

    async def _process_async_query(self, name, snapshot) -> datetime.datetime:
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
                # TODO: is this value for `parent` correct?
                parent=name,
                structured_query=snapshot._to_protobuf()._pb,
                limit_type=snapshot.limit_type,
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

    def build(self) -> str:
        buffer: str = ''

        named_query: NamedQuery
        for named_query in self.named_queries.values():
            buffer += self._compile_bundle_element(
                BundleElement(
                    named_query=named_query,
                )
            )

        bundled_document: '_BundledDocument'  # type: ignore
        document_count: int = 0
        for bundled_document in self.documents.values():
            buffer += self._compile_bundle_element(
                BundleElement(
                    document_metadata=bundled_document.metadata,
                )
            )
            if bundled_document.snapshot is not None:
                document_count += 1
                buffer += self._compile_bundle_element(
                    BundleElement(
                        document=bundled_document.snapshot._to_protobuf()._pb,
                    )
                )

        metadata: BundleElement = BundleElement(
            metadata=BundleMetadata(
                id=self.name,
                create_time=_helpers.build_timestamp(),
                version=FirestoreBundle.BUNDLE_SCHEMA_VERSION,
                total_documents=document_count,
                total_bytes=len(buffer.encode('utf-8')),
            )
        )
        return f'{self._compile_bundle_element(metadata)}{buffer}'

    def _compile_bundle_element(self, bundle_element: BundleElement) -> str:
        serialized_be: str = BundleElement.to_json(bundle_element)
        # TODO: Does this `len()` call need to be against `encode('utf-8')`?
        return f'{len(serialized_be)}{serialized_be}'


class _BundledDocument:
    """Convenience class to hold both the metadata and the actual content
    of a document to be bundled."""

    def __init__(
        self, snapshot: DocumentSnapshot, metadata: BundledDocumentMetadata,
    ) -> None:
        self.snapshot = snapshot
        self.metadata = metadata
