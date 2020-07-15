# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
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

from typing import Any, AsyncIterable, Awaitable, Callable, Iterable, Sequence, Tuple

from google.cloud.firestore_admin_v1.types import field
from google.cloud.firestore_admin_v1.types import firestore_admin
from google.cloud.firestore_admin_v1.types import index


class ListIndexesPager:
    """A pager for iterating through ``list_indexes`` requests.

    This class thinly wraps an initial
    :class:`~.firestore_admin.ListIndexesResponse` object, and
    provides an ``__iter__`` method to iterate through its
    ``indexes`` field.

    If there are more pages, the ``__iter__`` method will make additional
    ``ListIndexes`` requests and continue to iterate
    through the ``indexes`` field on the
    corresponding responses.

    All the usual :class:`~.firestore_admin.ListIndexesResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., firestore_admin.ListIndexesResponse],
        request: firestore_admin.ListIndexesRequest,
        response: firestore_admin.ListIndexesResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (:class:`~.firestore_admin.ListIndexesRequest`):
                The initial request object.
            response (:class:`~.firestore_admin.ListIndexesResponse`):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = firestore_admin.ListIndexesRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def pages(self) -> Iterable[firestore_admin.ListIndexesResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = self._method(self._request, metadata=self._metadata)
            yield self._response

    def __iter__(self) -> Iterable[index.Index]:
        for page in self.pages:
            yield from page.indexes

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListIndexesAsyncPager:
    """A pager for iterating through ``list_indexes`` requests.

    This class thinly wraps an initial
    :class:`~.firestore_admin.ListIndexesResponse` object, and
    provides an ``__aiter__`` method to iterate through its
    ``indexes`` field.

    If there are more pages, the ``__aiter__`` method will make additional
    ``ListIndexes`` requests and continue to iterate
    through the ``indexes`` field on the
    corresponding responses.

    All the usual :class:`~.firestore_admin.ListIndexesResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., Awaitable[firestore_admin.ListIndexesResponse]],
        request: firestore_admin.ListIndexesRequest,
        response: firestore_admin.ListIndexesResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (:class:`~.firestore_admin.ListIndexesRequest`):
                The initial request object.
            response (:class:`~.firestore_admin.ListIndexesResponse`):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = firestore_admin.ListIndexesRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    async def pages(self) -> AsyncIterable[firestore_admin.ListIndexesResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = await self._method(self._request, metadata=self._metadata)
            yield self._response

    def __aiter__(self) -> AsyncIterable[index.Index]:
        async def async_generator():
            async for page in self.pages:
                for response in page.indexes:
                    yield response

        return async_generator()

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListFieldsPager:
    """A pager for iterating through ``list_fields`` requests.

    This class thinly wraps an initial
    :class:`~.firestore_admin.ListFieldsResponse` object, and
    provides an ``__iter__`` method to iterate through its
    ``fields`` field.

    If there are more pages, the ``__iter__`` method will make additional
    ``ListFields`` requests and continue to iterate
    through the ``fields`` field on the
    corresponding responses.

    All the usual :class:`~.firestore_admin.ListFieldsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., firestore_admin.ListFieldsResponse],
        request: firestore_admin.ListFieldsRequest,
        response: firestore_admin.ListFieldsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (:class:`~.firestore_admin.ListFieldsRequest`):
                The initial request object.
            response (:class:`~.firestore_admin.ListFieldsResponse`):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = firestore_admin.ListFieldsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def pages(self) -> Iterable[firestore_admin.ListFieldsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = self._method(self._request, metadata=self._metadata)
            yield self._response

    def __iter__(self) -> Iterable[field.Field]:
        for page in self.pages:
            yield from page.fields

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListFieldsAsyncPager:
    """A pager for iterating through ``list_fields`` requests.

    This class thinly wraps an initial
    :class:`~.firestore_admin.ListFieldsResponse` object, and
    provides an ``__aiter__`` method to iterate through its
    ``fields`` field.

    If there are more pages, the ``__aiter__`` method will make additional
    ``ListFields`` requests and continue to iterate
    through the ``fields`` field on the
    corresponding responses.

    All the usual :class:`~.firestore_admin.ListFieldsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., Awaitable[firestore_admin.ListFieldsResponse]],
        request: firestore_admin.ListFieldsRequest,
        response: firestore_admin.ListFieldsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (:class:`~.firestore_admin.ListFieldsRequest`):
                The initial request object.
            response (:class:`~.firestore_admin.ListFieldsResponse`):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = firestore_admin.ListFieldsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    async def pages(self) -> AsyncIterable[firestore_admin.ListFieldsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = await self._method(self._request, metadata=self._metadata)
            yield self._response

    def __aiter__(self) -> AsyncIterable[field.Field]:
        async def async_generator():
            async for page in self.pages:
                for response in page.fields:
                    yield response

        return async_generator()

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)
