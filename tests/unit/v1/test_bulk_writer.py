# # Copyright 2021 Google LLC All rights reserved.
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

import datetime
import mock  # type: ignore
import unittest

import google
from google.cloud.firestore_v1.bulk_writer import BulkWriter, BulkWriterScheduler


class TestBulkWriterScheduler(unittest.TestCase):

    @mock.patch.object(google.cloud.firestore_v1.rate_limiter, "utcnow")
    def test_max_in_flight(self, mocked_now):
        six_minutes_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=6)
        mocked_now.return_value = six_minutes_ago
        
        scheduler = BulkWriterScheduler()
        self.assertEqual(scheduler.max_in_flight, 500)
        
        scheduler.request_send(20)

        now = datetime.datetime.utcnow()
        mocked_now.return_value = now

        scheduler.request_send(20)
        self.assertEqual(scheduler.max_in_flight, 750)