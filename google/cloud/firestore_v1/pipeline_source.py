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
from google.cloud.firestore_v1 import _pipeline_stages as stages
from google.cloud.firestore_v1.base_pipeline import _BasePipeline

if TYPE_CHECKING:  # pragma: NO COVER
    from google.cloud.firestore_v1.client import Client
    from google.cloud.firestore_v1.async_client import AsyncClient


PipelineType = TypeVar("PipelineType", bound=_BasePipeline)


class PipelineSource(Generic[PipelineType]):
    """
    A factory for creating Pipeline instances, which provide a framework for building data
    transformation and query pipelines for Firestore.

    Not meant to be instantiated directly. Instead, start by calling client.pipeline()
    to obtain an instance of PipelineSource. From there, you can use the provided
    methods to specify the data source for your pipeline.
    """

    def __init__(self, client: Client | AsyncClient):
        self.client = client

    def _create_pipeline(self, source_stage):
        return self.client._pipeline_cls._create_with_stages(self.client, source_stage)

    def collection(self, path: str) -> PipelineType:
        """
        Creates a new Pipeline that operates on a specified Firestore collection.

        Args:
            path: The path to the Firestore collection (e.g., "users")
        Returns:
            a new pipeline instance targeting the specified collection
        """
        return self._create_pipeline(stages.Collection(path))
