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
from typing import TYPE_CHECKING
from google.cloud.firestore_v1 import pipeline_stages as stages
from google.cloud.firestore_v1.document import DocumentReference
from google.cloud.firestore_v1.types.pipeline import (
    StructuredPipeline as StructuredPipeline_pb,
)
from google.cloud.firestore_v1.pipeline_result import PipelineResult
from google.cloud.firestore_v1 import _helpers, document

if TYPE_CHECKING:
    from google.cloud.firestore_v1.client import Client
    from google.cloud.firestore_v1.async_client import AsyncClient


class _BasePipeline:
    """
    Base class for building Firestore data transformation and query pipelines.

    This class is not intended to be instantiated directly.
    Use `client.collection.("...").pipeline()` to create pipeline instances.
    """

    def __init__(self, client: Client | AsyncClient, *stages: stages.Stage):
        """
        Initializes a new pipeline with the given stages.

        Pipeline classes should not be instantiated directly.

        Args:
            client: The client associated with the pipeline
            *stages: Initial stages for the pipeline.
        """
        self._client = client
        self.stages = tuple(stages)

    def __repr__(self):
        if not self.stages:
            return "Pipeline()"
        elif len(self.stages) == 1:
            return f"Pipeline({self.stages[0]!r})"
        else:
            stages_str = ",\n  ".join([repr(s) for s in self.stages])
            return f"Pipeline(\n  {stages_str}\n)"

    def _to_pb(self) -> StructuredPipeline_pb:
        return StructuredPipeline_pb(
            pipeline={"stages": [s._to_pb() for s in self.stages]}
        )

    def _append(self, new_stage):
        """
        Create a new Pipeline object with a new stage appended
        """
        return self.__class__(self._client, *self.stages, new_stage)