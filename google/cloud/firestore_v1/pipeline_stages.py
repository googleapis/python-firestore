from __future__ import annotations
from typing import Any, Dict, Iterable, List, Optional, Sequence
from enum import Enum
from enum import auto

from google.cloud.firestore_v1.pipeline_expressions import (
    Accumulator,
    Expr,
    ExprWithAlias,
    Field,
    FilterCondition,
    Selectable,
)

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

    def __repr__(self):
        items = ("%s=%r" % (k, v) for k, v in self.__dict__.items() if k != "name")
        return f"{self.__class__.__name__}({', '.join(items)})"


class AddFields(Stage):
    def __init__(self, *fields: Selectable):
        super().__init__("add_fields")
        self.fields = list(fields)

    def _fields_map(self) -> dict[str, Expr]:
        return dict(f._to_map() for f in self.fields)


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

    @property
    def _group_map(self) -> dict[str, Expr]:
        return dict(f._to_map() for f in self.groups)

    @property
    def _accumulators_map(self) -> dict[str, Expr]:
        return dict(f._to_map() for f in self.accumulators)


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
            path = "/" + path
        self.path = path


class CollectionGroup(Stage):
    def __init__(self, collection_id: str):
        super().__init__("collection_group")
        self.collection_id = collection_id


class Database(Stage):
    def __init__(self):
        super().__init__()


class Distinct(Stage):
    def __init__(self, *fields: str | Selectable):
        super().__init__()
        self.fields: list[Selectable] = [Field(f) if isinstance(f, str) else f for f in fields]

    @property
    def _fields_dict(self) -> dict[str, Selectable]:
        return dict(
            f._to_map()
            if isinstance(f, Selectable)
            else (f,Field(f))
            for f in self.fields
        )


class Documents(Stage):
    def __init__(self, *documents: str):
        super().__init__()
        self.documents = list(documents)

    @staticmethod
    def of(*documents: "DocumentReference") -> "Documents":
        doc_paths = ["/" + doc.path for doc in documents]
        return Documents(doc_paths)


class FindNearest(Stage):
    def __init__(
        self,
        property: Expr,
        vector: List[float],
        distance_measure: "DistanceMeasure",
        options: Optional["FindNearestOptions"] = None,
    ):
        super().__init__("find_nearest")
        self.property = property
        self.vector = vector
        self.distance_measure = distance_measure
        self.options = options or FindNearestOptions()


class GenericStage(Stage):
    def __init__(self, name: str, *params: Any):
        super().__init__(name)
        self.params = list(params)


class Limit(Stage):
    def __init__(self, limit: int):
        super().__init__()
        self.limit = limit


class Offset(Stage):
    def __init__(self, offset: int):
        super().__init__()
        self.offset = offset


class RemoveFields(Stage):
    def __init__(self, *fields: str | Field):
        super().__init__("remove_fields")
        self.fields = [Field(f) if isinstance(f, str) else f for f in fields]

    @property
    def _fields_map(self) -> dict[str, Field]:
        dict(f._to_map() for f in self.fields)


class Replace(Stage):
    class Mode(Enum):
        FULL_REPLACE = "full_replace"
        MERGE_PREFER_NEXT = "merge_prefer_nest"
        MERGE_PREFER_PARENT = "merge_prefer_parent"

    def __init__(self, field: Selectable, mode: Mode = Mode.FULL_REPLACE):
        super().__init__()
        self.field = field
        self.mode = mode


class Sample(Stage):

    class Mode(Enum):
        DOCUMENTS = auto()
        PERCENTAGE = auto()

    def __init__(self, n: int, mode: Mode = Mode.DOCUMENTS):
        super().__init__()
        self.n = n
        self.mode = mode

class Select(Stage):
    def __init__(self, *fields: str | Selectable):
        super().__init__()
        self.projections = [Field(f) if isinstance(f, str) else f for f in fields]

    @property
    def _projections_map(self) -> dict[str, Expr]:
        return dict(f._to_map() for f in self.projections)




class Sort(Stage):
    def __init__(self, *orders: "Ordering"):
        super().__init__()
        self.orders = list(orders)


class Union(Stage):
    def __init__(self, other: "Pipeline"):
        super().__init__()
        self.other = other


class Unnest(Stage):
    def __init__(self, field: Field, options: Optional["UnnestOptions"] = None):
        super().__init__()
        self.field = field
        self.options = options


class Where(Stage):
    def __init__(self, condition: FilterCondition):
        super().__init__()
        self.condition = condition

