from typing import Any, Dict, Iterable, List, Optional, Union

from google.cloud.firestore_v1.types import value
from google.cloud.firestore_v1.types.pipeline import Stage as GrpcStage
from google.cloud.firestore_v1.types.query import StructuredQuery

from google.cloud.firestore_v1.base_document import DocumentReference
from google.cloud.firestore_v1.field_path import FieldPath
from google.cloud.firestore_v1.pipeline import Pipeline
from google.cloud.firestore_v1.pipeline_expressions import (
    Accumulator,
    CompositeFilter,
    Direction,
    DistanceMeasure,
    Expr,
    ExprWithAlias,
    Field,
    FieldFilter,
    Filter,
    FilterCondition,
    Ordering,
    Scalar,
    Selectable,
    UnaryFilter,
)


class Stage:
    def __init__(self, custom_name: Optional[str] = None):
        self.name = custom_name or type(self).__name__.lower()


class AddFields(Stage):
    def __init__(self, fields: Dict[str, Expr]):
        super().__init__("add_fields")
        self.fields = fields

class Aggregate(Stage):
    def __init__(
        self,
        groups: Optional[Dict[str, Expr]] = None,
        accumulators: Optional[Dict[str, Accumulator]] = None,
    ):
        super().__init__()
        self.groups = groups or {}
        self.accumulators = accumulators or {}



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
    def __init__(self, groups: Dict[str, Expr]):
        super().__init__()
        self.groups = groups


class Documents(Stage):
    def __init__(self, documents: List[str]):
        super().__init__()
        self.documents = documents

    @staticmethod
    def of(*documents: DocumentReference) -> "Documents":
        doc_paths = ["/" + doc.path for doc in documents]
        return Documents(doc_paths)


class FindNearest(Stage):
    def __init__(
        self,
        property: Expr,
        vector: List[float],
        distance_measure: DistanceMeasure,
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
    def __init__(self, fields: List[Field]):
        super().__init__("remove_fields")
        self.fields = fields



class Replace(Stage):
    class Mode:
        FULL_REPLACE = value.Value(string_value="full_replace")
        MERGE_PREFER_NEXT = value.Value(string_value="merge_prefer_nest")
        MERGE_PREFER_PARENT = value.Value(string_value="merge_prefer_parent")

    def __init__(self, field: Selectable, mode: Mode = Mode.FULL_REPLACE):
        super().__init__()
        self.field = field
        self.mode = mode



class Sample(Stage):
    def __init__(self, options: "SampleOptions"):
        super().__init__()
        self.options = options



class Select(Stage):
    def __init__(self, projections: Dict[str, Expr]):
        super().__init__()
        self.projections = projections



class Sort(Stage):
    def __init__(self, orders: List[Ordering]):
        super().__init__()
        self.orders = orders



class Union(Stage):
    def __init__(self, other: Pipeline):
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



class FindNearestOptions:
    def __init__(
        self,
        limit: Optional[int] = None,
        distance_field: Optional[Field] = None,
    ):
        self.limit = limit
        self.distance_field = distance_field


class SampleOptions:
    class Mode:
        DOCUMENTS = value.Value(string_value="documents")
        PERCENT = value.Value(string_value="percent")

    def __init__(self, n: Union[int, float], mode: Mode):
        self.n = n
        self.mode = mode


class UnnestOptions:
    def __init__(self, index_field: str):
        self.index_field = index_field
