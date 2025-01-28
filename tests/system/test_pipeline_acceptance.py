from __future__ import annotations
import sys
import os
import pytest
import yaml
from typing import Any

# from google.cloud.firestore_v1.pipeline_stages import *
from google.cloud.firestore_v1 import pipeline_stages
from google.cloud.firestore_v1 import pipeline_expressions

from google.cloud.firestore import Client

FIRESTORE_TEST_DB = os.environ.get("SYSTEM_TESTS_DATABASE", "system-tests-named-db")
FIRESTORE_PROJECT = os.environ.get("GCLOUD_PROJECT")

test_dir_name = os.path.dirname(__file__)



def loader():
    # load test cases
    with open(f"{test_dir_name}/pipeline_e2e.yaml") as f:
        test_cases = yaml.safe_load(f)
    # load data
    data = test_cases["data"]
    client = Client(project=FIRESTORE_PROJECT, database=FIRESTORE_TEST_DB)
    try:
        # setup data
        batch = client.batch()
        for collection_name, documents in data.items():
            collection_ref = client.collection(collection_name)
            for document_id, document_data in documents.items():
                document_ref = collection_ref.document(document_id)
                batch.set(document_ref, document_data)
        batch.commit()

        # run tests
        for test in test_cases["tests"]:
            yield test
    finally:
        # clear data
        for collection_name, documents in data.items():
            collection_ref = client.collection(collection_name)
            for document_id in documents:
                document_ref = collection_ref.document(document_id)
                document_ref.delete()


def _apply_yaml_args(cls, yaml_args):
    if isinstance(yaml_args, dict):
        # yaml has a mapping of arguments. Treat as kwargs
        return cls(**parse_expressions(yaml_args))
    elif isinstance(yaml_args, list):
        # yaml has an array of arguments. Treat as args
        return cls(*parse_expressions(yaml_args))
    else:
        # yaml has a single argument
        return cls(parse_expressions(yaml_args))


def parse_pipeline(pipeline: list[dict[str, Any], str]):
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
            stage_obj = _apply_yaml_args(stage_cls, stage_yaml_args)
        else:
            # yaml has no arguments
            stage_obj = stage_cls()
        result_list.append(stage_obj)
    return result_list


def parse_expressions(yaml_element: Any):
    if isinstance(yaml_element, list):
        return [parse_expressions(v) for v in yaml_element]
    elif isinstance(yaml_element, dict):
        if len(yaml_element) == 1 and isinstance(list(yaml_element)[0], str) and hasattr(pipeline_expressions, list(yaml_element)[0]):
            # build pipeline expressions if possible
            cls_str = list(yaml_element)[0]
            cls = getattr(pipeline_expressions, cls_str)
            yaml_args = yaml_element[cls_str]
            return _apply_yaml_args(cls, yaml_args)
        else:
            # otherwise, return dict
            return {parse_expressions(k): parse_expressions(v) for k,v in yaml_element.items()}
    elif isinstance(yaml_element, str) and hasattr(pipeline_expressions, yaml_element):
        return getattr(pipeline_expressions, yaml_element)()
    else:
        return yaml_element


@pytest.mark.parametrize(
    "test_dict", loader(), ids=lambda x: f"{x.get('description', '')}"
)
def test_e2e_scenario(test_dict):
    pipeline = parse_pipeline(test_dict["pipeline"])

    # before_ast = ast.parse(test_dict["before"])
    # got_ast = before_ast
    # for transformer_info in test_dict["transformers"]:
    #     # transformer can be passed as a string, or a dict with name and args
    #     if isinstance(transformer_info, str):
    #         transformer_class = globals()[transformer_info]
    #         transformer_args = {}
    #     else:
    #         transformer_class = globals()[transformer_info["name"]]
    #         transformer_args = transformer_info.get("args", {})
    #     transformer = transformer_class(**transformer_args)
    #     got_ast = transformer.visit(got_ast)
    # if got_ast is None:
    #     final_str = ""
    # else:
    #     final_str = black.format_str(ast.unparse(got_ast), mode=black.FileMode())
    # if test_dict.get("after") is None:
    #     expected_str = ""
    # else:
    #     expected_str = black.format_str(test_dict["after"], mode=black.FileMode())
    # assert final_str == expected_str, f"Expected:\n{expected_str}\nGot:\n{final_str}"
