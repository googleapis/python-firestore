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


def _make_pipeline(*args, client=mock.Mock()):
    from google.cloud.firestore_v1.pipeline import Pipeline

    return Pipeline(client, *args)


def test_ctor():
    from google.cloud.firestore_v1.pipeline import Pipeline

    client = object()
    stages = [object() for i in range(10)]
    instance = Pipeline(client, *stages)
    assert instance._client == client
    assert len(instance.stages) == 10
    assert instance.stages[0] == stages[0]
    assert instance.stages[-1] == stages[-1]


def test_pipeline_repr_empty():
    ppl = _make_pipeline()
    repr_str = repr(ppl)
    assert repr_str == "Pipeline()"


def test_pipeline_repr_single_stage():
    stage = mock.Mock()
    stage.__repr__ = lambda x: "SingleStage"
    ppl = _make_pipeline(stage)
    repr_str = repr(ppl)
    assert repr_str == "Pipeline(SingleStage)"


def test_pipeline_repr_multiple_stage():
    from google.cloud.firestore_v1.pipeline_stages import GenericStage, Collection

    stage_1 = Collection("path")
    stage_2 = GenericStage("second", 2)
    stage_3 = GenericStage("third", 3)
    ppl = _make_pipeline(stage_1, stage_2, stage_3)
    repr_str = repr(ppl)
    assert repr_str == (
        "Pipeline(\n"
        "  Collection(path='/path'),\n"
        "  GenericStage(name='second'),\n"
        "  GenericStage(name='third')\n"
        ")"
    )


def test_pipeline_repr_long():
    from google.cloud.firestore_v1.pipeline_stages import GenericStage

    num_stages = 100
    stage_list = [GenericStage("custom", i) for i in range(num_stages)]
    ppl = _make_pipeline(*stage_list)
    repr_str = repr(ppl)
    assert repr_str.count("GenericStage") == num_stages
    assert repr_str.count("\n") == num_stages + 1


def test_pipeline__to_pb():
    from google.cloud.firestore_v1.types.pipeline import StructuredPipeline
    from google.cloud.firestore_v1.pipeline_stages import GenericStage

    stage_1 = GenericStage("first")
    stage_2 = GenericStage("second")
    ppl = _make_pipeline(stage_1, stage_2)
    pb = ppl._to_pb()
    assert isinstance(pb, StructuredPipeline)
    assert pb.pipeline.stages[0] == stage_1._to_pb()
    assert pb.pipeline.stages[1] == stage_2._to_pb()


def test_pipeline_append():
    """append should create a new pipeline with the additional stage"""
    from google.cloud.firestore_v1.pipeline_stages import GenericStage

    stage_1 = GenericStage("first")
    ppl_1 = _make_pipeline(stage_1, client=object())
    stage_2 = GenericStage("second")
    ppl_2 = ppl_1._append(stage_2)
    assert ppl_1 != ppl_2
    assert len(ppl_1.stages) == 1
    assert len(ppl_2.stages) == 2
    assert ppl_2.stages[0] == stage_1
    assert ppl_2.stages[1] == stage_2
    assert ppl_1._client == ppl_2._client
    assert isinstance(ppl_2, type(ppl_1))


def test_pipeline_stream_empty():
    """
    test stream pipeline with mocked empty response
    """
    from google.cloud.firestore_v1.types import ExecutePipelineResponse
    from google.cloud.firestore_v1.types import ExecutePipelineRequest
    from google.cloud.firestore_v1.pipeline_stages import GenericStage

    client = mock.Mock()
    client.project = "A"
    client._database = "B"
    mock_rpc = client._firestore_api.execute_pipeline
    mock_rpc.return_value = [ExecutePipelineResponse()]
    ppl_1 = _make_pipeline(GenericStage("s"), client=client)

    results = list(ppl_1.stream())
    assert results == []
    assert mock_rpc.call_count == 1
    request = mock_rpc.call_args[0][0]
    assert isinstance(request, ExecutePipelineRequest)
    assert request.structured_pipeline == ppl_1._to_pb()
    assert request.database == "projects/A/databases/B"


def test_pipeline_stream_no_doc_ref():
    """
    test stream pipeline with no doc ref
    """
    from google.cloud.firestore_v1.types import Document
    from google.cloud.firestore_v1.types import ExecutePipelineResponse
    from google.cloud.firestore_v1.types import ExecutePipelineRequest
    from google.cloud.firestore_v1.pipeline_stages import GenericStage
    from google.cloud.firestore_v1.pipeline_result import PipelineResult

    client = mock.Mock()
    client.project = "A"
    client._database = "B"
    mock_rpc = client._firestore_api.execute_pipeline
    mock_rpc.return_value = [
        ExecutePipelineResponse(results=[Document()], execution_time={"seconds": 9})
    ]
    ppl_1 = _make_pipeline(GenericStage("s"), client=client)

    results = list(ppl_1.stream())
    assert len(results) == 1
    assert mock_rpc.call_count == 1
    request = mock_rpc.call_args[0][0]
    assert isinstance(request, ExecutePipelineRequest)
    assert request.structured_pipeline == ppl_1._to_pb()
    assert request.database == "projects/A/databases/B"

    response = results[0]
    assert isinstance(response, PipelineResult)
    assert response.ref is None
    assert response.id is None
    assert response.create_time is None
    assert response.update_time is None
    assert response.execution_time.seconds == 9
    assert response.data() == {}


