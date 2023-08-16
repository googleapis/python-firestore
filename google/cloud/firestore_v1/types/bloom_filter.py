# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
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
#
from __future__ import annotations

from typing import MutableMapping, MutableSequence

import proto  # type: ignore


__protobuf__ = proto.module(
    package="google.firestore.v1",
    manifest={
        "BitSequence",
        "BloomFilter",
    },
)


class BitSequence(proto.Message):
    r"""A sequence of bits, encoded in a byte array.

    Each byte in the ``bitmap`` byte array stores 8 bits of the
    sequence. The only exception is the last byte, which may store 8 *or
    fewer* bits. The ``padding`` defines the number of bits of the last
    byte to be ignored as "padding". The values of these "padding" bits
    are unspecified and must be ignored.

    To retrieve the first bit, bit 0, calculate:
    ``(bitmap[0] & 0x01) != 0``. To retrieve the second bit, bit 1,
    calculate: ``(bitmap[0] & 0x02) != 0``. To retrieve the third bit,
    bit 2, calculate: ``(bitmap[0] & 0x04) != 0``. To retrieve the
    fourth bit, bit 3, calculate: ``(bitmap[0] & 0x08) != 0``. To
    retrieve bit n, calculate:
    ``(bitmap[n / 8] & (0x01 << (n % 8))) != 0``.

    The "size" of a ``BitSequence`` (the number of bits it contains) is
    calculated by this formula: ``(bitmap.length * 8) - padding``.

    Attributes:
        bitmap (bytes):
            The bytes that encode the bit sequence.
            May have a length of zero.
        padding (int):
            The number of bits of the last byte in ``bitmap`` to ignore
            as "padding". If the length of ``bitmap`` is zero, then this
            value must be ``0``. Otherwise, this value must be between 0
            and 7, inclusive.
    """

    bitmap: bytes = proto.Field(
        proto.BYTES,
        number=1,
    )
    padding: int = proto.Field(
        proto.INT32,
        number=2,
    )


class BloomFilter(proto.Message):
    r"""A bloom filter (https://en.wikipedia.org/wiki/Bloom_filter).

    The bloom filter hashes the entries with MD5 and treats the
    resulting 128-bit hash as 2 distinct 64-bit hash values, interpreted
    as unsigned integers using 2's complement encoding.

    These two hash values, named ``h1`` and ``h2``, are then used to
    compute the ``hash_count`` hash values using the formula, starting
    at ``i=0``:

    ::

        h(i) = h1 + (i * h2)

    These resulting values are then taken modulo the number of bits in
    the bloom filter to get the bits of the bloom filter to test for the
    given entry.

    Attributes:
        bits (google.cloud.firestore_v1.types.BitSequence):
            The bloom filter data.
        hash_count (int):
            The number of hashes used by the algorithm.
    """

    bits: "BitSequence" = proto.Field(
        proto.MESSAGE,
        number=1,
        message="BitSequence",
    )
    hash_count: int = proto.Field(
        proto.INT32,
        number=2,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
