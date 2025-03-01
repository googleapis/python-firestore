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
from typing import Any, Dict, Iterable, List, Optional, Sequence, TYPE_CHECKING
from enum import Enum
from enum import auto

from google.cloud.firestore_v1.types.document import Pipeline as Pipeline_pb
from google.cloud.firestore_v1.types.document import Value
from google.cloud.firestore_v1.document import DocumentReference
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
    Ordering
)

if TYPE_CHECKING:
    from google.cloud.firestore_v1.pipeline import Pipeline


class FindNearestOptions:
    def __init__(
        self,
        limit: Optional[int] = None,
        distance_field: Optional[Field] = None,
    ):
        self.limit = limit
        self.distance_field = distance_field


class UnnestOptions:
    def __init__(self, index_field: str):
        self.index_field = index_field


class Stage:
    def __init__(self, custom_name: Optional[str] = None):
        self.name = custom_name or type(self).__name__.lower()

    def _to_pb(self) -> Pipeline_pb.Stage:
        return Pipeline_pb.Stage(name=self.name, args=self._pb_args(), options=self._pb_options())

    def _pb_args(self) -> list[Value]:
        """Return Ordered list of arguments the given stage expects"""
        return []

    def _pb_options(self) -> dict[str, Value]:
        """Return optional named arguments that certain functions may support."""
        return {}

    def __repr__(self):
        items = ("%s=%r" % (k, v) for k, v in self.__dict__.items() if k != "name")
        return f"{self.__class__.__name__}({', '.join(items)})"


class AddFields(Stage):
    def __init__(self, *fields: Selectable):
        super().__init__("add_fields")
        self.fields = list(fields)

    def _pb_args(self):
        return [Value(map_value={"fields": {m[0]: m[1] for m in [f._to_map() for f in self.fields]}})]

class Aggregate(Stage):
    def __init__(
        self,
        *extra_accumulators: ExprWithAlias[Accumulator],
        accumulators: Sequence[ExprWithAlias[Accumulator]] = (),
        groups: Sequence[str | Selectable] = (),
    ):
        super().__init__()
        self.groups: list[Selectable] = [Field(f) if isinstance(f, str) else f for f in groups]
        self.accumulators: list[ExprWithAlias[Accumulator]] = [*accumulators, *extra_accumulators]

    def _pb_args(self):
        return [
            Value(map_value={"fields": {m[0]: m[1] for m in [f._to_map() for f in self.accumulators]}}),
            Value(map_value={"fields": {m[0]: m[1] for m in [f._to_map() for f in self.groups]}})
        ]

    def __repr__(self):
        accumulator_str = ', '.join(repr(v) for v in self.accumulators)
        group_str = ""
        if self.groups:
            if self.accumulators:
                group_str = ", "
            group_str += f"groups={self.groups}"
        return f"{self.__class__.__name__}({accumulator_str}{group_str})"


class Collection(Stage):
    def __init__(self, path: str):
        super().__init__()
        if not path.startswith("/"):
            path = f"/{path}"
        self.path = path

    def _pb_args(self):
        return [Value(reference_value=self.path)]

class CollectionGroup(Stage):
    def __init__(self, collection_id: str):
        super().__init__("collection_group")
        self.collection_id = collection_id

    def _pb_args(self):
        return [Value(string_value=self.collection_id)]


class Database(Stage):
    def __init__(self):
        super().__init__()

class Distinct(Stage):
    def __init__(self, *fields: str | Selectable):
        super().__init__()
        self.fields: list[Selectable] = [Field(f) if isinstance(f, str) else f for f in fields]

    def _pb_args(self) -> list[Value]:
        return [Value(map_value={"fields": {m[0]: m[1] for m in [f._to_map() for f in self.fields]}})]


class Documents(Stage):
    def __init__(self, *paths: str):
        super().__init__()
        self.paths = paths

    @staticmethod
    def of(*documents: "DocumentReference") -> "Documents":
        doc_paths = ["/" + doc.path for doc in documents]
        return Documents(*doc_paths)

    def _pb_args(self):
        return [Value(list_value={"values": [Value(string_value=path) for path in self.paths]})]


