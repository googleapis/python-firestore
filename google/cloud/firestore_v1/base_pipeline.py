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
from typing import Iterable, TYPE_CHECKING
from google.cloud.firestore_v1 import pipeline_stages as stages
from google.cloud.firestore_v1.types.pipeline import (
    StructuredPipeline as StructuredPipeline_pb,
)
from google.cloud.firestore_v1.types.firestore import ExecutePipelineRequest
from google.cloud.firestore_v1.pipeline_result import PipelineResult

if TYPE_CHECKING:
    from google.cloud.firestore_v1.client import Client
    from google.cloud.firestore_v1.async_client import AsyncClient
    from google.cloud.firestore_v1.types.firestore import ExecutePipelineResponse


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
        cls_str = type(self).__name__
        if not self.stages:
            return f"{cls_str}()"
        elif len(self.stages) == 1:
            return f"{cls_str}({self.stages[0]!r})"
        else:
            stages_str = ",\n  ".join([repr(s) for s in self.stages])
            return f"{cls_str}(\n  {stages_str}\n)"

    def _to_pb(self) -> StructuredPipeline_pb:
        return StructuredPipeline_pb(
            pipeline={"stages": [s._to_pb() for s in self.stages]}
        )

    def _append(self, new_stage):
        """
        Create a new Pipeline object with a new stage appended
        """
        return self.__class__(self._client, *self.stages, new_stage)

    def _execute_request_helper(self) -> ExecutePipelineRequest:
        """
        shared logic for creating an ExecutePipelineRequest
        """
        database_name = (
            f"projects/{self._client.project}/databases/{self._client._database}"
        )
        request = ExecutePipelineRequest(
            database=database_name,
            structured_pipeline=self._to_pb(),
        )
        return request

    def _execute_response_helper(self, response:ExecutePipelineResponse) -> Iterable[PipelineResult]:
        """
        shared logic for unpacking an ExecutePipelineReponse into PipelineResults
        """
        for doc in response.results:
            ref = self._client.document(doc.name) if doc.name else None
            yield PipelineResult(
                self._client,
                doc.fields,
                ref,
                response._pb.execution_time,
                doc.create_time.timestamp_pb() if doc.create_time else None,
                doc.update_time.timestamp_pb() if doc.update_time else None,
            )