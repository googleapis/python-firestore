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
from google.cloud.firestore_v1.base_pipeline import _BasePipeline

if TYPE_CHECKING:
    from google.cloud.firestore_v1.async_client import AsyncClient
    from google.cloud.firestore_v1.pipeline_result import PipelineResult
    from google.cloud.firestore_v1.async_transaction import AsyncTransaction


class AsyncPipeline(_BasePipeline):
    """
    Pipelines allow for complex data transformations and queries involving
    multiple stages like filtering, projection, aggregation, and vector search.

    This class extends `_BasePipeline` and provides methods to execute the
    defined pipeline stages using an asynchronous `AsyncClient`.

    Usage Example:
        >>> from google.cloud.firestore_v1.pipeline_expressions import Field
        >>>
        >>> async def run_pipeline():
        ...     client = AsyncClient(...)
        ...     pipeline = client.pipeline()
        ...                      .collection("books")
        ...                      .where(Field.of("published").gt(1980))
        ...                      .select("title", "author")
        ...     async for result in pipeline.execute_async():
        ...         print(result)

    Use `client.pipeline()` to create instances of this class.
    """

    def __init__(self, client: AsyncClient, *stages: stages.Stage):
        """
        Initializes an asynchronous Pipeline.

        Args:
            client: The asynchronous `AsyncClient` instance to use for execution.
            *stages: Initial stages for the pipeline.
        """
        super().__init__(client, *stages)

    async def execute(
        self,
        transaction: "AsyncTransaction" | None=None,
    ) -> AsyncIterable[PipelineResult]:
        """
        Executes this pipeline, providing results through an Iterable

        Args:
            transaction
                (Optional[:class:`~google.cloud.firestore_v1.transaction.Transaction`]):
                An existing transaction that this query will run in.
                If a ``transaction`` is used and it already has write operations
                added, this method cannot be used (i.e. read-after-write is not
                allowed).
        """
        request = self._prep_execute_request(transaction)
        async for response in await self._client._firestore_api.execute_pipeline(request):
            for result in self._execute_response_helper(response):
                yield result