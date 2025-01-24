from __future__ import annotations
import ast
import sys
import os
import black
import pytest
import yaml
from typing import Any

# from google.cloud.firestore_v1.pipeline_stages import *
from google.cloud.firestore_v1 import pipeline_stages
from google.cloud.firestore_v1 import pipeline_expressions

test_dir_name = os.path.dirname(__file__)


def loader():
    # load test cases
    with open(f"{test_dir_name}/pipeline_e2e.yaml") as f:
        test_cases = yaml.safe_load(f)
        for test in test_cases["tests"]:
            yield test

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
            if isinstance(stage_yaml_args, dict):
                # yaml has a mapping of arguments. Treat as kwargs
                stage_obj = stage_cls(**parse_expressions(stage_yaml_args))
            elif isinstance(stage_yaml_args, list):
                # yaml has an array of arguments. Treat as args
                stage_obj = stage_cls(*parse_expressions(stage_yaml_args))
            else:
                # yaml has a single argument
                stage_obj = stage_cls(parse_expressions(stage_yaml_args))
        else:
            # yaml has no arguments
            stage_obj = stage_cls()
        result_list.append(stage_obj)
    return result_list


def parse_expressions(yaml_element: Any):
    if isinstance(yaml_element, list):
        return [parse_expressions(v) for v in yaml_element]
    elif isinstance(yaml_element, dict):
        return {parse_expressions(k): parse_expressions(v) for k,v in yaml_element.items()}
    elif hasattr(pipeline_expressions, yaml_element):
        return getattr(pipeline_expressions, yaml_element)
    else:
        return yaml_element


@pytest.mark.parametrize(
    "test_dict", loader(), ids=lambda x: f"{x.get('description', '')}"
)
@pytest.mark.skipif(
    sys.version_info < (3, 9), reason="ast.unparse requires python3.9 or higher"
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
