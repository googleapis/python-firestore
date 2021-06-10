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
from typing import Callable, NoReturn, Optional


def utcnow():
    return datetime.datetime.utcnow()


default_initial_tokens: int = 500
default_phase_length: int = 60 * 5  # 5 minutes
microseconds_per_second: int = 1000000


class Throttle:
    """Implements 5/5/5 ramp-up via Token Bucket algorithm."""

    def __init__(
        self,
        initial_tokens: Optional[int] = default_initial_tokens,
        phase_length: Optional[int] = default_phase_length,
    ):
        # Tracks the volume of operations during a given ramp-up phase.
        self._operations_this_phase: int = 0

        self._start: datetime.datetime = utcnow()
        self._last_refill: datetime.datetime = self._start

        # Current number of available operations. Decrements with every
        # permitted request and refills over time.
        self._available_tokens: int = initial_tokens

        # Maximum size of the available operations. Can increase by 50%
        # every [phase_length] number of seconds.
        self._maximum_tokens: int = self._available_tokens

        # Number of seconds after which the [_maximum_tokens] can increase by 50%.
        self._phase_length: int = phase_length

        # Tracks how many times the [_maximum_tokens] has increased by 50%.
        self._phase: int = 0

    def take_tokens(self, num: Optional[int] = 1) -> bool:
        """Returns True if an operation is currently permitted or False if not."""
        self._check_phase()
        self._refill()

        if self._available_tokens > 0:
            _num_to_take = min(self._available_tokens, num)
            self._available_tokens -= _num_to_take
            self._operations_this_phase += _num_to_take
            return _num_to_take
        return 0

    def _check_phase(self):
        """Increments or decrements [_phase] depending on traffic.

        Every [_phase_length] seconds, if > 50% of available traffic was used
        during the window, increases [_phase], otherwise, decreases [_phase].

        This is a no-op unless a new [_phase_length] number of seconds since the
        start was crossed since it was last called.
        """
        age: datetime.timedelta = utcnow() - self._start

        # Uses integer division to calculate the expected phase. We start in
        # Phase 0, so until [_phase_length] seconds have passed, this will
        # not resolve to 1.
        expected_phase: int = age.seconds // self._phase_length

        # Short-circuit if we are still in the expected phase.
        if expected_phase == self._phase:
            return

        operations_last_phase: int = self._operations_this_phase
        self._operations_this_phase = 0

        previous_phase: int = self._phase
        self._phase = expected_phase

        # No-op if we did nothing for an entire phase
        if operations_last_phase and self._phase <= previous_phase + 1:
            self._increase_maximum_tokens()

    def _increase_maximum_tokens(self) -> NoReturn:
        self._maximum_tokens = round(self._maximum_tokens * 1.5)

    def _refill(self) -> NoReturn:
        """Replenishes any tokens that should have regenerated since the last
        operation."""
        now: datetime.datetime = utcnow()
        time_since_last_refill: datetime.timedelta = now - self._last_refill

        if time_since_last_refill:
            self._last_refill = now

            # If we haven't done anything for 1s, then we know for certain we
            # should reset to max capacity.
            if time_since_last_refill.seconds >= 1:
                self._available_tokens = self._maximum_tokens

            # If we have done something in the last 1s, then we know we should
            # allocate proportional tokens.
            else:
                _percent_of_max: float = (
                    time_since_last_refill.microseconds / microseconds_per_second
                )
                new_tokens: int = round(_percent_of_max * self._maximum_tokens)

                # Add the number of provisioned tokens, capped at the maximum size.
                self._available_tokens = min(
                    self._maximum_tokens, self._available_tokens + new_tokens,
                )
