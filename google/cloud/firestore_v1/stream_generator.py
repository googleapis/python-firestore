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

"""Classes for iterating over stream results for the Google Cloud Firestore API.
"""

from collections import abc

from google.cloud.firestore_v1.query_profile import ExplainMetrics, QueryExplainError
import google.cloud.firestore_v1.types.query_profile as query_profile_proto

class StreamGenerator(abc.Generator):
    """Generator for the streamed results."""

    def __init__(self, response_generator=None, explain_options=None):
        self._generator = response_generator
        self._explain_options = explain_options
        self._explain_metrics = None

    def __iter__(self):
        return self

    def __next__(self):
        next_value = self._generator.__next__()
        if type(next_value) is query_profile_proto.ExplainMetrics:
            self._explain_metrics = ExplainMetrics._from_pb(next_value)
            return self._generator.__next__()
        else:
            return next_value

    def send(self, value=None):
        return self._generator.send(value)

    def throw(self, exp=None):
        return self._generator.throw(exp)

    def close(self):
        return self._generator.close()

    @property
    def explain_metrics(self) -> ExplainMetrics:
        """
        Get the metrics associated with the query execution.
        Metrics are only available when explain_options is set on the query. If
        ExplainOptions.analyze is False, only plan_summary is available. If it is
        True, execution_stats is also available.
        :rtype: :class:`~google.cloud.datastore.query_profile.ExplainMetrics`
        :returns: The metrics associated with the query execution.
        :raises: :class:`~google.cloud.datastore.query_profile.QueryExplainError`
            if explain_metrics is not available on the query.
        """
        if self._explain_metrics is not None:
            return self._explain_metrics
        elif self._explain_options is None:
            raise QueryExplainError("explain_options not set on query.")
        elif self._explain_options.analyze is False:
            # we need to run the query to get the explain_metrics
            next(self)
            return self._explain_metrics
        raise QueryExplainError(
            "explain_metrics not available until query is complete."
        )
