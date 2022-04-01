# -*- coding: utf-8 -*-
# Copyright 2017 Google LLC All rights reserved.
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

import mock
import pytest


def _make_order(*args, **kwargs):
    from google.cloud.firestore_v1.order import Order

    return Order(*args, **kwargs)


def test_order_compare_across_heterogenous_values():
    from google.cloud.firestore_v1.order import Order

    # Constants used to represent min/max values of storage types.
    int_max_value = 2**31 - 1
    int_min_value = -(2**31)
    float_min_value = 1.175494351**-38
    float_nan = float("nan")
    inf = float("inf")

    groups = [None] * 65

    groups[0] = [nullValue()]

    groups[1] = [_boolean_value(False)]
    groups[2] = [_boolean_value(True)]

    # numbers
    groups[3] = [_double_value(float_nan), _double_value(float_nan)]
    groups[4] = [_double_value(-inf)]
    groups[5] = [_int_value(int_min_value - 1)]
    groups[6] = [_int_value(int_min_value)]
    groups[7] = [_double_value(-1.1)]
    # Integers and Doubles order the same.
    groups[8] = [_int_value(-1), _double_value(-1.0)]
    groups[9] = [_double_value(-float_min_value)]
    # zeros all compare the same.
    groups[10] = [
        _int_value(0),
        _double_value(-0.0),
        _double_value(0.0),
        _double_value(+0.0),
    ]
    groups[11] = [_double_value(float_min_value)]
    groups[12] = [_int_value(1), _double_value(1.0)]
    groups[13] = [_double_value(1.1)]
    groups[14] = [_int_value(int_max_value)]
    groups[15] = [_int_value(int_max_value + 1)]
    groups[16] = [_double_value(inf)]

    groups[17] = [_timestamp_value(123, 0)]
    groups[18] = [_timestamp_value(123, 123)]
    groups[19] = [_timestamp_value(345, 0)]

    # strings
    groups[20] = [_string_value("")]
    groups[21] = [_string_value("\u0000\ud7ff\ue000\uffff")]
    groups[22] = [_string_value("(╯°□°）╯︵ ┻━┻")]
    groups[23] = [_string_value("a")]
    groups[24] = [_string_value("abc def")]
    # latin small letter e + combining acute accent + latin small letter b
    groups[25] = [_string_value("e\u0301b")]
    groups[26] = [_string_value("æ")]
    # latin small letter e with acute accent + latin small letter a
    groups[27] = [_string_value("\u00e9a")]

    # blobs
    groups[28] = [_blob_value(b"")]
    groups[29] = [_blob_value(b"\x00")]
    groups[30] = [_blob_value(b"\x00\x01\x02\x03\x04")]
    groups[31] = [_blob_value(b"\x00\x01\x02\x04\x03")]
    groups[32] = [_blob_value(b"\x7f")]

    # resource names
    groups[33] = [_reference_value("projects/p1/databases/d1/documents/c1/doc1")]
    groups[34] = [_reference_value("projects/p1/databases/d1/documents/c1/doc2")]
    groups[35] = [
        _reference_value("projects/p1/databases/d1/documents/c1/doc2/c2/doc1")
    ]
    groups[36] = [
        _reference_value("projects/p1/databases/d1/documents/c1/doc2/c2/doc2")
    ]
    groups[37] = [_reference_value("projects/p1/databases/d1/documents/c10/doc1")]
    groups[38] = [_reference_value("projects/p1/databases/d1/documents/c2/doc1")]
    groups[39] = [_reference_value("projects/p2/databases/d2/documents/c1/doc1")]
    groups[40] = [_reference_value("projects/p2/databases/d2/documents/c1-/doc1")]
    groups[41] = [_reference_value("projects/p2/databases/d3/documents/c1-/doc1")]

    # geo points
    groups[42] = [_geoPoint_value(-90, -180)]
    groups[43] = [_geoPoint_value(-90, 0)]
    groups[44] = [_geoPoint_value(-90, 180)]
    groups[45] = [_geoPoint_value(0, -180)]
    groups[46] = [_geoPoint_value(0, 0)]
    groups[47] = [_geoPoint_value(0, 180)]
    groups[48] = [_geoPoint_value(1, -180)]
    groups[49] = [_geoPoint_value(1, 0)]
    groups[50] = [_geoPoint_value(1, 180)]
    groups[51] = [_geoPoint_value(90, -180)]
    groups[52] = [_geoPoint_value(90, 0)]
    groups[53] = [_geoPoint_value(90, 180)]

    # arrays
    groups[54] = [_array_value()]
    groups[55] = [_array_value(["bar"])]
    groups[56] = [_array_value(["foo"])]
    groups[57] = [_array_value(["foo", 0])]
    groups[58] = [_array_value(["foo", 1])]
    groups[59] = [_array_value(["foo", "0"])]

    # objects
    groups[60] = [_object_value({"bar": 0})]
    groups[61] = [_object_value({"bar": 0, "foo": 1})]
    groups[62] = [_object_value({"bar": 1})]
    groups[63] = [_object_value({"bar": 2})]
    groups[64] = [_object_value({"bar": "0"})]

    target = _make_order()

    for i in range(len(groups)):
        for left in groups[i]:
            for j in range(len(groups)):
                for right in groups[j]:

                    expected = Order._compare_to(i, j)
                    assert target.compare(left, right) == expected

                    expected = Order._compare_to(j, i)
                    assert target.compare(right, left) == expected


