# Copyright 2025 Google LLC
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

from __future__ import annotations
from typing import Any, MutableMapping, Iterable, TYPE_CHECKING
from google.cloud.firestore_v1 import _helpers
from google.cloud.firestore_v1.field_path import get_nested_value
from google.cloud.firestore_v1.field_path import FieldPath

if TYPE_CHECKING:  # pragma: NO COVER
    from google.cloud.firestore_v1.base_client import BaseClient
    from google.cloud.firestore_v1.base_document import BaseDocumentReference
    from google.protobuf.timestamp_pb2 import Timestamp
    from google.cloud.firestore_v1.types.document import Value as ValueProto
    from google.cloud.firestore_v1.vector import Vector


class PipelineResult:
    """
    Contains data read from a Firestore Pipeline. The data can be extracted with
    the `data()` or `get()` methods.

    If the PipelineResult represents a non-document result `ref` may be `None`.
    """

    def __init__(
        self,
        client: BaseClient,
        fields_pb: MutableMapping[str, ValueProto],
        ref: BaseDocumentReference | None = None,
        execution_time: Timestamp | None = None,
        create_time: Timestamp | None = None,
        update_time: Timestamp | None = None,
    ):
        """
        PipelineResult should be returned from `pipeline.execute()`, not constructed manually.

        Args:
            client: The Firestore client instance.
            fields_pb: A map of field names to their protobuf Value representations.
            ref: The DocumentReference or AsyncDocumentReference if this result corresponds to a document.
            execution_time: The time at which the pipeline execution producing this result occurred.
            create_time: The creation time of the document, if applicable.
            update_time: The last update time of the document, if applicable.
        """
        self._client = client
        self._fields_pb = fields_pb
        self._ref = ref
        self._execution_time = execution_time
        self._create_time = create_time
        self._update_time = update_time

    def __repr__(self):
        return f"{type(self).__name__}(data={self.data()})"

    @property
    def ref(self) -> BaseDocumentReference | None:
        """
        The `BaseDocumentReference` if this result represents a document, else `None`.
        """
        return self._ref

    @property
    def id(self) -> str | None:
        """The ID of the document if this result represents a document, else `None`."""
        return self._ref.id if self._ref else None

    @property
    def create_time(self) -> Timestamp | None:
        """The creation time of the document. `None` if not applicable."""
        return self._create_time

    @property
    def update_time(self) -> Timestamp | None:
        """The last update time of the document. `None` if not applicable."""
        return self._update_time

    @property
    def execution_time(self) -> Timestamp:
        """
        The time at which the pipeline producing this result was executed.

        Raise:
            ValueError: if not set
        """
        if self._execution_time is None:
            raise ValueError("'execution_time' is expected to exist, but it is None.")
        return self._execution_time

    def __eq__(self, other: object) -> bool:
        """
        Compares this `PipelineResult` to another object for equality.

        Two `PipelineResult` instances are considered equal if their document
        references (if any) are equal and their underlying field data
        (protobuf representation) is identical.
        """
        if not isinstance(other, PipelineResult):
            return NotImplemented
        return (self._ref == other._ref) and (self._fields_pb == other._fields_pb)

    def data(self) -> dict | "Vector" | None:
        """
        Retrieves all fields in the result.

        Returns:
            The data in dictionary format, or `None` if the document doesn't exist.
        """
        if self._fields_pb is None:
            return None

        return _helpers.decode_dict(self._fields_pb, self._client)

    def get(self, field_path: str | FieldPath) -> Any:
        """
        Retrieves the field specified by `field_path`.

        Args:
            field_path: The field path (e.g. 'foo' or 'foo.bar') to a specific field.

        Returns:
            The data at the specified field location, decoded to Python types.
        """
        str_path = (
            field_path if isinstance(field_path, str) else field_path.to_api_repr()
        )
        value = get_nested_value(str_path, self._fields_pb)
        return _helpers.decode_value(value, self._client)

class PipelineSnapshot(list[PipelineResult]):
    def __init__(self, results_list: list[PipelineResult]):
        super().__init__(results_list)

    @classmethod
    def _from_stream(cls, stream: PipelineStream):
        results = [r for r in stream]
        return cls(results)

class PipelineStream(Iterable[PipelineResult]):

    def __init__(self, client, rpc_stream):
        self._client = client
        self._stream = rpc_stream

    def __iter__(self) -> PipelineStream:
        for response in self._stream:
            for doc in response.results:
                ref = self._client.document(doc.name) if doc.name else None
                yield PipelineResult(
                    self._client,
                    doc.fields,
                    ref,
                    response._pb.execution_time,
                    doc._pb.create_time if doc.create_time else None,
                    doc._pb.update_time if doc.update_time else None,
                )