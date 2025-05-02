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
from typing_extensions import Self
from google.cloud.firestore_v1 import pipeline_stages as stages
from google.cloud.firestore_v1.base_client import BaseClient
from google.cloud.firestore_v1.types.pipeline import (
    StructuredPipeline as StructuredPipeline_pb,
)
from google.cloud.firestore_v1 import _helpers, document
from google.cloud.firestore_v1.pipeline_expressions import (
    FilterCondition,
    Selectable,
)


class _BasePipeline:
    """
    Base class for building Firestore data transformation and query pipelines.

    This class is not intended to be instantiated directly.
    Use `client.collection.("...").pipeline()` to create pipeline instances.
    """

    def __init__(self, client: BaseClient, *stages: stages.Stage):
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

    @staticmethod
    def _parse_response(response_pb, client):
        for doc in response_pb.results:
            data = _helpers.decode_dict(doc.fields, client)
            yield document.DocumentSnapshot(
                None,
                data,
                exists=True,
                read_time=response_pb._pb.execution_time,
                create_time=doc.create_time,
                update_time=doc.update_time,
            )

    def select(self, *selections: str | Selectable) -> Self:
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
            >>> pipeline = client.collection("books").pipeline()
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

    def where(self, condition: FilterCondition) -> Self:
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
            >>> pipeline = client.collection("books").pipeline()
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

    def sort(self, *orders: stages.Ordering) -> Self:
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
            >>> pipeline = client.collection("books").pipeline()
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

    def offset(self, offset: int) -> Self:
        """
        Skips the first `offset` number of documents from the results of previous stages.
        This stage is useful for implementing pagination, allowing you to retrieve
        results in chunks. It is typically used in conjunction with `limit()` to
        control the size of each page.
        Example:
            >>> from google.cloud.firestore_v1.pipeline_expressions import Field
            >>> pipeline = client.collection("books").pipeline()
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

    def limit(self, limit: int) -> Self:
        """
        Limits the maximum number of documents returned by previous stages to `limit`.
        This stage is useful for controlling the size of the result set, often used for:
            - **Pagination:** In combination with `offset()` to retrieve specific pages.
            - **Top-N queries:** To get a limited number of results after sorting.
            - **Performance:** To prevent excessive data transfer.
        Example:
            >>> from google.cloud.firestore_v1.pipeline_expressions import Field
            >>> pipeline = client.collection("books").pipeline()
            >>> # Limit the results to the top 10 highest-rated books
            >>> pipeline = pipeline.sort(Field.of("rating").descending())
            >>> pipeline = pipeline.limit(10)
        Args:
            limit: The non-negative maximum number of documents to return.
        Returns:
            A new Pipeline object with this stage appended to the stage list
        """
        return self._append(stages.Limit(limit))