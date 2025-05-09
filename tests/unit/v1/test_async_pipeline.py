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

def _make_async_pipeline(*args, client=mock.Mock()):
    from google.cloud.firestore_v1.async_pipeline import AsyncPipeline

    return AsyncPipeline(client, *args)

def test_ctor():
    from google.cloud.firestore_v1.async_pipeline import AsyncPipeline
    client = object()
    stages = [object() for i in range(10)]
    instance = AsyncPipeline(client, *stages)
    assert instance._client == client
    assert len(instance.stages) == 10
    assert instance.stages[0] == stages[0]
    assert instance.stages[-1] == stages[-1]

def test_async_pipeline_repr_empty():
    ppl = _make_async_pipeline()
    repr_str = repr(ppl)
    assert repr_str == "AsyncPipeline()"

def test_async_pipeline_repr_single_stage():
    stage = mock.Mock()
    stage.__repr__ = lambda x: "SingleStage"
    ppl = _make_async_pipeline(stage)
    repr_str = repr(ppl)
    assert repr_str == 'AsyncPipeline(SingleStage)'

def test_async_pipeline_repr_multiple_stage():
    from google.cloud.firestore_v1.pipeline_stages import GenericStage, Collection
    stage_1 = Collection("path")
    stage_2 = GenericStage("second", 2)
    stage_3 = GenericStage("third", 3)
    ppl = _make_async_pipeline(stage_1, stage_2, stage_3)
    repr_str = repr(ppl)
    assert repr_str == (
        "AsyncPipeline(\n"
        "  Collection(path='/path'),\n"
        "  GenericStage(params=[2]),\n"
        "  GenericStage(params=[3])\n"
        ")"
    )

def test_async_pipeline_repr_long():
    from google.cloud.firestore_v1.pipeline_stages import GenericStage
    num_stages = 100
    stage_list = [GenericStage("custom", i) for i in range(num_stages)]
    ppl = _make_async_pipeline(*stage_list)
    repr_str = repr(ppl)
    assert repr_str.count("GenericStage") == num_stages
    assert repr_str.count('\n') == num_stages+1

def test_async_pipeline__to_pb():
    from google.cloud.firestore_v1.types.pipeline import StructuredPipeline
    from google.cloud.firestore_v1.pipeline_stages import GenericStage
    stage_1 = GenericStage("first")
    stage_2 = GenericStage("second")
    ppl = _make_async_pipeline(stage_1, stage_2)
    pb = ppl._to_pb()
    assert isinstance(pb, StructuredPipeline)
    assert pb.pipeline.stages[0] == stage_1._to_pb()
    assert pb.pipeline.stages[1] == stage_2._to_pb()

def test_async_pipeline_append():
    """append should create a new pipeline with the additional stage"""
    from google.cloud.firestore_v1.pipeline_stages import GenericStage
    stage_1 = GenericStage("first")
    ppl_1 = _make_async_pipeline(stage_1, client=object())
    stage_2 = GenericStage("second")
    ppl_2 = ppl_1._append(stage_2)
    assert ppl_1 != ppl_2
    assert len(ppl_1.stages) == 1
    assert len(ppl_2.stages) == 2
    assert ppl_2.stages[0] == stage_1
    assert ppl_2.stages[1] == stage_2
    assert ppl_1._client == ppl_2._client
    assert isinstance(ppl_2, type(ppl_1))