def test_pipeline_stream_populated():
    """
    test stream pipeline with fully populated doc ref
    """
    from google.cloud.firestore_v1.types import Document
    from google.cloud.firestore_v1.types import ExecutePipelineResponse
    from google.cloud.firestore_v1.types import ExecutePipelineRequest
    from google.cloud.firestore_v1.types import Value
    from google.cloud.firestore_v1.client import Client
    from google.cloud.firestore_v1.document import DocumentReference
    from google.cloud.firestore_v1.pipeline_result import PipelineResult

    real_client = Client()
    client = mock.Mock()
    client.project = "A"
    client._database = "B"
    client.document = real_client.document
    mock_rpc = client._firestore_api.execute_pipeline

    mock_rpc.return_value = [
        ExecutePipelineResponse(
            results=[
                Document(
                    name="test/my_doc",
                    create_time={"seconds": 1},
                    update_time={"seconds": 2},
                    fields={"key": Value(string_value="str_val")},
                )
            ],
            execution_time={"seconds": 9},
        )
    ]
    ppl_1 = _make_pipeline(client=client)

    results = list(ppl_1.stream())
    assert len(results) == 1
    assert mock_rpc.call_count == 1
    request = mock_rpc.call_args[0][0]
    assert isinstance(request, ExecutePipelineRequest)
    assert request.structured_pipeline == ppl_1._to_pb()
    assert request.database == "projects/A/databases/B"
    assert request.transaction == b""

    response = results[0]
    assert isinstance(response, PipelineResult)
    assert isinstance(response.ref, DocumentReference)
    assert response.ref.path == "test/my_doc"
    assert response.id == "my_doc"
    assert response.create_time.seconds == 1
    assert response.update_time.seconds == 2
    assert response.execution_time.seconds == 9
    assert response.data() == {"key": "str_val"}


def test_pipeline_stream_multiple():
    """
    test stream pipeline with multiple docs and responses
    """
    from google.cloud.firestore_v1.types import Document
    from google.cloud.firestore_v1.types import ExecutePipelineResponse
    from google.cloud.firestore_v1.types import ExecutePipelineRequest
    from google.cloud.firestore_v1.types import Value
    from google.cloud.firestore_v1.client import Client
    from google.cloud.firestore_v1.pipeline_result import PipelineResult

    real_client = Client()
    client = mock.Mock()
    client.project = "A"
    client._database = "B"
    client.document = real_client.document
    mock_rpc = client._firestore_api.execute_pipeline

    mock_rpc.return_value = [
        ExecutePipelineResponse(
            results=[
                Document(fields={"key": Value(integer_value=0)}),
                Document(fields={"key": Value(integer_value=1)}),
            ],
            execution_time={"seconds": 0},
        ),
        ExecutePipelineResponse(
            results=[
                Document(fields={"key": Value(integer_value=2)}),
                Document(fields={"key": Value(integer_value=3)}),
            ],
            execution_time={"seconds": 1},
        ),
    ]
    ppl_1 = _make_pipeline(client=client)

    results = list(ppl_1.stream())
    assert len(results) == 4
    assert mock_rpc.call_count == 1
    request = mock_rpc.call_args[0][0]
    assert isinstance(request, ExecutePipelineRequest)
    assert request.structured_pipeline == ppl_1._to_pb()
    assert request.database == "projects/A/databases/B"

    for idx, response in enumerate(results):
        assert isinstance(response, PipelineResult)
        assert response.data() == {"key": idx}


def test_pipeline_stream_with_transaction():
    """
    test stream pipeline with fully populated doc ref
    """
    from google.cloud.firestore_v1.types import ExecutePipelineResponse
    from google.cloud.firestore_v1.types import ExecutePipelineRequest
    from google.cloud.firestore_v1.transaction import Transaction

    client = mock.Mock()
    client.project = "A"
    client._database = "B"
    mock_rpc = client._firestore_api.execute_pipeline

    transaction = Transaction(client)
    transaction._id = b"123"

    mock_rpc.return_value = [ExecutePipelineResponse()]
    ppl_1 = _make_pipeline(client=client)

    list(ppl_1.stream(transaction=transaction))
    assert mock_rpc.call_count == 1
    request = mock_rpc.call_args[0][0]
    assert isinstance(request, ExecutePipelineRequest)
    assert request.structured_pipeline == ppl_1._to_pb()
    assert request.database == "projects/A/databases/B"
    assert request.transaction == b"123"


def test_pipeline_execute_stream_equivalence():
    """
    Pipeline.execute should provide same results from pipeline.stream, as a list
    """
    from google.cloud.firestore_v1.types import Document
    from google.cloud.firestore_v1.types import ExecutePipelineResponse
    from google.cloud.firestore_v1.types import Value
    from google.cloud.firestore_v1.client import Client

    real_client = Client()
    client = mock.Mock()
    client.project = "A"
    client._database = "B"
    client.document = real_client.document
    mock_rpc = client._firestore_api.execute_pipeline

    mock_rpc.return_value = [
        ExecutePipelineResponse(
            results=[
                Document(
                    name="test/my_doc",
                    fields={"key": Value(string_value="str_val")},
                )
            ],
        )
    ]
    ppl_1 = _make_pipeline(client=client)

    stream_results = list(ppl_1.stream())
    execute_results = ppl_1.execute()
    assert stream_results == execute_results
    assert stream_results[0].data()["key"] == "str_val"
    assert execute_results[0].data()["key"] == "str_val"


def test_pipeline_execute_stream_equivalence_mocked():
    """
    pipeline.execute should call pipeline.stream internally
    """
    ppl_1 = _make_pipeline()
    expected_data = [object(), object()]
    expected_arg = object()
    with mock.patch.object(ppl_1, "stream") as mock_stream:
        mock_stream.return_value = expected_data
        stream_results = ppl_1.execute(expected_arg)
        assert mock_stream.call_count == 1
        assert mock_stream.call_args[0] == ()
        assert len(mock_stream.call_args[1]) == 1
        assert mock_stream.call_args[1]["transaction"] == expected_arg
        assert stream_results == expected_data
