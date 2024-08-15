# Copyright 2024 Google LLC All rights reserved.
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

from google.cloud.firestore_v1.query_profile import (
    ExplainMetrics,
    ExplainOptions,
    QueryExplainError,
)


from typing import List, Optional, TypeVar


T = TypeVar("T")


class QueryResultsList(list):
    """A list of received query results from the query call.

    This is a subclass of the built-in list. A new property `explain_metrics`
    is added to return the query profile results.

    Args:
        docs (list[T]):
            The list of query results.
        explain_options
            (Optional[:class:`~google.cloud.firestore_v1.query_profile.ExplainOptions`]):
            Options to enable query profiling for this query. When set,
            explain_metrics will be available on the returned generator.
        explain_metrics (Optional[ExplainMetrics]):
            Query profile results.
    """

    def __init__(
        self,
        docs: List,
        explain_options: Optional[ExplainOptions] = None,
        explain_metrics: Optional[ExplainMetrics] = None,
    ):
        super().__init__(docs)
        self._explain_options = explain_options
        self._explain_metrics = explain_metrics

    @property
    def explain_options(self):
        return self._explain_options

    @property
    def explain_metrics(self):
        if self._explain_options is None:
            raise QueryExplainError("explain_options not set on query.")
        else:
            return self._explain_metrics