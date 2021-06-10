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
from typing import Optional

import mock
import google
from google.cloud.firestore_v1 import ramp_up


# Pick a point in time as the center of our universe for this test run.
# It is okay for this to update every time the tests are run.
fake_now = datetime.datetime.utcnow()


def now_plus_n(
    seconds: Optional[int] = 0, microseconds: Optional[int] = 0,
) -> datetime.timedelta:
    return fake_now + datetime.timedelta(seconds=seconds, microseconds=microseconds,)


class TestRampUp(unittest.TestCase):
    @mock.patch.object(google.cloud.firestore_v1.ramp_up, "utcnow")
    def test_ramp_up_basic(self, mocked_now):
        """Verifies that if the clock does not advance, the RampUp allows 500
        writes before crashing out.
        """
        mocked_now.return_value = fake_now
        # This RampUp will never advance. Poor fella.
        ramp = ramp_up.RampUp()
        for _ in range(ramp_up.default_initial_tokens):
            self.assertEqual(ramp.take_tokens(), 1)
        self.assertEqual(ramp.take_tokens(), 0)

    @mock.patch.object(google.cloud.firestore_v1.ramp_up, "utcnow")
    def test_ramp_up_with_refill(self, mocked_now):
        """Verifies that if the clock advances, the RampUp allows appropriate
        additional writes.
        """
        mocked_now.return_value = fake_now
        ramp = ramp_up.RampUp()
        ramp._available_tokens = 0
        self.assertEqual(ramp.take_tokens(), 0)
        # Advance the clock 0.1 seconds
        mocked_now.return_value = now_plus_n(microseconds=100000)
        for _ in range(round(ramp_up.default_initial_tokens / 10)):
            self.assertEqual(ramp.take_tokens(), 1)
        self.assertEqual(ramp.take_tokens(), 0)

    @mock.patch.object(google.cloud.firestore_v1.ramp_up, "utcnow")
    def test_ramp_up_phase_length(self, mocked_now):
        """Verifies that if the clock advances, the RampUp allows appropriate
        additional writes.
        """
        mocked_now.return_value = fake_now
        ramp = ramp_up.RampUp()
        self.assertEqual(ramp.take_tokens(), 1)
        ramp._available_tokens = 0
        self.assertEqual(ramp.take_tokens(), 0)
        # Advance the clock 1 phase
        mocked_now.return_value = now_plus_n(
            seconds=ramp_up.default_phase_length, microseconds=1,
        )
        for _ in range(round(ramp_up.default_initial_tokens * 3 / 2)):
            self.assertTrue(
                ramp.take_tokens(), msg=f"token {_} should have been allowed"
            )
        self.assertEqual(ramp.take_tokens(), 0)

    @mock.patch.object(google.cloud.firestore_v1.ramp_up, "utcnow")
    def test_ramp_up_idle_phase_length(self, mocked_now):
        """Verifies that if the clock advances but nothing happens, the RampUp
        doesn't ramp up.
        """
        mocked_now.return_value = fake_now
        ramp = ramp_up.RampUp()
        ramp._available_tokens = 0
        self.assertEqual(ramp.take_tokens(), 0)
        # Advance the clock 1 phase
        mocked_now.return_value = now_plus_n(
            seconds=ramp_up.default_phase_length, microseconds=1,
        )
        for _ in range(round(ramp_up.default_initial_tokens)):
            self.assertEqual(
                ramp.take_tokens(), 1, msg=f"token {_} should have been allowed"
            )
            self.assertEqual(ramp._maximum_tokens, 500)
        self.assertEqual(ramp.take_tokens(), 0)

    @mock.patch.object(google.cloud.firestore_v1.ramp_up, "utcnow")
    def test_take_batch_size(self, mocked_now):
        """Verifies that if the clock advances but nothing happens, the RampUp
        doesn't ramp up.
        """
        page_size: int = 20
        mocked_now.return_value = fake_now
        ramp = ramp_up.RampUp()
        ramp._available_tokens = 15
        self.assertEqual(ramp.take_tokens(page_size), 15)
        # Advance the clock 1 phase
        mocked_now.return_value = now_plus_n(
            seconds=ramp_up.default_phase_length, microseconds=1,
        )
        ramp._check_phase()
        self.assertEqual(ramp._maximum_tokens, 750)

        for _ in range(740 // page_size):
            self.assertEqual(
                ramp.take_tokens(page_size),
                page_size,
                msg=f"page {_} should have been allowed",
            )
        self.assertEqual(ramp.take_tokens(page_size), 10)
        self.assertEqual(ramp.take_tokens(page_size), 0)

    @mock.patch.object(google.cloud.firestore_v1.ramp_up, "utcnow")
    def test_phase_progress(self, mocked_now):
        mocked_now.return_value = fake_now

        ramp = ramp_up.RampUp()
        self.assertEqual(ramp._phase, 0)
        self.assertEqual(ramp._maximum_tokens, 500)
        ramp.take_tokens()

        # Advance the clock 1 phase
        mocked_now.return_value = now_plus_n(
            seconds=ramp_up.default_phase_length, microseconds=1,
        )
        ramp.take_tokens()
        self.assertEqual(ramp._phase, 1)
        self.assertEqual(ramp._maximum_tokens, 750)

        # Advance the clock another phase
        mocked_now.return_value = now_plus_n(
            seconds=ramp_up.default_phase_length * 2, microseconds=1,
        )
        ramp.take_tokens()
        self.assertEqual(ramp._phase, 2)
        self.assertEqual(ramp._maximum_tokens, 1125)

        # Advance the clock another ms and the phase should not advance
        mocked_now.return_value = now_plus_n(
            seconds=ramp_up.default_phase_length * 2, microseconds=2,
        )
        ramp.take_tokens()
        self.assertEqual(ramp._phase, 2)
        self.assertEqual(ramp._maximum_tokens, 1125)
