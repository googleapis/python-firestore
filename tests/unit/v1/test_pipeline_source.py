# Copyright 2025 Google LLC All rights reserved.
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
# limitations under the License

import mock
import pytest

from google.cloud.firestore_v1.pipeline_source import PipelineSource
from google.cloud.firestore_v1.pipeline import Pipeline
from google.cloud.firestore_v1.async_pipeline import AsyncPipeline
from google.cloud.firestore_v1.client import Client
from google.cloud.firestore_v1.async_client import AsyncClient
from google.cloud.firestore_v1 import pipeline_stages as stages


class TestPipelineSource:
    _expected_pipeline_type = Pipeline

    def _make_client(self):
        return Client()

    def test_make_from_client(self):
        instance = self._make_client().pipeline()
        assert isinstance(instance, PipelineSource)

    def test_create_pipeline(self):
        instance = self._make_client().pipeline()
        ppl = instance._create_pipeline(None)
        assert isinstance(ppl, self._expected_pipeline_type)

    def test_collection(self):
        instance = self._make_client().pipeline()
        ppl = instance.collection("path")
        assert isinstance(ppl, self._expected_pipeline_type)
        assert len(ppl.stages) == 1
        first_stage = ppl.stages[0]
        assert isinstance(first_stage, stages.Collection)
        assert first_stage.path == "/path"


class TestPipelineSourceWithAsyncClient(TestPipelineSource):
    """
    When an async client is used, it should produce async pipelines
    """

    _expected_pipeline_type = AsyncPipeline

    def _make_client(self):
        return AsyncClient()
