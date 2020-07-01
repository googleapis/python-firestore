# -*- coding: utf-8 -*-
#
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests."""

import mock
import pytest

from google.rpc import status_pb2

from google.cloud import firestore_admin_v1
from google.cloud.firestore_admin_v1.proto import field_pb2
from google.cloud.firestore_admin_v1.proto import firestore_admin_pb2
from google.cloud.firestore_admin_v1.proto import index_pb2
from google.cloud.firestore_admin_v1.proto import operation_pb2
from google.longrunning import operations_pb2
from google.protobuf import empty_pb2


class MultiCallableStub(object):
    """Stub for the grpc.UnaryUnaryMultiCallable interface."""

    def __init__(self, method, channel_stub):
        self.method = method
        self.channel_stub = channel_stub

    def __call__(self, request, timeout=None, metadata=None, credentials=None):
        self.channel_stub.requests.append((self.method, request))

        response = None
        if self.channel_stub.responses:
            response = self.channel_stub.responses.pop()

        if isinstance(response, Exception):
            raise response

        if response:
            return response


class ChannelStub(object):
    """Stub for the grpc.Channel interface."""

    def __init__(self, responses=[]):
        self.responses = responses
        self.requests = []

    def unary_unary(self, method, request_serializer=None, response_deserializer=None):
        return MultiCallableStub(method, self)


class CustomException(Exception):
    pass


class TestFirestoreAdminClient(object):
    def test_delete_index(self):
        channel = ChannelStub()
        patch = mock.patch("google.api_core.grpc_helpers.create_channel")
        with patch as create_channel:
            create_channel.return_value = channel
            client = firestore_admin_v1.FirestoreAdminClient()

        # Setup Request
        name = client.index_path("[PROJECT]", "[DATABASE]", "[COLLECTION]", "[INDEX]")

        client.delete_index(name)

        assert len(channel.requests) == 1
        expected_request = firestore_admin_pb2.DeleteIndexRequest(name=name)
        actual_request = channel.requests[0][1]
        assert expected_request == actual_request

    def test_delete_index_exception(self):
        # Mock the API response
        channel = ChannelStub(responses=[CustomException()])
        patch = mock.patch("google.api_core.grpc_helpers.create_channel")
        with patch as create_channel:
            create_channel.return_value = channel
            client = firestore_admin_v1.FirestoreAdminClient()

        # Setup request
        name = client.index_path("[PROJECT]", "[DATABASE]", "[COLLECTION]", "[INDEX]")

        with pytest.raises(CustomException):
            client.delete_index(name)

    def test_update_field(self):
        # Setup Expected Response
        name = "name3373707"
        expected_response = {"name": name}
        expected_response = field_pb2.Field(**expected_response)
        operation = operations_pb2.Operation(
            name="operations/test_update_field", done=True
        )
        operation.response.Pack(expected_response)

        # Mock the API response
        channel = ChannelStub(responses=[operation])
        patch = mock.patch("google.api_core.grpc_helpers.create_channel")
        with patch as create_channel:
            create_channel.return_value = channel
            client = firestore_admin_v1.FirestoreAdminClient()

        # Setup Request
        field = {}

        response = client.update_field(field)
        result = response.result()
        assert expected_response == result

        assert len(channel.requests) == 1
        expected_request = firestore_admin_pb2.UpdateFieldRequest(field=field)
        actual_request = channel.requests[0][1]
        assert expected_request == actual_request

    def test_update_field_exception(self):
        # Setup Response
        error = status_pb2.Status()
        operation = operations_pb2.Operation(
            name="operations/test_update_field_exception", done=True
        )
        operation.error.CopyFrom(error)

        # Mock the API response
        channel = ChannelStub(responses=[operation])
        patch = mock.patch("google.api_core.grpc_helpers.create_channel")
        with patch as create_channel:
            create_channel.return_value = channel
            client = firestore_admin_v1.FirestoreAdminClient()

        # Setup Request
        field = {}

        response = client.update_field(field)
        exception = response.exception()
        assert exception.errors[0] == error

    def test_create_index(self):
        # Setup Expected Response
        name = "name3373707"
        expected_response = {"name": name}
        expected_response = index_pb2.Index(**expected_response)
        operation = operations_pb2.Operation(
            name="operations/test_create_index", done=True
        )
        operation.response.Pack(expected_response)

        # Mock the API response
        channel = ChannelStub(responses=[operation])
        patch = mock.patch("google.api_core.grpc_helpers.create_channel")
        with patch as create_channel:
            create_channel.return_value = channel
            client = firestore_admin_v1.FirestoreAdminClient()

        # Setup Request
        parent = client.collection_group_path("[PROJECT]", "[DATABASE]", "[COLLECTION]")
        index = {}

        response = client.create_index(parent, index)
        result = response.result()
        assert expected_response == result

        assert len(channel.requests) == 1
        expected_request = firestore_admin_pb2.CreateIndexRequest(
            parent=parent, index=index
        )
        actual_request = channel.requests[0][1]
        assert expected_request == actual_request

    def test_create_index_exception(self):
        # Setup Response
        error = status_pb2.Status()
        operation = operations_pb2.Operation(
            name="operations/test_create_index_exception", done=True
        )
        operation.error.CopyFrom(error)

        # Mock the API response
        channel = ChannelStub(responses=[operation])
        patch = mock.patch("google.api_core.grpc_helpers.create_channel")
        with patch as create_channel:
            create_channel.return_value = channel
            client = firestore_admin_v1.FirestoreAdminClient()

        # Setup Request
        parent = client.collection_group_path("[PROJECT]", "[DATABASE]", "[COLLECTION]")
        index = {}

        response = client.create_index(parent, index)
        exception = response.exception()
        assert exception.errors[0] == error

    def test_list_indexes(self):
        # Setup Expected Response
        next_page_token = ""
        indexes_element = {}
        indexes = [indexes_element]
        expected_response = {"next_page_token": next_page_token, "indexes": indexes}
        expected_response = firestore_admin_pb2.ListIndexesResponse(**expected_response)

        # Mock the API response
        channel = ChannelStub(responses=[expected_response])
        patch = mock.patch("google.api_core.grpc_helpers.create_channel")
        with patch as create_channel:
            create_channel.return_value = channel
            client = firestore_admin_v1.FirestoreAdminClient()

        # Setup Request
        parent = client.collection_group_path("[PROJECT]", "[DATABASE]", "[COLLECTION]")

        paged_list_response = client.list_indexes(parent)
        resources = list(paged_list_response)
        assert len(resources) == 1

        assert expected_response.indexes[0] == resources[0]

        assert len(channel.requests) == 1
        expected_request = firestore_admin_pb2.ListIndexesRequest(parent=parent)
        actual_request = channel.requests[0][1]
        assert expected_request == actual_request

    def test_list_indexes_exception(self):
        channel = ChannelStub(responses=[CustomException()])
        patch = mock.patch("google.api_core.grpc_helpers.create_channel")
        with patch as create_channel:
            create_channel.return_value = channel
            client = firestore_admin_v1.FirestoreAdminClient()

        # Setup request
        parent = client.collection_group_path("[PROJECT]", "[DATABASE]", "[COLLECTION]")

        paged_list_response = client.list_indexes(parent)
        with pytest.raises(CustomException):
            list(paged_list_response)

    def test_get_index(self):
        # Setup Expected Response
        name_2 = "name2-1052831874"
        expected_response = {"name": name_2}
        expected_response = index_pb2.Index(**expected_response)

        # Mock the API response
        channel = ChannelStub(responses=[expected_response])
        patch = mock.patch("google.api_core.grpc_helpers.create_channel")
        with patch as create_channel:
            create_channel.return_value = channel
            client = firestore_admin_v1.FirestoreAdminClient()

        # Setup Request
        name = client.index_path("[PROJECT]", "[DATABASE]", "[COLLECTION]", "[INDEX]")

        response = client.get_index(name)
        assert expected_response == response

        assert len(channel.requests) == 1
        expected_request = firestore_admin_pb2.GetIndexRequest(name=name)
        actual_request = channel.requests[0][1]
        assert expected_request == actual_request

    def test_get_index_exception(self):
        # Mock the API response
        channel = ChannelStub(responses=[CustomException()])
        patch = mock.patch("google.api_core.grpc_helpers.create_channel")
        with patch as create_channel:
            create_channel.return_value = channel
            client = firestore_admin_v1.FirestoreAdminClient()

        # Setup request
        name = client.index_path("[PROJECT]", "[DATABASE]", "[COLLECTION]", "[INDEX]")

        with pytest.raises(CustomException):
            client.get_index(name)

    def test_get_field(self):
        # Setup Expected Response
        name_2 = "name2-1052831874"
        expected_response = {"name": name_2}
        expected_response = field_pb2.Field(**expected_response)

        # Mock the API response
        channel = ChannelStub(responses=[expected_response])
        patch = mock.patch("google.api_core.grpc_helpers.create_channel")
        with patch as create_channel:
            create_channel.return_value = channel
            client = firestore_admin_v1.FirestoreAdminClient()

        # Setup Request
        name = client.field_path("[PROJECT]", "[DATABASE]", "[COLLECTION]", "[FIELD]")

        response = client.get_field(name)
        assert expected_response == response

        assert len(channel.requests) == 1
        expected_request = firestore_admin_pb2.GetFieldRequest(name=name)
        actual_request = channel.requests[0][1]
        assert expected_request == actual_request

    def test_get_field_exception(self):
        # Mock the API response
        channel = ChannelStub(responses=[CustomException()])
        patch = mock.patch("google.api_core.grpc_helpers.create_channel")
        with patch as create_channel:
            create_channel.return_value = channel
            client = firestore_admin_v1.FirestoreAdminClient()

        # Setup request
        name = client.field_path("[PROJECT]", "[DATABASE]", "[COLLECTION]", "[FIELD]")

        with pytest.raises(CustomException):
            client.get_field(name)

    def test_list_fields(self):
        # Setup Expected Response
        next_page_token = ""
        fields_element = {}
        fields = [fields_element]
        expected_response = {"next_page_token": next_page_token, "fields": fields}
        expected_response = firestore_admin_pb2.ListFieldsResponse(**expected_response)

        # Mock the API response
        channel = ChannelStub(responses=[expected_response])
        patch = mock.patch("google.api_core.grpc_helpers.create_channel")
        with patch as create_channel:
            create_channel.return_value = channel
            client = firestore_admin_v1.FirestoreAdminClient()

        # Setup Request
        parent = client.collection_group_path("[PROJECT]", "[DATABASE]", "[COLLECTION]")

        paged_list_response = client.list_fields(parent)
        resources = list(paged_list_response)
        assert len(resources) == 1

        assert expected_response.fields[0] == resources[0]

        assert len(channel.requests) == 1
        expected_request = firestore_admin_pb2.ListFieldsRequest(parent=parent)
        actual_request = channel.requests[0][1]
        assert expected_request == actual_request

    def test_list_fields_exception(self):
        channel = ChannelStub(responses=[CustomException()])
        patch = mock.patch("google.api_core.grpc_helpers.create_channel")
        with patch as create_channel:
            create_channel.return_value = channel
            client = firestore_admin_v1.FirestoreAdminClient()

        # Setup request
        parent = client.collection_group_path("[PROJECT]", "[DATABASE]", "[COLLECTION]")

        paged_list_response = client.list_fields(parent)
        with pytest.raises(CustomException):
            list(paged_list_response)

    def test_export_documents(self):
        # Setup Expected Response
        output_uri_prefix = "outputUriPrefix124746435"
        expected_response = {"output_uri_prefix": output_uri_prefix}
        expected_response = operation_pb2.ExportDocumentsResponse(**expected_response)
        operation = operations_pb2.Operation(
            name="operations/test_export_documents", done=True
        )
        operation.response.Pack(expected_response)

        # Mock the API response
        channel = ChannelStub(responses=[operation])
        patch = mock.patch("google.api_core.grpc_helpers.create_channel")
        with patch as create_channel:
            create_channel.return_value = channel
            client = firestore_admin_v1.FirestoreAdminClient()

        # Setup Request
        name = client.database_path("[PROJECT]", "[DATABASE]")

        response = client.export_documents(name)
        result = response.result()
        assert expected_response == result

        assert len(channel.requests) == 1
        expected_request = firestore_admin_pb2.ExportDocumentsRequest(name=name)
        actual_request = channel.requests[0][1]
        assert expected_request == actual_request

    def test_export_documents_exception(self):
        # Setup Response
        error = status_pb2.Status()
        operation = operations_pb2.Operation(
            name="operations/test_export_documents_exception", done=True
        )
        operation.error.CopyFrom(error)

        # Mock the API response
        channel = ChannelStub(responses=[operation])
        patch = mock.patch("google.api_core.grpc_helpers.create_channel")
        with patch as create_channel:
            create_channel.return_value = channel
            client = firestore_admin_v1.FirestoreAdminClient()

        # Setup Request
        name = client.database_path("[PROJECT]", "[DATABASE]")

        response = client.export_documents(name)
        exception = response.exception()
        assert exception.errors[0] == error

    def test_import_documents(self):
        # Setup Expected Response
        expected_response = {}
        expected_response = empty_pb2.Empty(**expected_response)
        operation = operations_pb2.Operation(
            name="operations/test_import_documents", done=True
        )
        operation.response.Pack(expected_response)

        # Mock the API response
        channel = ChannelStub(responses=[operation])
        patch = mock.patch("google.api_core.grpc_helpers.create_channel")
        with patch as create_channel:
            create_channel.return_value = channel
            client = firestore_admin_v1.FirestoreAdminClient()

        # Setup Request
        name = client.database_path("[PROJECT]", "[DATABASE]")

        response = client.import_documents(name)
        result = response.result()
        assert expected_response == result

        assert len(channel.requests) == 1
        expected_request = firestore_admin_pb2.ImportDocumentsRequest(name=name)
        actual_request = channel.requests[0][1]
        assert expected_request == actual_request

    def test_import_documents_exception(self):
        # Setup Response
        error = status_pb2.Status()
        operation = operations_pb2.Operation(
            name="operations/test_import_documents_exception", done=True
        )
        operation.error.CopyFrom(error)

        # Mock the API response
        channel = ChannelStub(responses=[operation])
        patch = mock.patch("google.api_core.grpc_helpers.create_channel")
        with patch as create_channel:
            create_channel.return_value = channel
            client = firestore_admin_v1.FirestoreAdminClient()

        # Setup Request
        name = client.database_path("[PROJECT]", "[DATABASE]")

        response = client.import_documents(name)
        exception = response.exception()
        assert exception.errors[0] == error
