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
from typing import Iterable, Sequence, TYPE_CHECKING
from google.cloud.firestore_v1 import _pipeline_stages as stages
from google.cloud.firestore_v1.types.pipeline import (
    StructuredPipeline as StructuredPipeline_pb,
)
from google.cloud.firestore_v1.types.firestore import ExecutePipelineRequest
from google.cloud.firestore_v1.pipeline_result import PipelineResult
from google.cloud.firestore_v1.pipeline_expressions import (
    Accumulator,
    Expr,
    ExprWithAlias,
    FilterCondition,
    Selectable,
)
from google.cloud.firestore_v1 import _helpers

if TYPE_CHECKING:  # pragma: NO COVER
    from google.cloud.firestore_v1.client import Client
    from google.cloud.firestore_v1.async_client import AsyncClient
    from google.cloud.firestore_v1.types.firestore import ExecutePipelineResponse
    from google.cloud.firestore_v1.transaction import BaseTransaction


class _BasePipeline:
    """
    Base class for building Firestore data transformation and query pipelines.

    This class is not intended to be instantiated directly.
    Use `client.pipeline()` to create pipeline instances.
    """

    def __init__(self, client: Client | AsyncClient):
        """
        Initializes a new pipeline.

        Pipelines should not be instantiated directly. Instead,
        call client.pipeline() to create an instance

        Args:
            client: The client associated with the pipeline
        """
        self._client = client
        self.stages: Sequence[stages.Stage] = tuple()

    @classmethod
    def _create_with_stages(
        cls, client: Client | AsyncClient, *stages
    ) -> _BasePipeline:
        """
        Initializes a new pipeline with the given stages.

        Pipeline classes should not be instantiated directly.

        Args:
            client: The client associated with the pipeline
            *stages: Initial stages for the pipeline.
        """
        new_instance = cls(client)
        new_instance.stages = tuple(stages)
        return new_instance

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
        return self.__class__._create_with_stages(self._client, *self.stages, new_stage)

    def _prep_execute_request(
        self, transaction: BaseTransaction | None
    ) -> ExecutePipelineRequest:
        """
        shared logic for creating an ExecutePipelineRequest
        """
        database_name = (
            f"projects/{self._client.project}/databases/{self._client._database}"
        )
        transaction_id = (
            _helpers.get_transaction_id(transaction)
            if transaction is not None
            else None
        )
        request = ExecutePipelineRequest(
            database=database_name,
            transaction=transaction_id,
            structured_pipeline=self._to_pb(),
        )
        return request

    def _execute_response_helper(
        self, response: ExecutePipelineResponse
    ) -> Iterable[PipelineResult]:
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
                doc._pb.create_time if doc.create_time else None,
                doc._pb.update_time if doc.update_time else None,
            )

    def generic_stage(self, name: str, *params: Expr) -> "_BasePipeline":
        """
        Adds a generic, named stage to the pipeline with specified parameters.

        This method provides a flexible way to extend the pipeline's functionality
        by adding custom stages. Each generic stage is defined by a unique `name`
        and a set of `params` that control its behavior.

        Example:
            >>> # Assume we don't have a built-in "where" stage
            >>> pipeline = client.pipeline().collection("books")
            >>> pipeline = pipeline.generic_stage("where", [Field.of("published").lt(900)])
            >>> pipeline = pipeline.select("title", "author")

        Args:
            name: The name of the generic stage.
            *params: A sequence of `Expr` objects representing the parameters for the stage.

        Returns:
            A new Pipeline object with this stage appended to the stage list
        """
        return self._append(stages.GenericStage(name, *params))

    def select(self, *selections: str | Selectable) -> "_BasePipeline":
        """
        Selects or creates a set of fields from the outputs of previous stages.
        The selected fields are defined using `Selectable` expressions or field names:
            - `Field`: References an existing document field.
            - `Function`: Represents the result of a function with an assigned alias
              name using `Expr.as_()`.
            - `str`: The name of an existing field.
        If no selections are provided, the output of this stage is empty. Use
        `add_fields()` instead if only additions are desired.
        Example:
            >>> from google.cloud.firestore_v1.pipeline_expressions import Field, to_upper
            >>> pipeline = client.pipeline().collection("books")
            >>> # Select by name
            >>> pipeline = pipeline.select("name", "address")
            >>> # Select using Field and Function expressions
            >>> pipeline = pipeline.select(
            ...     Field.of("name"),
            ...     Field.of("address").to_upper().as_("upperAddress"),
            ... )
        Args:
            *selections: The fields to include in the output documents, specified as
                         field names (str) or `Selectable` expressions.
        Returns:
            A new Pipeline object with this stage appended to the stage list
        """
        return self._append(stages.Select(*selections))

    def where(self, condition: FilterCondition) -> "_BasePipeline":
        """
        Filters the documents from previous stages to only include those matching
        the specified `FilterCondition`.
        This stage allows you to apply conditions to the data, similar to a "WHERE"
        clause in SQL. You can filter documents based on their field values, using
        implementations of `FilterCondition`, typically including but not limited to:
            - field comparators: `eq`, `lt` (less than), `gt` (greater than), etc.
            - logical operators: `And`, `Or`, `Not`, etc.
            - advanced functions: `regex_matches`, `array_contains`, etc.
        Example:
            >>> from google.cloud.firestore_v1.pipeline_expressions import Field, And,
            >>> pipeline = client.pipeline().collection("books")
            >>> # Using static functions
            >>> pipeline = pipeline.where(
            ...     And(
            ...         Field.of("rating").gt(4.0),   # Filter for ratings > 4.0
            ...         Field.of("genre").eq("Science Fiction") # Filter for genre
            ...     )
            ... )
            >>> # Using methods on expressions
            >>> pipeline = pipeline.where(
            ...     And(
            ...         Field.of("rating").gt(4.0),
            ...         Field.of("genre").eq("Science Fiction")
            ...     )
            ... )
        Args:
            condition: The `FilterCondition` to apply.
        Returns:
            A new Pipeline object with this stage appended to the stage list
        """
        return self._append(stages.Where(condition))

    def sort(self, *orders: stages.Ordering) -> "_BasePipeline":
        """
        Sorts the documents from previous stages based on one or more `Ordering` criteria.
        This stage allows you to order the results of your pipeline. You can specify
        multiple `Ordering` instances to sort by multiple fields or expressions in
        ascending or descending order. If documents have the same value for a sorting
        criterion, the next specified ordering will be used. If all orderings result
        in equal comparison, the documents are considered equal and the relative order
        is unspecified.
        Example:
            >>> from google.cloud.firestore_v1.pipeline_expressions import Field
            >>> pipeline = client.pipeline().collection("books")
            >>> # Sort books by rating descending, then title ascending
            >>> pipeline = pipeline.sort(
            ...     Field.of("rating").descending(),
            ...     Field.of("title").ascending()
            ... )
        Args:
            *orders: One or more `Ordering` instances specifying the sorting criteria.
        Returns:
            A new Pipeline object with this stage appended to the stage list
        """
        return self._append(stages.Sort(*orders))

    def offset(self, offset: int) -> "_BasePipeline":
        """
        Skips the first `offset` number of documents from the results of previous stages.
        This stage is useful for implementing pagination, allowing you to retrieve
        results in chunks. It is typically used in conjunction with `limit()` to
        control the size of each page.
        Example:
            >>> from google.cloud.firestore_v1.pipeline_expressions import Field
            >>> pipeline = client.pipeline().collection("books")
            >>> # Retrieve the second page of 20 results (assuming sorted)
            >>> pipeline = pipeline.sort(Field.of("published").descending())
            >>> pipeline = pipeline.offset(20)  # Skip the first 20 results
            >>> pipeline = pipeline.limit(20)   # Take the next 20 results
        Args:
            offset: The non-negative number of documents to skip.
        Returns:
            A new Pipeline object with this stage appended to the stage list
        """
        return self._append(stages.Offset(offset))

    def limit(self, limit: int) -> "_BasePipeline":
        """
        Limits the maximum number of documents returned by previous stages to `limit`.
        This stage is useful for controlling the size of the result set, often used for:
            - **Pagination:** In combination with `offset()` to retrieve specific pages.
            - **Top-N queries:** To get a limited number of results after sorting.
            - **Performance:** To prevent excessive data transfer.
        Example:
            >>> from google.cloud.firestore_v1.pipeline_expressions import Field
            >>> pipeline = client.pipeline().collection("books")
            >>> # Limit the results to the top 10 highest-rated books
            >>> pipeline = pipeline.sort(Field.of("rating").descending())
            >>> pipeline = pipeline.limit(10)
        Args:
            limit: The non-negative maximum number of documents to return.
        Returns:
            A new Pipeline object with this stage appended to the stage list
        """
        return self._append(stages.Limit(limit))

    def aggregate(
        self,
        *accumulators: ExprWithAlias[Accumulator],
        groups: Sequence[str | Selectable] = (),
    ) -> "_BasePipeline":
        """
        Performs aggregation operations on the documents from previous stages,
        optionally grouped by specified fields or expressions.

        This stage allows you to calculate aggregate values (like sum, average, count,
        min, max) over a set of documents.

        - **Accumulators:** Define the aggregation calculations using `Accumulator`
          expressions (e.g., `sum()`, `avg()`, `count()`, `min()`, `max()`) combined
          with `as_()` to name the result field.
        - **Groups:** Optionally specify fields (by name or `Selectable`) to group
          the documents by. Aggregations are then performed within each distinct group.
          If no groups are provided, the aggregation is performed over the entire input.

        Example:
            >>> from google.cloud.firestore_v1.pipeline_expressions import Field, avg, count_all
            >>> pipeline = client.pipeline().collection("books")
            >>> # Calculate the average rating and total count for all books
            >>> pipeline = pipeline.aggregate(
            ...     Field.of("rating").avg().as_("averageRating"),
            ...     Field.of("rating").count().as_("totalBooks")
            ... )
            >>> # Calculate the average rating for each genre
            >>> pipeline = pipeline.aggregate(
            ...     Field.of("rating").avg().as_("avg_rating"),
            ...     groups=["genre"] # Group by the 'genre' field
            ... )
            >>> # Calculate the count for each author, grouping by Field object
            >>> pipeline = pipeline.aggregate(
            ...     Count().as_("bookCount"),
            ...     groups=[Field.of("author")]
            ... )


        Args:
            *accumulators: One or more `ExprWithAlias[Accumulator]` expressions defining
                           the aggregations to perform and their output names.
            groups: An optional sequence of field names (str) or `Selectable`
                    expressions to group by before aggregating.

        Returns:
            A new Pipeline object with this stage appended to the stage list
        """
        return self._append(stages.Aggregate(*accumulators, groups=groups))
