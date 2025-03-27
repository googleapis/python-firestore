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
import datetime
from typing import AsyncIterable, TYPE_CHECKING
from google.cloud.firestore_v1 import pipeline_stages as stages
from google.cloud.firestore_v1.types.firestore import ExecutePipelineRequest
from google.cloud.firestore_v1.types.firestore import ExecutePipelineResponse
from google.cloud.firestore_v1.base_pipeline import _BasePipeline

if TYPE_CHECKING:
    from google.cloud.firestore_v1.async_client import AsyncClient


class Pipeline(_BasePipeline):
    def __init__(self, client:AsyncClient, *stages: stages.Stage):
        super().__init__(*stages)
        self._client = client

    async def execute_async(self) -> AsyncIterable["ExecutePipelineResponse"]:
        database_name = f"projects/{self._client.project}/databases/{self._client._database}"
        request = ExecutePipelineRequest(
            database=database_name,
            structured_pipeline=self._to_pb(),
            read_time=datetime.datetime.now(),
        )
        return await self._client._firestore_api.execute_pipeline(request)