class FindNearest(Stage):
    def __init__(
        self,
        field: str | Expr,
        vector: Sequence[float] | Vector,
        distance_measure: "DistanceMeasure",
        options: Optional["FindNearestOptions"] = None,
    ):
        super().__init__("find_nearest")
        self.field: Expr = Field(field) if isinstance(field, str) else field
        self.vector: Vector = vector if isinstance(vector, Vector) else Vector(vector)
        self.distance_measure = distance_measure
        self.options = options or FindNearestOptions()

    def _pb_args(self):
        return [
            self.field._to_pb(),
            Value(array_value={"values": self.vector}),
            Value(string_value=self.distance_measure.value),
        ]

    def _pb_options(self) -> dict[str, Value]:
        options = {}
        if self.options and self.options.limit is not None:
            options["limit"] = Value(integer_value=self.options.limit)
        if self.options and self.options.distance_field is not None:
            options["distance_field"] = self.options.distance_field._to_pb()
        return options

class GenericStage(Stage):
    def __init__(self, name: str, *params: Expr | Value):
        super().__init__(name)
        self.params: list[Value] = [p._to_pb() if isinstance(p, Expr) else p for p in params]

    def _pb_args(self):
        return self.params


class Limit(Stage):
    def __init__(self, limit: int):
        super().__init__()
        self.limit = limit

    def _pb_args(self):
        return [Value(integer_value=self.limit)]


class Offset(Stage):
    def __init__(self, offset: int):
        super().__init__()
        self.offset = offset

    def _pb_args(self):
        return [Value(integer_value=self.offset)]


class RemoveFields(Stage):
    def __init__(self, *fields: str | Field):
        super().__init__("remove_fields")
        self.fields = [Field(f) if isinstance(f, str) else f for f in fields]

    def _pb_args(self) -> list[Value]:
        return [Value(map_value={"fields": {m[0]: m[1] for m in [f._to_map() for f in self.fields]}})]


class Replace(Stage):
    class Mode(Enum):
        FULL_REPLACE = "full_replace"
        MERGE_PREFER_NEXT = "merge_prefer_nest"
        MERGE_PREFER_PARENT = "merge_prefer_parent"

    def __init__(self, field: Selectable | str, mode: Mode | str = Mode.FULL_REPLACE):
        super().__init__()
        self.field = Field(field) if isinstance(field, str) else field
        self.mode = self.Mode[mode] if isinstance(mode, str) else mode

    def _pb_args(self):
        return [self.field._to_pb(), Value(string_value=self.mode.value)]


class Sample(Stage):

    def __init__(self, limit_or_options: int | SampleOptions):
        super().__init__()
        if isinstance(limit_or_options, int):
            options = SampleOptions(limit_or_options, SampleOptions.Mode.DOCUMENTS)
        else:
            options = limit_or_options
        self.options: SampleOptions = options

    def _pb_args(self):
        return [Value(integer_value=self.options.n), Value(string_value=self.options.mode.value)]


class Select(Stage):
    def __init__(self, *selections: str | Selectable):
        super().__init__()
        self.projections = [Field(s) if isinstance(s, str) else s for s in selections]

    def _pb_args(self) -> list[Value]:
        return [Value(map_value={"fields": {m[0]: m[1] for m in [f._to_map() for f in self.projections]}})]


class Sort(Stage):
    def __init__(self, *orders: "Ordering"):
        super().__init__()
        self.orders = list(orders)

    def _pb_args(self):
        return [o._to_pb() for o in self.orders]


class Union(Stage):
    def __init__(self, other: Pipeline):
        super().__init__()
        self.other = other

    def _pb_args(self):
        return [Value(pipeline_value=self.other._to_pb())]


class Unnest(Stage):
    def __init__(self, field: Field | str, options: Optional["UnnestOptions"] = None):
        super().__init__()
        self.field: Field = Field(field) if isinstance(field, str) else field
        self.options = options

    def _pb_args(self):
        return [self.field._to_pb()]

    def _pb_options(self):
        options = {}
        if self.options is not None:
            options["index_field"] = Value(string_value=self.options.index_field)
        return options


class Where(Stage):
    def __init__(self, condition: FilterCondition):
        super().__init__()
        self.condition = condition

    def _pb_args(self):
        return [self.condition._to_pb()]

