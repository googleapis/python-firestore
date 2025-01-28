from __future__ import annotations
from typing import Any, Dict, Iterable, List, Optional
from google.cloud.firestore_v1 import pipeline_stages as stages

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
    def __init__(self, *stages: stages.Stage):
        self.stages = list(stages)

    def __repr__(self):
        if not self.stages:
            return "Pipeline()"
        elif len(self.stages) == 1:
            return f"Pipeline({self.stages[0]!r})"
        else:
            stages_str = ",\n  ".join([repr(s) for s in self.stages])
            return f"Pipeline(\n  {stages_str}\n)"

    def add_fields(self, fields: Dict[str, Expr]) -> Pipeline:
        self.stages.append(stages.AddFields(fields))
        return self

    def remove_fields(self, fields: List[Field]) -> Pipeline:
        self.stages.append(stages.RemoveFields(fields))
        return self

    def select(self, projections: Dict[str, Expr]) -> Pipeline:
        self.stages.append(stages.Select(projections))
        return self

    def where(self, condition: FilterCondition) -> Pipeline:
        self.stages.append(stages.Where(condition))
        return self

    def find_nearest(
        self,
        field: str | Expr,
        vector: "Vector",
        distance_measure: "FindNearest.DistanceMeasure",
        limit: int | None,
        options: Optional[stages.FindNearestOptions] = None,
    ) -> Pipeline:
        self.stages.append(stages.FindNearest(field, vector, distance_measure, options))
        return self

    def sort(self, orders: List[stages.Ordering]) -> Pipeline:
        self.stages.append(stages.Sort(orders))
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

    def generic_stage(self, name: str, params: List[Any]) -> Pipeline:
        self.stages.append(stages.GenericStage(name, params))
        return self

    def offset(self, offset: int) -> Pipeline:
        self.stages.append(stages.Offset(offset))
        return self

    def limit(self, limit: int) -> Pipeline:
        self.stages.append(stages.Limit(limit))
        return self

    def aggregate(
        self,
        accumulators: Optional[Dict[str, Accumulator]] = None,
    ) -> Pipeline:
        self.stages.append(stages.Aggregate(accumulators=accumulators))
        return self

    def distinct(self, fields: Dict[str, Expr]) -> Pipeline:
        self.stages.append(stages.Distinct(fields))
        return self

    def execute(self) -> list["PipelineResult"]:
        return []

    async def execute_async(self) -> List["PipelineResult"]:
        return []
