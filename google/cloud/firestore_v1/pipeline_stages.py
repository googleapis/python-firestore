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
from typing import Optional, TYPE_CHECKING
from abc import ABC
from abc import abstractmethod

from google.cloud.firestore_v1.types.document import Pipeline as Pipeline_pb
from google.cloud.firestore_v1.types.document import Value
from google.cloud.firestore_v1.pipeline_expressions import Expr

if TYPE_CHECKING:
    from google.cloud.firestore_v1.base_document import BaseDocumentReference


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


class Collection(Stage):
    """Specifies a collection as the initial data source."""

    def __init__(self, path: str):
        super().__init__()
        if not path.startswith("/"):
            path = f"/{path}"
        self.path = path

    def _pb_args(self):
        return [Value(reference_value=self.path)]


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