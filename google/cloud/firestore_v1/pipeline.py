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
from google.cloud.firestore_v1.base_pipeline import _BasePipeline
from google.cloud.firestore_v1.pipeline_result import PipelineStream
from google.cloud.firestore_v1.pipeline_result import PipelineSnapshot

if TYPE_CHECKING:  # pragma: NO COVER
    from google.cloud.firestore_v1.client import Client
    from google.cloud.firestore_v1.pipeline_result import PipelineResult
    from google.cloud.firestore_v1.transaction import Transaction
    from google.cloud.firestore_v1.query_profile import ExplainMetrics
    from google.cloud.firestore_v1.query_profile import ExplainOptions


class Pipeline(_BasePipeline):
    """
    Pipelines allow for complex data transformations and queries involving
    multiple stages like filtering, projection, aggregation, and vector search.

    Usage Example:
        >>> from google.cloud.firestore_v1.pipeline_expressions import Field
        >>>
        >>> def run_pipeline():
        ...     client = Client(...)
        ...     pipeline = client.pipeline()
        ...                      .collection("books")
        ...                      .where(Field.of("published").gt(1980))
        ...                      .select("title", "author")
        ...     for result in pipeline.execute():
        ...         print(result)

    Use `client.pipeline()` to create instances of this class.
    """

    def __init__(self, client: Client, *stages: stages.Stage):
        """
        Initializes a Pipeline.

        Args:
            client: The `Client` instance to use for execution.
            *stages: Initial stages for the pipeline.
        """
        super().__init__(client, *stages)

    def execute(
        self,
        *,
        transaction: "Transaction" | None = None,
        explain_options: ExplainOptions | None = None,
    ) -> PipelineSnapshot[PipelineResult]:
        """
        Executes this pipeline and returns results as a list

        Args:
            transaction (Optional[:class:`~google.cloud.firestore_v1.transaction.Transaction`]):
                An existing transaction that this query will run in.
                If a ``transaction`` is used and it already has write operations
                added, this method cannot be used (i.e. read-after-write is not
                allowed).
            explain_options (Optional[:class:`~google.cloud.firestore_v1.query_profile.ExplainOptions`]):
                Options to enable query profiling for this query. When set,
                explain_metrics will be available on the returned list.
        """
        stream = self.stream(transaction=transaction, explain_options=explain_options)
        results = [result for result in stream]
        return PipelineSnapshot(results, stream)

    def stream(
        self,
        *,
        transaction: "Transaction" | None = None,
        explain_options: ExplainOptions | None = None,
    ) -> PipelineStream[PipelineResult]:
        """
        Process this pipeline as a stream, providing results through an Iterable

        Args:
            transaction (Optional[:class:`~google.cloud.firestore_v1.transaction.Transaction`]):
                An existing transaction that this query will run in.
                If a ``transaction`` is used and it already has write operations
                added, this method cannot be used (i.e. read-after-write is not
                allowed).
            explain_options (Optional[:class:`~google.cloud.firestore_v1.query_profile.ExplainOptions`]):
                Options to enable query profiling for this query. When set,
                explain_metrics will be available on the returned generator.
        """
        return PipelineStream(self, transaction, explain_options)