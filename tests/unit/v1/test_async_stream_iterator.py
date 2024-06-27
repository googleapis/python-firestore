# Copyright 2024 Google LLC All rights reserved.
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

import pytest


def _make_async_stream_iterator(iterable):
    from google.cloud.firestore_v1.async_stream_iterator import AsyncStreamIterator

    async def _inner_generator():
        for i in iterable:
            X = yield i
            if X:
                yield X

    return AsyncStreamIterator(_inner_generator())


@pytest.mark.asyncio
async def test_async_stream_iterator_iter():
    expected_results = [0, 1, 2]
    inst = _make_async_stream_iterator(expected_results)

    actual_results = []
    async for result in inst:
        actual_results.append(result)

    assert expected_results == actual_results


@pytest.mark.asyncio
async def test_async_stream_iterator_next():
    expected_results = [0, 1]
    inst = _make_async_stream_iterator(expected_results)

    actual_results = []
    actual_results.append(await anext(inst))
    actual_results.append(await anext(inst))

    with pytest.raises(StopAsyncIteration):
        await anext(inst)

    assert expected_results == actual_results


@pytest.mark.asyncio
async def test_async_stream_iterator_send():
    expected_results = [0, 1]
    inst = _make_async_stream_iterator(expected_results)

    actual_results = []
    actual_results.append(await anext(inst))
    assert await inst.asend(2) == 2
    actual_results.append(await anext(inst))

    with pytest.raises(StopAsyncIteration):
        await anext(inst)

    assert expected_results == actual_results


@pytest.mark.asyncio
async def test_async_stream_iterator_throw():
    inst = _make_async_stream_iterator([])
    with pytest.raises(ValueError):
        await inst.athrow(ValueError)
