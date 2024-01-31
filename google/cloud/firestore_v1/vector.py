# -*- coding: utf-8 -*-
# Copyright 2024 Google LLC
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


class Vector():
    r""" A class to represent Firestore Vector in python.

    Underline it'll be converted to a map representation in Firestore API.
    """

    value: list[float] = None

    def __init__(self, value: list[float]):
        self.value = value

    def __eq__(self, other: 'Vector') -> bool:
        if not isinstance(other, Vector):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.value == other.value
    
    def __str__(self):
        return 'Vector<' + ','.join([str(i) for i in self.value]) + '>'

    def __repr__(self):
        return 'Vector<' + ','.join([str(i) for i in self.value]) + '>'

    def to_map_value(self):
        return {
            "__type__": "__vector__",
            "value": self.value
        }
