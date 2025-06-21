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

import pytest

import google.cloud.firestore_v1._pipeline_stages as stages
from google.cloud.firestore_v1.pipeline_expressions import (
    Constant,
    Field,
    Ordering,
)
from google.cloud.firestore_v1.types.document import Value
from google.cloud.firestore_v1._helpers import GeoPoint


class TestStage:
    def test_ctor(self):
        """
        Base class should be abstract
        """
        with pytest.raises(TypeError):
            stages.Stage()


class TestCollection:
    def _make_one(self, *args, **kwargs):
        return stages.Collection(*args, **kwargs)

    @pytest.mark.parametrize(
        "input_arg,expected",
        [
            ("test", "Collection(path='/test')"),
            ("/test", "Collection(path='/test')"),
        ],
    )
    def test_repr(self, input_arg, expected):
        instance = self._make_one(input_arg)
        repr_str = repr(instance)
        assert repr_str == expected

    def test_to_pb(self):
        input_arg = "test/col"
        instance = self._make_one(input_arg)
        result = instance._to_pb()
        assert result.name == "collection"
        assert len(result.args) == 1
        assert result.args[0].reference_value == "/test/col"
        assert len(result.options) == 0


class TestGenericStage:
    def _make_one(self, *args, **kwargs):
        return stages.GenericStage(*args, **kwargs)

    @pytest.mark.parametrize(
        "input_args,expected_params",
        [
            (("name",), []),
            (("custom", Value(string_value="val")), [Value(string_value="val")]),
            (("n", Value(integer_value=1)), [Value(integer_value=1)]),
            (("n", Constant.of(1)), [Value(integer_value=1)]),
            (
                ("n", Constant.of(True), Constant.of(False)),
                [Value(boolean_value=True), Value(boolean_value=False)],
            ),
            (
                ("n", Constant.of(GeoPoint(1, 2))),
                [Value(geo_point_value={"latitude": 1, "longitude": 2})],
            ),
            (("n", Constant.of(None)), [Value(null_value=0)]),
            (
                ("n", Constant.of([0, 1, 2])),
                [
                    Value(
                        array_value={
                            "values": [Value(integer_value=n) for n in range(3)]
                        }
                    )
                ],
            ),
            (
                ("n", Value(reference_value="/projects/p/databases/d/documents/doc")),
                [Value(reference_value="/projects/p/databases/d/documents/doc")],
            ),
            (
                ("n", Constant.of({"a": "b"})),
                [Value(map_value={"fields": {"a": Value(string_value="b")}})],
            ),
        ],
    )
    def test_ctor(self, input_args, expected_params):
        instance = self._make_one(*input_args)
        assert instance.params == expected_params

    @pytest.mark.parametrize(
        "input_args,expected",
        [
            (("name",), "GenericStage(name='name')"),
            (("custom", Value(string_value="val")), "GenericStage(name='custom')"),
        ],
    )
    def test_repr(self, input_args, expected):
        instance = self._make_one(*input_args)
        repr_str = repr(instance)
        assert repr_str == expected

    def test_to_pb(self):
        instance = self._make_one("name", Constant.of(True), Constant.of("test"))
        result = instance._to_pb()
        assert result.name == "name"
        assert len(result.args) == 2
        assert result.args[0].boolean_value is True
        assert result.args[1].string_value == "test"
        assert len(result.options) == 0


class TestLimit:
    def _make_one(self, *args, **kwargs):
        return stages.Limit(*args, **kwargs)

    def test_repr(self):
        instance = self._make_one(10)
        repr_str = repr(instance)
        assert repr_str == "Limit(limit=10)"

    def test_to_pb(self):
        instance = self._make_one(5)
        result = instance._to_pb()
        assert result.name == "limit"
        assert len(result.args) == 1
        assert result.args[0].integer_value == 5
        assert len(result.options) == 0


class TestOffset:
    def _make_one(self, *args, **kwargs):
        return stages.Offset(*args, **kwargs)

    def test_repr(self):
        instance = self._make_one(20)
        repr_str = repr(instance)
        assert repr_str == "Offset(offset=20)"

    def test_to_pb(self):
        instance = self._make_one(3)
        result = instance._to_pb()
        assert result.name == "offset"
        assert len(result.args) == 1
        assert result.args[0].integer_value == 3
        assert len(result.options) == 0


class TestSelect:
    def _make_one(self, *args, **kwargs):
        return stages.Select(*args, **kwargs)

    def test_repr(self):
        instance = self._make_one("field1", Field.of("field2"))
        repr_str = repr(instance)
        assert (
            repr_str == "Select(projections=[Field.of('field1'), Field.of('field2')])"
        )

    def test_to_pb(self):
        instance = self._make_one("field1", "field2.subfield", Field.of("field3"))
        result = instance._to_pb()
        assert result.name == "select"
        assert len(result.args) == 1
        got_map = result.args[0].map_value.fields
        assert got_map.get("field1").field_reference_value == "field1"
        assert got_map.get("field2.subfield").field_reference_value == "field2.subfield"
        assert got_map.get("field3").field_reference_value == "field3"
        assert len(result.options) == 0


class TestSort:
    def _make_one(self, *args, **kwargs):
        return stages.Sort(*args, **kwargs)

    def test_repr(self):
        order1 = Ordering(Field.of("field1"), "ASCENDING")
        instance = self._make_one(order1)
        repr_str = repr(instance)
        assert repr_str == "Sort(orders=[Field.of('field1').ascending()])"

    def test_to_pb(self):
        order1 = Ordering(Field.of("name"), "ASCENDING")
        order2 = Ordering(Field.of("age"), "DESCENDING")
        instance = self._make_one(order1, order2)
        result = instance._to_pb()
        assert result.name == "sort"
        assert len(result.args) == 2
        got_map = result.args[0].map_value.fields
        assert got_map.get("expression").field_reference_value == "name"
        assert got_map.get("direction").string_value == "ascending"
        assert len(result.options) == 0


class TestWhere:
    def _make_one(self, *args, **kwargs):
        return stages.Where(*args, **kwargs)

    def test_repr(self):
        condition = Field.of("age").gt(30)
        instance = self._make_one(condition)
        repr_str = repr(instance)
        assert repr_str == "Where(condition=Field.of('age').gt(Constant.of(30)))"

    def test_to_pb(self):
        condition = Field.of("city").eq("SF")
        instance = self._make_one(condition)
        result = instance._to_pb()
        assert result.name == "where"
        assert len(result.args) == 1
        got_fn = result.args[0].function_value
        assert got_fn.name == "eq"
        assert len(got_fn.args) == 2
        assert got_fn.args[0].field_reference_value == "city"
        assert got_fn.args[1].string_value == "SF"
        assert len(result.options) == 0
