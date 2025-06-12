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
from typing import Generic, TypeVar, TYPE_CHECKING
from google.cloud.firestore_v1 import pipeline_stages as stages
from google.cloud.firestore_v1.base_pipeline import _BasePipeline
from google.cloud.firestore_v1._helpers import DOCUMENT_PATH_DELIMITER

if TYPE_CHECKING:  # pragma: NO COVER
    from google.cloud.firestore_v1.client import Client
    from google.cloud.firestore_v1.async_client import AsyncClient
    from google.cloud.firestore_v1.base_document import BaseDocumentReference


PipelineType = TypeVar("PipelineType", bound=_BasePipeline)


class PipelineSource(Generic[PipelineType]):
    """
    A factory for creating Pipeline instances, which provide a framework for building data
    transformation and query pipelines for Firestore.

    Start by calling client.pipeline() to obtain an instance of PipelineSource.
    From there, you can use the provided methods .collection() to specify the
    data source for your pipeline.

    This class is typically used to start building Firestore pipelines. It allows you to define
    the initial data source for a pipeline.
    """

    def __init__(self, client: Client | AsyncClient):
        self.client = client

    def _create_pipeline(self, source_stage):
        return self.client._pipeline_cls(self.client, source_stage)

    def collection(self, path: str | tuple[str]) -> PipelineType:
        """
        Creates a new Pipeline that operates on a specified Firestore collection.

        Args:
            path: The path to the Firestore collection (e.g., "users"). Can either be:
                * A single ``/``-delimited path to a collection
                * A tuple of collection path segment
        Returns:
            a new pipeline instance targeting the specified collection
        """
        if isinstance(path, tuple):
            path = DOCUMENT_PATH_DELIMITER.join(path)
        return self._create_pipeline(stages.Collection(path))

    def collection_group(self, collection_id: str) -> PipelineType:
        """
        Creates a new Pipeline that that operates on all documents in a collection group.
        Args:
            collection_id: The ID of the collection group
        Returns:
            a new pipeline instance targeting the specified collection group
        """
        return self._create_pipeline(stages.CollectionGroup(collection_id))

    def database(self) -> PipelineType:
        """
        Creates a new Pipeline that operates on all documents in the Firestore database.
        Returns:
            a new pipeline instance targeting the specified collection
        """
        return self._create_pipeline(stages.Database())

    def documents(self, *docs: "BaseDocumentReference") -> PipelineType:
        """
        Creates a new Pipeline that operates on a specific set of Firestore documents.
        Args:
            docs: The DocumentReference instances representing the documents to include in the pipeline.
        Returns:
            a new pipeline instance targeting the specified documents
        """
        return self._create_pipeline(stages.Documents.of(*docs))