def test_order_compare_w_typeorder_type_failure():
    target = _make_order()
    left = mock.Mock()
    left.WhichOneof.return_value = "imaginary-type"

    with pytest.raises(ValueError) as exc_info:
        target.compare(left, mock.Mock())

    (message,) = exc_info.value.args
    assert message.startswith("Could not detect value")


def test_order_compare_w_failure_to_find_type():
    from google.cloud.firestore_v1.order import TypeOrder

    target = _make_order()
    left = mock.Mock()
    left.WhichOneof.return_value = "imaginary-type"
    right = mock.Mock()
    # Patch from value to get to the deep compare. Since left is a bad type
    # expect this to fail with value error.
    with mock.patch.object(TypeOrder, "from_value") as to:
        to.value = None
        with pytest.raises(ValueError) as exc_info:
            target.compare(left, right)

    (message,) = exc_info.value.args
    assert message.startswith("Unknown ``value_type``")


def test_order_compare_w_objects_different_keys():
    left = _object_value({"foo": 0})
    right = _object_value({"bar": 0})

    target = _make_order()
    target.compare(left, right)


def _boolean_value(b):
    from google.cloud.firestore_v1._helpers import encode_value

    return encode_value(b)


def _double_value(d):
    from google.cloud.firestore_v1._helpers import encode_value

    return encode_value(d)


def _int_value(value):
    from google.cloud.firestore_v1._helpers import encode_value

    return encode_value(value)


def _string_value(s):
    from google.cloud.firestore_v1._helpers import encode_value

    return encode_value(s)


def _reference_value(r):
    from google.cloud.firestore_v1.types import document

    return document.Value(reference_value=r)


def _blob_value(b):
    from google.cloud.firestore_v1._helpers import encode_value

    return encode_value(b)


def nullValue():
    from google.cloud.firestore_v1._helpers import encode_value

    return encode_value(None)


def _timestamp_value(seconds, nanos):
    from google.cloud.firestore_v1.types import document
    from google.protobuf import timestamp_pb2

    return document.Value(
        timestamp_value=timestamp_pb2.Timestamp(seconds=seconds, nanos=nanos)
    )


def _geoPoint_value(latitude, longitude):
    from google.cloud.firestore_v1._helpers import encode_value
    from google.cloud.firestore_v1._helpers import GeoPoint

    return encode_value(GeoPoint(latitude, longitude))


def _array_value(values=[]):
    from google.cloud.firestore_v1._helpers import encode_value

    return encode_value(values)


def _object_value(keysAndValues):
    from google.cloud.firestore_v1._helpers import encode_value

    return encode_value(keysAndValues)
