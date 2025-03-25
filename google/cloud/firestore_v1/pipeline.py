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
from typing import AsyncIterable, Any, Dict, Iterable, List, Optional, Sequence
from google.cloud.firestore_v1 import pipeline_stages as stages
from google.cloud.firestore_v1.types.pipeline import StructuredPipeline as StructuredPipeline_pb
from google.cloud.firestore_v1.types.firestore import ExecutePipelineRequest
from google.cloud.firestore_v1.types.firestore import ExecutePipelineResponse
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from google.cloud.firestore_v1.pipeline_expressions import (
    Accumulator,
    Expr,
    ExprWithAlias,
    Field,
    FilterCondition,
    Selectable,
    SampleOptions,
)


class Pipeline:
    def __init__(self, client, *stages: stages.Stage):
        self._client = client
        self.stages = list(stages)

    def __repr__(self):
        if not self.stages:
            return "Pipeline()"
        elif len(self.stages) == 1:
            return f"Pipeline({self.stages[0]!r})"
        else:
            stages_str = ",\n  ".join([repr(s) for s in self.stages])
            return f"Pipeline(\n  {stages_str}\n)"

    def _to_pb(self) -> StructuredPipeline_pb:
        return StructuredPipeline_pb(pipeline={"stages":[s._to_pb() for s in self.stages]})

    def add_fields(self, *fields: Selectable) -> Pipeline:
        self.stages.append(stages.AddFields(*fields))
        return self

    def remove_fields(self, *fields: Field | str) -> Pipeline:
        self.stages.append(stages.RemoveFields(*fields))
        return self

    def select(self, *selections: str | Selectable) -> Pipeline:
        self.stages.append(stages.Select(*selections))
        return self

    def where(self, condition: FilterCondition) -> Pipeline:
        self.stages.append(stages.Where(condition))
        return self

    def find_nearest(
        self,
        field: str | Expr,
        vector: Sequence[float] | "Vector",
        distance_measure: "DistanceMeasure",
        limit: int | None,
        options: Optional[stages.FindNearestOptions] = None,
    ) -> Pipeline:
        self.stages.append(stages.FindNearest(field, vector, distance_measure, options))
        return self

    def sort(self, *orders: stages.Ordering) -> Pipeline:
        self.stages.append(stages.Sort(*orders))
        return self

    def replace(
        self,
        field: Selectable,
        mode: stages.Replace.Mode = stages.Replace.Mode.FULL_REPLACE,
    ) -> Pipeline:
        self.stages.append(stages.Replace(field, mode))
        return self

    def sample(self, limit_or_options: int | SampleOptions) -> Pipeline:
        self.stages.append(stages.Sample(limit_or_options))
        return self

    def union(self, other: Pipeline) -> Pipeline:
        self.stages.append(stages.Union(other))
        return self

    def unnest(
        self,
        field_name: str,
        options: Optional[stages.UnnestOptions] = None,
    ) -> Pipeline:
        self.stages.append(stages.Unnest(field_name, options))
        return self

    def generic_stage(self, name: str, *params: Expr) -> Pipeline:
        self.stages.append(stages.GenericStage(name, *params))
        return self

    def offset(self, offset: int) -> Pipeline:
        self.stages.append(stages.Offset(offset))
        return self

    def limit(self, limit: int) -> Pipeline:
        self.stages.append(stages.Limit(limit))
        return self

    def aggregate(
        self,
        *accumulators: ExprWithAlias[Accumulator],
        groups: Sequence[str | Selectable] = (),
    ) -> Pipeline:
        self.stages.append(stages.Aggregate(*accumulators, groups=groups))
        return self

    def distinct(self, *fields: str | Selectable) -> Pipeline:
        self.stages.append(stages.Distinct(*fields))
        return self

    def execute(self) -> Iterable["ExecutePipelineResponse"]:
        breakpoint()
        request = ExecutePipelineRequest(
            database=self._client._database,
            structured_pipeline=self._to_pb(),
            transaction=b"test",
        )
        results = self._client._firestore_api.execute_pipeline(request)
        print(request)
        return results

    async def execute_async(self) -> AsyncIterable["ExecutePipelineResponse"]:
        from google.cloud.firestore_v1.async_client import AsyncClient
        if not isinstance(self._client, AsyncClient):
            raise TypeError("execute_async requires AsyncClient")
        # TODO
        raise NotImplementedError
