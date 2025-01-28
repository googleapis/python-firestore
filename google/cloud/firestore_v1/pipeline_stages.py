from __future__ import annotations
from typing import Any, Dict, Iterable, List, Optional, Sequence
from enum import Enum

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


class SampleOptions:
    class Mode(Enum):
        DOCUMENTS = "documents"
        PERCENT = "percent"

    def __init__(self, n: int | float, mode: Mode):
        self.n = n
        self.mode = mode


class UnnestOptions:
    def __init__(self, index_field: str):
        self.index_field = index_field


class Stage:
    def __init__(self, custom_name: Optional[str] = None):
        self.name = custom_name or type(self).__name__.lower()


class AddFields(Stage):
    def __init__(self, *fields: Selectable):
        super().__init__("add_fields")
        self.fields = dict(f._to_map() for f in fields)


class Aggregate(Stage):
    def __init__(
        self,
        *extra_accumulators: ExprWithAlias[Accumulator],
        accumulators: Sequence[ExprWithAlias[Accumulator]] = (),
        groups: Sequence[str | Selectable] = (),
    ):
        super().__init__()
        self.groups: dict[str, Expr] = dict(
            f._to_map()
            if isinstance(f, Selectable)
            else (f,Field(f))
            for f in groups
        )
        self.accumulators: dict[str, Expr] = dict(f._to_map() for f in [*accumulators, *extra_accumulators])


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
        self.fields = dict(
            f._to_map()
            if isinstance(f, Selectable)
            else (f,Field(f))
            for f in fields
        )


class Documents(Stage):
    def __init__(self, documents: List[str]):
        super().__init__()
        self.documents = documents

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
    def __init__(self, name: str, params: List[Any]):
        super().__init__(name)
        self.params = params


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
        self.fields = dict(
            f._to_map()
            if isinstance(f, Selectable)
            else (f,Field(f))
            for f in fields
        )


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
    def __init__(self, options: "SampleOptions"):
        super().__init__()
        self.options = options


class Select(Stage):
    def __init__(self, *fields: str | Selectable):
        super().__init__()
        self.projections = dict(
            f._to_map()
            if isinstance(f, Selectable)
            else (f,Field(f))
            for f in fields
        )




class Sort(Stage):
    def __init__(self, orders: List["Ordering"]):
        super().__init__()
        self.orders = orders


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

