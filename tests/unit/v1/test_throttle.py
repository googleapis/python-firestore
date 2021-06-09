# Copyright 2021 Google LLC All rights reserved.
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
import unittest
from typing import Callable, Optional


from google.cloud.firestore_v1 import throttle


# Pick a point in time as the center of our universe for this test run.
# It is okay for this to update every time the tests are run.
fake_now = datetime.datetime.utcnow()


def now() -> datetime.datetime:
    return fake_now


def now_plus_n(
    seconds: Optional[int] = 0, microseconds: Optional[int] = 0,
) -> Callable:
    def wrapper():
        return fake_now + datetime.timedelta(
            seconds=seconds, microseconds=microseconds,
        )

    return wrapper


class TestThrottle(unittest.TestCase):
    def test_throttle_basic(self):
        """Verifies that if time stands still, the Throttle allows 500 writes
        before crashing out.
        """
        # This throttle will never advance. Poor fella.
        th = throttle.Throttle(now_getter=now)
        for _ in range(throttle.default_initial_tokens):
            self.assertTrue(th.take_token())
        self.assertFalse(th.take_token())

    def test_throttle_with_refill(self):
        """Verifies that if clock advances, the Throttle allows appropriate
        additional writes.
        """
        th = throttle.Throttle(now_getter=now)
        th._available_tokens = 0
        self.assertFalse(th.take_token())
        # Advance the clock 0.1 seconds
        th._now = now_plus_n(microseconds=100000)
        for _ in range(round(throttle.default_initial_tokens / 10)):
            self.assertTrue(th.take_token())
        self.assertFalse(th.take_token())

    def test_throttle_phase_length(self):
        """Verifies that if clock advances, the Throttle allows appropriate
        additional writes.
        """
        th = throttle.Throttle(now_getter=now)
        self.assertTrue(th.take_token())
        th._available_tokens = 0
        self.assertFalse(th.take_token())
        # Advance the clock 1 phase
        th._now = now_plus_n(seconds=throttle.default_phase_length, microseconds=1)
        for _ in range(round(throttle.default_initial_tokens * 3 / 2)):
            self.assertTrue(th.take_token(), msg=f"token {_} should have been allowed")
        self.assertFalse(th.take_token())

    def test_throttle_idle_phase_length(self):
        """Verifies that if clock advances but nothing happens, the Throttle
        doesn't ramp up.
        """
        th = throttle.Throttle(now_getter=now)
        th._available_tokens = 0
        self.assertFalse(th.take_token())
        # Advance the clock 1 phase
        th._now = now_plus_n(seconds=throttle.default_phase_length, microseconds=1)
        for _ in range(round(throttle.default_initial_tokens)):
            self.assertTrue(th.take_token(), msg=f"token {_} should have been allowed")
            self.assertEqual(th._maximum_tokens, 500)
        self.assertFalse(th.take_token())
