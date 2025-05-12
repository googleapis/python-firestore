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
import datetime

from google.cloud.firestore_v1.pipeline_result import PipelineResult


class TestPipelineResult:

    def _make_one(self, *args, **kwargs):
        if not args:
            # use defaults if not passed
            args = [mock.Mock(), {}]
        return PipelineResult(*args, **kwargs)

    def test_ref(self):
        expected = object()
        instance = self._make_one(ref=expected)
        assert instance.ref == expected
        # should be None if not set
        assert self._make_one().ref == None

    def test_id(self):
        ref = mock.Mock()
        ref.id = "test"
        instance = self._make_one(ref=ref)
        assert instance.id == "test"
        # should be None if not set
        assert self._make_one().id == None

    def test_create_time(self):
        expected = object()
        instance = self._make_one(create_time=expected)
        assert instance.create_time == expected
        # should be None if not set
        assert self._make_one().create_time == None

    def test_update_time(self):
        expected = object()
        instance = self._make_one(update_time=expected)
        assert instance.update_time == expected
        # should be None if not set
        assert self._make_one().update_time== None

    def test_exection_time(self):
        expected = object()
        instance = self._make_one(execution_time=expected)
        assert instance.execution_time == expected
        # should raise if not set
        with pytest.raises(ValueError) as e:
            self._make_one().execution_time
            assert "execution_time" in e

    @pytest.mark.parametrize("first,second,result", [
        ((object(),{}), (object(), {}), True),
        ((object(),{1:1}), (object(), {1:1}), True),
        ((object(),{1:1}), (object(), {2:2}), False),
        ((object(),{}, "ref"), (object(), {}, "ref"), True),
        ((object(),{}, "ref"), (object(), {}, "diff"), False),
        ((object(),{1:1}, "ref"), (object(), {1:1}, "ref"), True),
        ((object(),{1:1}, "ref"), (object(), {2:2}, "ref"), False),
        ((object(),{1:1}, "ref"), (object(), {1:1}, "diff"), False),
        ((object(),{1:1}, "ref", 1,2,3), (object(), {1:1}, "ref", 4,5,6), True),
    ])
    def test_eq(self, first, second, result):
        first_obj = self._make_one(*first)
        second_obj = self._make_one(*second)
        assert (first_obj == second_obj) is result

    def test_data(self):
        from google.cloud.firestore_v1.types.document import Value
        client = mock.Mock()
        data = {"str": Value(string_value="hello world"), "int": Value(integer_value=5)}
        instance = self._make_one(client, data)
        got = instance.data()
        assert len(got) == 2
        assert got["str"] == "hello world"
        assert got["int"] == 5

    def test_data_none(self):
        client = object()
        data = None
        instance = self._make_one(client, data)
        assert instance.data() is None

    def test_data_call(self):
        """
        ensure decode_dict is called on .data
        """
        client = object()
        data = {"hello": "world"}
        instance = self._make_one(client, data)
        with mock.patch("google.cloud.firestore_v1._helpers.decode_dict") as decode_mock:
            got = instance.data()
            decode_mock.assert_called_once_with(data, client)
            assert got == decode_mock.return_value

    def test_get(self):
        from google.cloud.firestore_v1.types.document import Value
        client = object()
        data = {"key": Value(string_value="hello world")}
        instance = self._make_one(client, data)
        got = instance.get("key")
        assert got == "hello world"

    def test_get_nested(self):
        from google.cloud.firestore_v1.types.document import Value
        client = object()
        data = {
            "first": {"second": Value(string_value="hello world")}
        }
        instance = self._make_one(client, data)
        got = instance.get("first.second")
        assert got == "hello world"

    def test_get_field_path(self):
        from google.cloud.firestore_v1.types.document import Value
        from google.cloud.firestore_v1.field_path import FieldPath
        client = object()
        data = {
            "first": {"second": Value(string_value="hello world")}
        }
        path = FieldPath.from_string("first.second")
        instance = self._make_one(client, data)
        got = instance.get(path)
        assert got == "hello world"

    def test_get_failure(self):
        """
        test calling get on value not in data
        """
        client = object()
        data = {}
        instance = self._make_one(client, data)
        with pytest.raises(KeyError):
            instance.get("key")

    def test_get_call(self):
        """
        ensure decode_value is called on .get()
        """
        client = object()
        data = {"key": "value"}
        instance = self._make_one(client, data)
        with mock.patch("google.cloud.firestore_v1._helpers.decode_value") as decode_mock:
            got = instance.get("key")
            decode_mock.assert_called_once_with("value", client)
            assert got == decode_mock.return_value