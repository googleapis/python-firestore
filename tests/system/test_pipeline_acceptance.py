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
import sys
import os
import pytest
import yaml
import re
from typing import Any
from contextlib import nullcontext

from google.protobuf.json_format import MessageToDict

# from google.cloud.firestore_v1.pipeline_stages import *
from google.cloud.firestore_v1 import pipeline_stages
from google.cloud.firestore_v1 import pipeline_expressions
from google.cloud.firestore_v1.pipeline import Pipeline
from google.api_core.exceptions import GoogleAPIError

from google.cloud.firestore import Client

FIRESTORE_TEST_DB = os.environ.get("SYSTEM_TESTS_DATABASE", "system-tests-named-db")
FIRESTORE_PROJECT = os.environ.get("GCLOUD_PROJECT")

test_dir_name = os.path.dirname(__file__)

def yaml_loader(field="tests"):
    """
    loads test cases or data from yaml file
    """
    with open(f"{test_dir_name}/pipeline_e2e.yaml") as f:
        test_cases = yaml.safe_load(f)
    return test_cases[field]

@pytest.fixture
def client():
    client = Client(project=FIRESTORE_PROJECT, database=FIRESTORE_TEST_DB)
    data = yaml_loader("data")
    try:
        # setup data
        batch = client.batch()
        for collection_name, documents in data.items():
            collection_ref = client.collection(collection_name)
            for document_id, document_data in documents.items():
                document_ref = collection_ref.document(document_id)
                batch.set(document_ref, document_data)
        batch.commit()

        yield client

    finally:
        # clear data
        for collection_name, documents in data.items():
            collection_ref = client.collection(collection_name)
            for document_id in documents:
                document_ref = collection_ref.document(document_id)
                document_ref.delete()


def _apply_yaml_args(cls, client, yaml_args):
    if isinstance(yaml_args, dict):
        return cls(**parse_expressions(client, yaml_args))
    elif isinstance(yaml_args, list):
        # yaml has an array of arguments. Treat as args
        return cls(*parse_expressions(client, yaml_args))
    else:
        # yaml has a single argument
        return cls(parse_expressions(client, yaml_args))

def parse_pipeline(client, pipeline: list[dict[str, Any], str]):
    """
    parse a yaml list of pipeline stages into firestore.pipeline_stages.Stage classes
    """
    result_list = []
    for stage in pipeline:
        # stage will be either a map of the stage_name and its args, or just the stage_name itself
        stage_name: str = stage if isinstance(stage, str) else list(stage.keys())[0]
        stage_cls: type[pipeline_stages.Stage] = getattr(pipeline_stages, stage_name)
        # breakpoint()
        # find arguments if given
        if isinstance(stage, dict):
            stage_yaml_args = stage[stage_name]
            stage_obj = _apply_yaml_args(stage_cls, client, stage_yaml_args)
        else:
            # yaml has no arguments
            stage_obj = stage_cls()
        result_list.append(stage_obj)
    return Pipeline(client, *result_list)

def _is_expr_string(yaml_str):
    return isinstance(yaml_str, str) and \
            yaml_str[0].isupper() and \
            hasattr(pipeline_expressions, yaml_str)

def parse_expressions(client, yaml_element: Any):
    if isinstance(yaml_element, list):
        return [parse_expressions(client, v) for v in yaml_element]
    elif isinstance(yaml_element, dict):
        if len(yaml_element) == 1 and _is_expr_string(list(yaml_element)[0]):
            # build pipeline expressions if possible
            cls_str = list(yaml_element)[0]
            cls = getattr(pipeline_expressions, cls_str)
            yaml_args = yaml_element[cls_str]
            return _apply_yaml_args(cls, client, yaml_args)
        elif len(yaml_element) == 1 and list(yaml_element)[0] == "Pipeline":
            # find Pipeline objects for Union expressions
            other_ppl = yaml_element["Pipeline"]
            return parse_pipeline(client, other_ppl)
        else:
            # otherwise, return dict
            return {parse_expressions(client, k): parse_expressions(client, v) for k,v in yaml_element.items()}
    elif _is_expr_string(yaml_element):
        return getattr(pipeline_expressions, yaml_element)()
    else:
        return yaml_element

@pytest.mark.parametrize(
    "test_dict", yaml_loader(), ids=lambda x: f"{x.get('description', '')}"
)
def test_e2e_scenario(test_dict, client):
    error_regex = test_dict.get("assert_error", None)
    expected_proto = test_dict.get("assert_proto", None)
    expected_results = test_dict.get("assert_results", None)
    pipeline = parse_pipeline(client, test_dict["pipeline"])
    # check if proto matches as expected
    if expected_proto:
        got_proto = MessageToDict(pipeline._to_pb()._pb)
        assert yaml.dump(expected_proto) == yaml.dump(got_proto)
    # check if server responds as expected
    with pytest.raises(GoogleAPIError) if error_regex else nullcontext() as ctx:
        got_results = [snapshot.to_dict() for snapshot in pipeline.execute()]
        if expected_results:
            assert got_results == expected_results
    # check for error message if expected
    if error_regex:
        found_error = str(ctx.value)
        match = re.search(error_regex, found_error)
        assert match, f"error '{found_error}' does not match '{error_regex}'"