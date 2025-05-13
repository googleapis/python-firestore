# -*- coding: utf-8 -*-
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
#
from __future__ import annotations

from typing import MutableMapping, MutableSequence

import proto  # type: ignore

from google.protobuf import any_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.firestore.v1",
    manifest={
        "ExplainStats",
    },
)


class ExplainStats(proto.Message):
    r"""Explain stats for an RPC request, includes both the optimized
    plan and execution stats.

    Attributes:
        data (google.protobuf.any_pb2.Any):
            The format depends on the ``output_format`` options in the
            request.

            The only option today is ``TEXT``, which is a
            ``google.protobuf.StringValue``.
    """

    data: any_pb2.Any = proto.Field(
        proto.MESSAGE,
        number=1,
        message=any_pb2.Any,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
