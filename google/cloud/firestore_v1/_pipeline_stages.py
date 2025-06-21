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
from typing import Optional, Sequence
from abc import ABC
from abc import abstractmethod

from google.cloud.firestore_v1.types.document import Pipeline as Pipeline_pb
from google.cloud.firestore_v1.types.document import Value
from google.cloud.firestore_v1.pipeline_expressions import (
    Accumulator,
    Expr,
    ExprWithAlias,
    Field,
    FilterCondition,
    Selectable,
    Ordering,
)


class Stage(ABC):
    """Base class for all pipeline stages.

    Each stage represents a specific operation (e.g., filtering, sorting,
    transforming) within a Firestore pipeline. Subclasses define the specific
    arguments and behavior for each operation.
    """

    def __init__(self, custom_name: Optional[str] = None):
        self.name = custom_name or type(self).__name__.lower()

    def _to_pb(self) -> Pipeline_pb.Stage:
        return Pipeline_pb.Stage(
            name=self.name, args=self._pb_args(), options=self._pb_options()
        )

    @abstractmethod
    def _pb_args(self) -> list[Value]:
        """Return Ordered list of arguments the given stage expects"""
        raise NotImplementedError

    def _pb_options(self) -> dict[str, Value]:
        """Return optional named arguments that certain functions may support."""
        return {}

    def __repr__(self):
        items = ("%s=%r" % (k, v) for k, v in self.__dict__.items() if k != "name")
        return f"{self.__class__.__name__}({', '.join(items)})"


class Aggregate(Stage):
    """Performs aggregation operations, optionally grouped."""

    def __init__(
        self,
        *args: ExprWithAlias[Accumulator],
        accumulators: Sequence[ExprWithAlias[Accumulator]] = (),
        groups: Sequence[str | Selectable] = (),
    ):
        super().__init__()
        self.groups: list[Selectable] = [
            Field(f) if isinstance(f, str) else f for f in groups
        ]
        if args and accumulators:
            raise ValueError(
                "Aggregate stage contains both positional and keyword accumulators"
            )
        self.accumulators = args or accumulators

    def _pb_args(self):
        return [
            Value(
                map_value={
                    "fields": {
                        m[0]: m[1] for m in [f._to_map() for f in self.accumulators]
                    }
                }
            ),
            Value(
                map_value={
                    "fields": {m[0]: m[1] for m in [f._to_map() for f in self.groups]}
                }
            ),
        ]

    def __repr__(self):
        accumulator_str = ", ".join(repr(v) for v in self.accumulators)
        group_str = ""
        if self.groups:
            if self.accumulators:
                group_str = ", "
            group_str += f"groups={self.groups}"
        return f"{self.__class__.__name__}({accumulator_str}{group_str})"


class Collection(Stage):
    """Specifies a collection as the initial data source."""

    def __init__(self, path: str):
        super().__init__()
        if not path.startswith("/"):
            path = f"/{path}"
        self.path = path

    def _pb_args(self):
        return [Value(reference_value=self.path)]


class CollectionGroup(Stage):
    """Specifies a collection group as the initial data source."""

    def __init__(self, collection_id: str):
        super().__init__("collection_group")
        self.collection_id = collection_id

    def _pb_args(self):
        return [Value(string_value=self.collection_id)]


class GenericStage(Stage):
    """Represents a generic, named stage with parameters."""

    def __init__(self, name: str, *params: Expr | Value):
        super().__init__(name)
        self.params: list[Value] = [
            p._to_pb() if isinstance(p, Expr) else p for p in params
        ]

    def _pb_args(self):
        return self.params

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"


class Limit(Stage):
    """Limits the maximum number of documents returned."""

    def __init__(self, limit: int):
        super().__init__()
        self.limit = limit

    def _pb_args(self):
        return [Value(integer_value=self.limit)]


class Offset(Stage):
    """Skips a specified number of documents."""

    def __init__(self, offset: int):
        super().__init__()
        self.offset = offset

    def _pb_args(self):
        return [Value(integer_value=self.offset)]


class Select(Stage):
    """Selects or creates a set of fields."""

    def __init__(self, *selections: str | Selectable):
        super().__init__()
        self.projections = [Field(s) if isinstance(s, str) else s for s in selections]

    def _pb_args(self) -> list[Value]:
        return [Selectable._value_from_selectables(*self.projections)]


class Sort(Stage):
    """Sorts documents based on specified criteria."""

    def __init__(self, *orders: "Ordering"):
        super().__init__()
        self.orders = list(orders)

    def _pb_args(self):
        return [o._to_pb() for o in self.orders]


class Where(Stage):
    """Filters documents based on a specified condition."""

    def __init__(self, condition: FilterCondition):
        super().__init__()
        self.condition = condition

    def _pb_args(self):
        return [self.condition._to_pb()]
