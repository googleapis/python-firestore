# -*- coding: utf-8 -*-
# Copyright 2022 Google LLC
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
import os

# try/except added for compatibility with python < 3.8
try:
    from unittest import mock
    from unittest.mock import AsyncMock  # pragma: NO COVER
except ImportError:  # pragma: NO COVER
    import mock

import grpc
from grpc.experimental import aio
from collections.abc import Iterable
from google.protobuf import json_format
import json
import math
import pytest
from proto.marshal.rules.dates import DurationRule, TimestampRule
from proto.marshal.rules import wrappers
from requests import Response
from requests import Request, PreparedRequest
from requests.sessions import Session
from google.protobuf import json_format

from google.api_core import client_options
from google.api_core import exceptions as core_exceptions
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.api_core import path_template
from google.auth import credentials as ga_credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.firestore_v1.services.firestore import FirestoreAsyncClient
from google.cloud.firestore_v1.services.firestore import FirestoreClient
from google.cloud.firestore_v1.services.firestore import pagers
from google.cloud.firestore_v1.services.firestore import transports
from google.cloud.firestore_v1.types import aggregation_result
from google.cloud.firestore_v1.types import common
from google.cloud.firestore_v1.types import document
from google.cloud.firestore_v1.types import document as gf_document
from google.cloud.firestore_v1.types import firestore
from google.cloud.firestore_v1.types import query
from google.cloud.firestore_v1.types import write as gf_write
from google.cloud.location import locations_pb2
from google.longrunning import operations_pb2
from google.oauth2 import service_account
from google.protobuf import struct_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from google.protobuf import wrappers_pb2  # type: ignore
from google.rpc import status_pb2  # type: ignore
from google.type import latlng_pb2  # type: ignore
import google.auth


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


# If default endpoint is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint(client):
    return (
        "foo.googleapis.com"
        if ("localhost" in client.DEFAULT_ENDPOINT)
        else client.DEFAULT_ENDPOINT
    )


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert FirestoreClient._get_default_mtls_endpoint(None) is None
    assert FirestoreClient._get_default_mtls_endpoint(api_endpoint) == api_mtls_endpoint
    assert (
        FirestoreClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        FirestoreClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        FirestoreClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert FirestoreClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi


@pytest.mark.parametrize(
    "client_class,transport_name",
    [
        (FirestoreClient, "grpc"),
        (FirestoreAsyncClient, "grpc_asyncio"),
        (FirestoreClient, "rest"),
    ],
)
def test_firestore_client_from_service_account_info(client_class, transport_name):
    creds = ga_credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_info"
    ) as factory:
        factory.return_value = creds
        info = {"valid": True}
        client = client_class.from_service_account_info(info, transport=transport_name)
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == (
            "firestore.googleapis.com:443"
            if transport_name in ["grpc", "grpc_asyncio"]
            else "https://firestore.googleapis.com"
        )


@pytest.mark.parametrize(
    "transport_class,transport_name",
    [
        (transports.FirestoreGrpcTransport, "grpc"),
        (transports.FirestoreGrpcAsyncIOTransport, "grpc_asyncio"),
        (transports.FirestoreRestTransport, "rest"),
    ],
)
def test_firestore_client_service_account_always_use_jwt(
    transport_class, transport_name
):
    with mock.patch.object(
        service_account.Credentials, "with_always_use_jwt_access", create=True
    ) as use_jwt:
        creds = service_account.Credentials(None, None, None)
        transport = transport_class(credentials=creds, always_use_jwt_access=True)
        use_jwt.assert_called_once_with(True)

    with mock.patch.object(
        service_account.Credentials, "with_always_use_jwt_access", create=True
    ) as use_jwt:
        creds = service_account.Credentials(None, None, None)
        transport = transport_class(credentials=creds, always_use_jwt_access=False)
        use_jwt.assert_not_called()


@pytest.mark.parametrize(
    "client_class,transport_name",
    [
        (FirestoreClient, "grpc"),
        (FirestoreAsyncClient, "grpc_asyncio"),
        (FirestoreClient, "rest"),
    ],
)
def test_firestore_client_from_service_account_file(client_class, transport_name):
    creds = ga_credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file(
            "dummy/file/path.json", transport=transport_name
        )
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        client = client_class.from_service_account_json(
            "dummy/file/path.json", transport=transport_name
        )
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == (
            "firestore.googleapis.com:443"
            if transport_name in ["grpc", "grpc_asyncio"]
            else "https://firestore.googleapis.com"
        )


def test_firestore_client_get_transport_class():
    transport = FirestoreClient.get_transport_class()
    available_transports = [
        transports.FirestoreGrpcTransport,
        transports.FirestoreRestTransport,
    ]
    assert transport in available_transports

    transport = FirestoreClient.get_transport_class("grpc")
    assert transport == transports.FirestoreGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (FirestoreClient, transports.FirestoreGrpcTransport, "grpc"),
        (
            FirestoreAsyncClient,
            transports.FirestoreGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
        (FirestoreClient, transports.FirestoreRestTransport, "rest"),
    ],
)
@mock.patch.object(
    FirestoreClient, "DEFAULT_ENDPOINT", modify_default_endpoint(FirestoreClient)
)
@mock.patch.object(
    FirestoreAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(FirestoreAsyncClient),
)
def test_firestore_client_client_options(client_class, transport_class, transport_name):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(FirestoreClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=ga_credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(FirestoreClient, "get_transport_class") as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(transport=transport_name, client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(transport=transport_name)
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
                api_audience=None,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(transport=transport_name)
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
                api_audience=None,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError):
            client = client_class(transport=transport_name)

    # Check the case GOOGLE_API_USE_CLIENT_CERTIFICATE has unsupported value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError):
            client = client_class(transport=transport_name)

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id="octopus",
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )
    # Check the case api_endpoint is provided
    options = client_options.ClientOptions(
        api_audience="https://language.googleapis.com"
    )
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience="https://language.googleapis.com",
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,use_client_cert_env",
    [
        (FirestoreClient, transports.FirestoreGrpcTransport, "grpc", "true"),
        (
            FirestoreAsyncClient,
            transports.FirestoreGrpcAsyncIOTransport,
            "grpc_asyncio",
            "true",
        ),
        (FirestoreClient, transports.FirestoreGrpcTransport, "grpc", "false"),
        (
            FirestoreAsyncClient,
            transports.FirestoreGrpcAsyncIOTransport,
            "grpc_asyncio",
            "false",
        ),
        (FirestoreClient, transports.FirestoreRestTransport, "rest", "true"),
        (FirestoreClient, transports.FirestoreRestTransport, "rest", "false"),
    ],
)
@mock.patch.object(
    FirestoreClient, "DEFAULT_ENDPOINT", modify_default_endpoint(FirestoreClient)
)
@mock.patch.object(
    FirestoreAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(FirestoreAsyncClient),
)
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_firestore_client_mtls_env_auto(
    client_class, transport_class, transport_name, use_client_cert_env
):
    # This tests the endpoint autoswitch behavior. Endpoint is autoswitched to the default
    # mtls endpoint, if GOOGLE_API_USE_CLIENT_CERTIFICATE is "true" and client cert exists.

    # Check the case client_cert_source is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        options = client_options.ClientOptions(
            client_cert_source=client_cert_source_callback
        )
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(client_options=options, transport=transport_name)

            if use_client_cert_env == "false":
                expected_client_cert_source = None
                expected_host = client.DEFAULT_ENDPOINT
            else:
                expected_client_cert_source = client_cert_source_callback
                expected_host = client.DEFAULT_MTLS_ENDPOINT

            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=expected_host,
                scopes=None,
                client_cert_source_for_mtls=expected_client_cert_source,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
                api_audience=None,
            )

    # Check the case ADC client cert is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=True,
            ):
                with mock.patch(
                    "google.auth.transport.mtls.default_client_cert_source",
                    return_value=client_cert_source_callback,
                ):
                    if use_client_cert_env == "false":
                        expected_host = client.DEFAULT_ENDPOINT
                        expected_client_cert_source = None
                    else:
                        expected_host = client.DEFAULT_MTLS_ENDPOINT
                        expected_client_cert_source = client_cert_source_callback

                    patched.return_value = None
                    client = client_class(transport=transport_name)
                    patched.assert_called_once_with(
                        credentials=None,
                        credentials_file=None,
                        host=expected_host,
                        scopes=None,
                        client_cert_source_for_mtls=expected_client_cert_source,
                        quota_project_id=None,
                        client_info=transports.base.DEFAULT_CLIENT_INFO,
                        always_use_jwt_access=True,
                        api_audience=None,
                    )

    # Check the case client_cert_source and ADC client cert are not provided.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=False,
            ):
                patched.return_value = None
                client = client_class(transport=transport_name)
                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=client.DEFAULT_ENDPOINT,
                    scopes=None,
                    client_cert_source_for_mtls=None,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                    always_use_jwt_access=True,
                    api_audience=None,
                )


@pytest.mark.parametrize("client_class", [FirestoreClient, FirestoreAsyncClient])
@mock.patch.object(
    FirestoreClient, "DEFAULT_ENDPOINT", modify_default_endpoint(FirestoreClient)
)
@mock.patch.object(
    FirestoreAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(FirestoreAsyncClient),
)
def test_firestore_client_get_mtls_endpoint_and_cert_source(client_class):
    mock_client_cert_source = mock.Mock()

    # Test the case GOOGLE_API_USE_CLIENT_CERTIFICATE is "true".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        mock_api_endpoint = "foo"
        options = client_options.ClientOptions(
            client_cert_source=mock_client_cert_source, api_endpoint=mock_api_endpoint
        )
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source(
            options
        )
        assert api_endpoint == mock_api_endpoint
        assert cert_source == mock_client_cert_source

    # Test the case GOOGLE_API_USE_CLIENT_CERTIFICATE is "false".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "false"}):
        mock_client_cert_source = mock.Mock()
        mock_api_endpoint = "foo"
        options = client_options.ClientOptions(
            client_cert_source=mock_client_cert_source, api_endpoint=mock_api_endpoint
        )
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source(
            options
        )
        assert api_endpoint == mock_api_endpoint
        assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source()
        assert api_endpoint == client_class.DEFAULT_ENDPOINT
        assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source()
        assert api_endpoint == client_class.DEFAULT_MTLS_ENDPOINT
        assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "auto" and default cert doesn't exist.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        with mock.patch(
            "google.auth.transport.mtls.has_default_client_cert_source",
            return_value=False,
        ):
            api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source()
            assert api_endpoint == client_class.DEFAULT_ENDPOINT
            assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "auto" and default cert exists.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        with mock.patch(
            "google.auth.transport.mtls.has_default_client_cert_source",
            return_value=True,
        ):
            with mock.patch(
                "google.auth.transport.mtls.default_client_cert_source",
                return_value=mock_client_cert_source,
            ):
                (
                    api_endpoint,
                    cert_source,
                ) = client_class.get_mtls_endpoint_and_cert_source()
                assert api_endpoint == client_class.DEFAULT_MTLS_ENDPOINT
                assert cert_source == mock_client_cert_source


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (FirestoreClient, transports.FirestoreGrpcTransport, "grpc"),
        (
            FirestoreAsyncClient,
            transports.FirestoreGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
        (FirestoreClient, transports.FirestoreRestTransport, "rest"),
    ],
)
def test_firestore_client_client_options_scopes(
    client_class, transport_class, transport_name
):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(
        scopes=["1", "2"],
    )
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=["1", "2"],
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,grpc_helpers",
    [
        (FirestoreClient, transports.FirestoreGrpcTransport, "grpc", grpc_helpers),
        (
            FirestoreAsyncClient,
            transports.FirestoreGrpcAsyncIOTransport,
            "grpc_asyncio",
            grpc_helpers_async,
        ),
        (FirestoreClient, transports.FirestoreRestTransport, "rest", None),
    ],
)
def test_firestore_client_client_options_credentials_file(
    client_class, transport_class, transport_name, grpc_helpers
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")

    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )


def test_firestore_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.firestore_v1.services.firestore.transports.FirestoreGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = FirestoreClient(client_options={"api_endpoint": "squid.clam.whelk"})
        grpc_transport.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,grpc_helpers",
    [
        (FirestoreClient, transports.FirestoreGrpcTransport, "grpc", grpc_helpers),
        (
            FirestoreAsyncClient,
            transports.FirestoreGrpcAsyncIOTransport,
            "grpc_asyncio",
            grpc_helpers_async,
        ),
    ],
)
def test_firestore_client_create_channel_credentials_file(
    client_class, transport_class, transport_name, grpc_helpers
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")

    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )

    # test that the credentials from file are saved and used as the credentials.
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch.object(
        google.auth, "default", autospec=True
    ) as adc, mock.patch.object(
        grpc_helpers, "create_channel"
    ) as create_channel:
        creds = ga_credentials.AnonymousCredentials()
        file_creds = ga_credentials.AnonymousCredentials()
        load_creds.return_value = (file_creds, None)
        adc.return_value = (creds, None)
        client = client_class(client_options=options, transport=transport_name)
        create_channel.assert_called_with(
            "firestore.googleapis.com:443",
            credentials=file_creds,
            credentials_file=None,
            quota_project_id=None,
            default_scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/datastore",
            ),
            scopes=None,
            default_host="firestore.googleapis.com",
            ssl_credentials=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.GetDocumentRequest,
        dict,
    ],
)
def test_get_document(request_type, transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_document), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = document.Document(
            name="name_value",
        )
        response = client.get_document(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.GetDocumentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, document.Document)
    assert response.name == "name_value"


def test_get_document_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_document), "__call__") as call:
        client.get_document()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.GetDocumentRequest()


@pytest.mark.asyncio
async def test_get_document_async(
    transport: str = "grpc_asyncio", request_type=firestore.GetDocumentRequest
):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_document), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            document.Document(
                name="name_value",
            )
        )
        response = await client.get_document(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.GetDocumentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, document.Document)
    assert response.name == "name_value"


@pytest.mark.asyncio
async def test_get_document_async_from_dict():
    await test_get_document_async(request_type=dict)


def test_get_document_field_headers():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.GetDocumentRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_document), "__call__") as call:
        call.return_value = document.Document()
        client.get_document(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_document_field_headers_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.GetDocumentRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_document), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(document.Document())
        await client.get_document(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.ListDocumentsRequest,
        dict,
    ],
)
def test_list_documents(request_type, transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_documents), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.ListDocumentsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_documents(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.ListDocumentsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDocumentsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_documents_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_documents), "__call__") as call:
        client.list_documents()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.ListDocumentsRequest()


@pytest.mark.asyncio
async def test_list_documents_async(
    transport: str = "grpc_asyncio", request_type=firestore.ListDocumentsRequest
):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_documents), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.ListDocumentsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_documents(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.ListDocumentsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDocumentsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_documents_async_from_dict():
    await test_list_documents_async(request_type=dict)


def test_list_documents_field_headers():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.ListDocumentsRequest()

    request.parent = "parent_value"
    request.collection_id = "collection_id_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_documents), "__call__") as call:
        call.return_value = firestore.ListDocumentsResponse()
        client.list_documents(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value&collection_id=collection_id_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_documents_field_headers_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.ListDocumentsRequest()

    request.parent = "parent_value"
    request.collection_id = "collection_id_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_documents), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.ListDocumentsResponse()
        )
        await client.list_documents(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value&collection_id=collection_id_value",
    ) in kw["metadata"]


def test_list_documents_pager(transport_name: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials,
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_documents), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                    document.Document(),
                    document.Document(),
                ],
                next_page_token="abc",
            ),
            firestore.ListDocumentsResponse(
                documents=[],
                next_page_token="def",
            ),
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                ],
                next_page_token="ghi",
            ),
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                    document.Document(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (
                    ("parent", ""),
                    ("collection_id", ""),
                )
            ),
        )
        pager = client.list_documents(request={})

        assert pager._metadata == metadata

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, document.Document) for i in results)


def test_list_documents_pages(transport_name: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials,
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_documents), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                    document.Document(),
                    document.Document(),
                ],
                next_page_token="abc",
            ),
            firestore.ListDocumentsResponse(
                documents=[],
                next_page_token="def",
            ),
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                ],
                next_page_token="ghi",
            ),
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                    document.Document(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_documents(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_documents_async_pager():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_documents), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                    document.Document(),
                    document.Document(),
                ],
                next_page_token="abc",
            ),
            firestore.ListDocumentsResponse(
                documents=[],
                next_page_token="def",
            ),
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                ],
                next_page_token="ghi",
            ),
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                    document.Document(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_documents(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, document.Document) for i in responses)


@pytest.mark.asyncio
async def test_list_documents_async_pages():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_documents), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                    document.Document(),
                    document.Document(),
                ],
                next_page_token="abc",
            ),
            firestore.ListDocumentsResponse(
                documents=[],
                next_page_token="def",
            ),
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                ],
                next_page_token="ghi",
            ),
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                    document.Document(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (
            await client.list_documents(request={})
        ).pages:  # pragma: no branch
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.UpdateDocumentRequest,
        dict,
    ],
)
def test_update_document(request_type, transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_document), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gf_document.Document(
            name="name_value",
        )
        response = client.update_document(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.UpdateDocumentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gf_document.Document)
    assert response.name == "name_value"


def test_update_document_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_document), "__call__") as call:
        client.update_document()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.UpdateDocumentRequest()


@pytest.mark.asyncio
async def test_update_document_async(
    transport: str = "grpc_asyncio", request_type=firestore.UpdateDocumentRequest
):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_document), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gf_document.Document(
                name="name_value",
            )
        )
        response = await client.update_document(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.UpdateDocumentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gf_document.Document)
    assert response.name == "name_value"


@pytest.mark.asyncio
async def test_update_document_async_from_dict():
    await test_update_document_async(request_type=dict)


def test_update_document_field_headers():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.UpdateDocumentRequest()

    request.document.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_document), "__call__") as call:
        call.return_value = gf_document.Document()
        client.update_document(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "document.name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_document_field_headers_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.UpdateDocumentRequest()

    request.document.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_document), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gf_document.Document()
        )
        await client.update_document(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "document.name=name_value",
    ) in kw["metadata"]


def test_update_document_flattened():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_document), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gf_document.Document()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_document(
            document=gf_document.Document(name="name_value"),
            update_mask=common.DocumentMask(field_paths=["field_paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].document
        mock_val = gf_document.Document(name="name_value")
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = common.DocumentMask(field_paths=["field_paths_value"])
        assert arg == mock_val


def test_update_document_flattened_error():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_document(
            firestore.UpdateDocumentRequest(),
            document=gf_document.Document(name="name_value"),
            update_mask=common.DocumentMask(field_paths=["field_paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_document_flattened_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_document), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gf_document.Document()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gf_document.Document()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_document(
            document=gf_document.Document(name="name_value"),
            update_mask=common.DocumentMask(field_paths=["field_paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].document
        mock_val = gf_document.Document(name="name_value")
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = common.DocumentMask(field_paths=["field_paths_value"])
        assert arg == mock_val


@pytest.mark.asyncio
async def test_update_document_flattened_error_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_document(
            firestore.UpdateDocumentRequest(),
            document=gf_document.Document(name="name_value"),
            update_mask=common.DocumentMask(field_paths=["field_paths_value"]),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.DeleteDocumentRequest,
        dict,
    ],
)
def test_delete_document(request_type, transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_document), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.delete_document(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.DeleteDocumentRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_document_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_document), "__call__") as call:
        client.delete_document()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.DeleteDocumentRequest()


@pytest.mark.asyncio
async def test_delete_document_async(
    transport: str = "grpc_asyncio", request_type=firestore.DeleteDocumentRequest
):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_document), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.delete_document(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.DeleteDocumentRequest()

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_delete_document_async_from_dict():
    await test_delete_document_async(request_type=dict)


def test_delete_document_field_headers():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.DeleteDocumentRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_document), "__call__") as call:
        call.return_value = None
        client.delete_document(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_document_field_headers_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.DeleteDocumentRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_document), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.delete_document(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


def test_delete_document_flattened():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_document), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_document(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_delete_document_flattened_error():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_document(
            firestore.DeleteDocumentRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_document_flattened_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_document), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_document(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_delete_document_flattened_error_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_document(
            firestore.DeleteDocumentRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.BatchGetDocumentsRequest,
        dict,
    ],
)
def test_batch_get_documents(request_type, transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_get_documents), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = iter([firestore.BatchGetDocumentsResponse()])
        response = client.batch_get_documents(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.BatchGetDocumentsRequest()

    # Establish that the response is the type that we expect.
    for message in response:
        assert isinstance(message, firestore.BatchGetDocumentsResponse)


def test_batch_get_documents_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_get_documents), "__call__"
    ) as call:
        client.batch_get_documents()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.BatchGetDocumentsRequest()


@pytest.mark.asyncio
async def test_batch_get_documents_async(
    transport: str = "grpc_asyncio", request_type=firestore.BatchGetDocumentsRequest
):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_get_documents), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = mock.Mock(aio.UnaryStreamCall, autospec=True)
        call.return_value.read = mock.AsyncMock(
            side_effect=[firestore.BatchGetDocumentsResponse()]
        )
        response = await client.batch_get_documents(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.BatchGetDocumentsRequest()

    # Establish that the response is the type that we expect.
    message = await response.read()
    assert isinstance(message, firestore.BatchGetDocumentsResponse)


@pytest.mark.asyncio
async def test_batch_get_documents_async_from_dict():
    await test_batch_get_documents_async(request_type=dict)


def test_batch_get_documents_field_headers():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.BatchGetDocumentsRequest()

    request.database = "database_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_get_documents), "__call__"
    ) as call:
        call.return_value = iter([firestore.BatchGetDocumentsResponse()])
        client.batch_get_documents(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "database=database_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_batch_get_documents_field_headers_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.BatchGetDocumentsRequest()

    request.database = "database_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_get_documents), "__call__"
    ) as call:
        call.return_value = mock.Mock(aio.UnaryStreamCall, autospec=True)
        call.return_value.read = mock.AsyncMock(
            side_effect=[firestore.BatchGetDocumentsResponse()]
        )
        await client.batch_get_documents(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "database=database_value",
    ) in kw["metadata"]


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.BeginTransactionRequest,
        dict,
    ],
)
def test_begin_transaction(request_type, transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.begin_transaction), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.BeginTransactionResponse(
            transaction=b"transaction_blob",
        )
        response = client.begin_transaction(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.BeginTransactionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, firestore.BeginTransactionResponse)
    assert response.transaction == b"transaction_blob"


def test_begin_transaction_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.begin_transaction), "__call__"
    ) as call:
        client.begin_transaction()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.BeginTransactionRequest()


@pytest.mark.asyncio
async def test_begin_transaction_async(
    transport: str = "grpc_asyncio", request_type=firestore.BeginTransactionRequest
):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.begin_transaction), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.BeginTransactionResponse(
                transaction=b"transaction_blob",
            )
        )
        response = await client.begin_transaction(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.BeginTransactionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, firestore.BeginTransactionResponse)
    assert response.transaction == b"transaction_blob"


@pytest.mark.asyncio
async def test_begin_transaction_async_from_dict():
    await test_begin_transaction_async(request_type=dict)


def test_begin_transaction_field_headers():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.BeginTransactionRequest()

    request.database = "database_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.begin_transaction), "__call__"
    ) as call:
        call.return_value = firestore.BeginTransactionResponse()
        client.begin_transaction(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "database=database_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_begin_transaction_field_headers_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.BeginTransactionRequest()

    request.database = "database_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.begin_transaction), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.BeginTransactionResponse()
        )
        await client.begin_transaction(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "database=database_value",
    ) in kw["metadata"]


def test_begin_transaction_flattened():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.begin_transaction), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.BeginTransactionResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.begin_transaction(
            database="database_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].database
        mock_val = "database_value"
        assert arg == mock_val


def test_begin_transaction_flattened_error():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.begin_transaction(
            firestore.BeginTransactionRequest(),
            database="database_value",
        )


@pytest.mark.asyncio
async def test_begin_transaction_flattened_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.begin_transaction), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.BeginTransactionResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.BeginTransactionResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.begin_transaction(
            database="database_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].database
        mock_val = "database_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_begin_transaction_flattened_error_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.begin_transaction(
            firestore.BeginTransactionRequest(),
            database="database_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.CommitRequest,
        dict,
    ],
)
def test_commit(request_type, transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.commit), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.CommitResponse()
        response = client.commit(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.CommitRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, firestore.CommitResponse)


def test_commit_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.commit), "__call__") as call:
        client.commit()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.CommitRequest()


@pytest.mark.asyncio
async def test_commit_async(
    transport: str = "grpc_asyncio", request_type=firestore.CommitRequest
):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.commit), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.CommitResponse()
        )
        response = await client.commit(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.CommitRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, firestore.CommitResponse)


@pytest.mark.asyncio
async def test_commit_async_from_dict():
    await test_commit_async(request_type=dict)


def test_commit_field_headers():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.CommitRequest()

    request.database = "database_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.commit), "__call__") as call:
        call.return_value = firestore.CommitResponse()
        client.commit(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "database=database_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_commit_field_headers_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.CommitRequest()

    request.database = "database_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.commit), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.CommitResponse()
        )
        await client.commit(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "database=database_value",
    ) in kw["metadata"]


def test_commit_flattened():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.commit), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.CommitResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.commit(
            database="database_value",
            writes=[gf_write.Write(update=document.Document(name="name_value"))],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].database
        mock_val = "database_value"
        assert arg == mock_val
        arg = args[0].writes
        mock_val = [gf_write.Write(update=document.Document(name="name_value"))]
        assert arg == mock_val


def test_commit_flattened_error():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.commit(
            firestore.CommitRequest(),
            database="database_value",
            writes=[gf_write.Write(update=document.Document(name="name_value"))],
        )


@pytest.mark.asyncio
async def test_commit_flattened_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.commit), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.CommitResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.CommitResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.commit(
            database="database_value",
            writes=[gf_write.Write(update=document.Document(name="name_value"))],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].database
        mock_val = "database_value"
        assert arg == mock_val
        arg = args[0].writes
        mock_val = [gf_write.Write(update=document.Document(name="name_value"))]
        assert arg == mock_val


@pytest.mark.asyncio
async def test_commit_flattened_error_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.commit(
            firestore.CommitRequest(),
            database="database_value",
            writes=[gf_write.Write(update=document.Document(name="name_value"))],
        )


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.RollbackRequest,
        dict,
    ],
)
def test_rollback(request_type, transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.rollback), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.rollback(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.RollbackRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_rollback_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.rollback), "__call__") as call:
        client.rollback()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.RollbackRequest()


@pytest.mark.asyncio
async def test_rollback_async(
    transport: str = "grpc_asyncio", request_type=firestore.RollbackRequest
):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.rollback), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.rollback(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.RollbackRequest()

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_rollback_async_from_dict():
    await test_rollback_async(request_type=dict)


def test_rollback_field_headers():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.RollbackRequest()

    request.database = "database_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.rollback), "__call__") as call:
        call.return_value = None
        client.rollback(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "database=database_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_rollback_field_headers_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.RollbackRequest()

    request.database = "database_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.rollback), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.rollback(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "database=database_value",
    ) in kw["metadata"]


def test_rollback_flattened():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.rollback), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.rollback(
            database="database_value",
            transaction=b"transaction_blob",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].database
        mock_val = "database_value"
        assert arg == mock_val
        arg = args[0].transaction
        mock_val = b"transaction_blob"
        assert arg == mock_val


def test_rollback_flattened_error():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.rollback(
            firestore.RollbackRequest(),
            database="database_value",
            transaction=b"transaction_blob",
        )


@pytest.mark.asyncio
async def test_rollback_flattened_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.rollback), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.rollback(
            database="database_value",
            transaction=b"transaction_blob",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].database
        mock_val = "database_value"
        assert arg == mock_val
        arg = args[0].transaction
        mock_val = b"transaction_blob"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_rollback_flattened_error_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.rollback(
            firestore.RollbackRequest(),
            database="database_value",
            transaction=b"transaction_blob",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.RunQueryRequest,
        dict,
    ],
)
def test_run_query(request_type, transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.run_query), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = iter([firestore.RunQueryResponse()])
        response = client.run_query(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.RunQueryRequest()

    # Establish that the response is the type that we expect.
    for message in response:
        assert isinstance(message, firestore.RunQueryResponse)


def test_run_query_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.run_query), "__call__") as call:
        client.run_query()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.RunQueryRequest()


@pytest.mark.asyncio
async def test_run_query_async(
    transport: str = "grpc_asyncio", request_type=firestore.RunQueryRequest
):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.run_query), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = mock.Mock(aio.UnaryStreamCall, autospec=True)
        call.return_value.read = mock.AsyncMock(
            side_effect=[firestore.RunQueryResponse()]
        )
        response = await client.run_query(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.RunQueryRequest()

    # Establish that the response is the type that we expect.
    message = await response.read()
    assert isinstance(message, firestore.RunQueryResponse)


@pytest.mark.asyncio
async def test_run_query_async_from_dict():
    await test_run_query_async(request_type=dict)


def test_run_query_field_headers():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.RunQueryRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.run_query), "__call__") as call:
        call.return_value = iter([firestore.RunQueryResponse()])
        client.run_query(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_run_query_field_headers_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.RunQueryRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.run_query), "__call__") as call:
        call.return_value = mock.Mock(aio.UnaryStreamCall, autospec=True)
        call.return_value.read = mock.AsyncMock(
            side_effect=[firestore.RunQueryResponse()]
        )
        await client.run_query(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.RunAggregationQueryRequest,
        dict,
    ],
)
def test_run_aggregation_query(request_type, transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.run_aggregation_query), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = iter([firestore.RunAggregationQueryResponse()])
        response = client.run_aggregation_query(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.RunAggregationQueryRequest()

    # Establish that the response is the type that we expect.
    for message in response:
        assert isinstance(message, firestore.RunAggregationQueryResponse)


def test_run_aggregation_query_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.run_aggregation_query), "__call__"
    ) as call:
        client.run_aggregation_query()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.RunAggregationQueryRequest()


@pytest.mark.asyncio
async def test_run_aggregation_query_async(
    transport: str = "grpc_asyncio", request_type=firestore.RunAggregationQueryRequest
):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.run_aggregation_query), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = mock.Mock(aio.UnaryStreamCall, autospec=True)
        call.return_value.read = mock.AsyncMock(
            side_effect=[firestore.RunAggregationQueryResponse()]
        )
        response = await client.run_aggregation_query(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.RunAggregationQueryRequest()

    # Establish that the response is the type that we expect.
    message = await response.read()
    assert isinstance(message, firestore.RunAggregationQueryResponse)


@pytest.mark.asyncio
async def test_run_aggregation_query_async_from_dict():
    await test_run_aggregation_query_async(request_type=dict)


def test_run_aggregation_query_field_headers():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.RunAggregationQueryRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.run_aggregation_query), "__call__"
    ) as call:
        call.return_value = iter([firestore.RunAggregationQueryResponse()])
        client.run_aggregation_query(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_run_aggregation_query_field_headers_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.RunAggregationQueryRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.run_aggregation_query), "__call__"
    ) as call:
        call.return_value = mock.Mock(aio.UnaryStreamCall, autospec=True)
        call.return_value.read = mock.AsyncMock(
            side_effect=[firestore.RunAggregationQueryResponse()]
        )
        await client.run_aggregation_query(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.PartitionQueryRequest,
        dict,
    ],
)
def test_partition_query(request_type, transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.partition_query), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.PartitionQueryResponse(
            next_page_token="next_page_token_value",
        )
        response = client.partition_query(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.PartitionQueryRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.PartitionQueryPager)
    assert response.next_page_token == "next_page_token_value"


def test_partition_query_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.partition_query), "__call__") as call:
        client.partition_query()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.PartitionQueryRequest()


@pytest.mark.asyncio
async def test_partition_query_async(
    transport: str = "grpc_asyncio", request_type=firestore.PartitionQueryRequest
):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.partition_query), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.PartitionQueryResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.partition_query(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.PartitionQueryRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.PartitionQueryAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_partition_query_async_from_dict():
    await test_partition_query_async(request_type=dict)


def test_partition_query_field_headers():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.PartitionQueryRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.partition_query), "__call__") as call:
        call.return_value = firestore.PartitionQueryResponse()
        client.partition_query(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_partition_query_field_headers_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.PartitionQueryRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.partition_query), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.PartitionQueryResponse()
        )
        await client.partition_query(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


def test_partition_query_pager(transport_name: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials,
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.partition_query), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            firestore.PartitionQueryResponse(
                partitions=[
                    query.Cursor(),
                    query.Cursor(),
                    query.Cursor(),
                ],
                next_page_token="abc",
            ),
            firestore.PartitionQueryResponse(
                partitions=[],
                next_page_token="def",
            ),
            firestore.PartitionQueryResponse(
                partitions=[
                    query.Cursor(),
                ],
                next_page_token="ghi",
            ),
            firestore.PartitionQueryResponse(
                partitions=[
                    query.Cursor(),
                    query.Cursor(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.partition_query(request={})

        assert pager._metadata == metadata

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, query.Cursor) for i in results)


def test_partition_query_pages(transport_name: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials,
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.partition_query), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            firestore.PartitionQueryResponse(
                partitions=[
                    query.Cursor(),
                    query.Cursor(),
                    query.Cursor(),
                ],
                next_page_token="abc",
            ),
            firestore.PartitionQueryResponse(
                partitions=[],
                next_page_token="def",
            ),
            firestore.PartitionQueryResponse(
                partitions=[
                    query.Cursor(),
                ],
                next_page_token="ghi",
            ),
            firestore.PartitionQueryResponse(
                partitions=[
                    query.Cursor(),
                    query.Cursor(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.partition_query(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_partition_query_async_pager():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.partition_query), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            firestore.PartitionQueryResponse(
                partitions=[
                    query.Cursor(),
                    query.Cursor(),
                    query.Cursor(),
                ],
                next_page_token="abc",
            ),
            firestore.PartitionQueryResponse(
                partitions=[],
                next_page_token="def",
            ),
            firestore.PartitionQueryResponse(
                partitions=[
                    query.Cursor(),
                ],
                next_page_token="ghi",
            ),
            firestore.PartitionQueryResponse(
                partitions=[
                    query.Cursor(),
                    query.Cursor(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.partition_query(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, query.Cursor) for i in responses)


@pytest.mark.asyncio
async def test_partition_query_async_pages():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.partition_query), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            firestore.PartitionQueryResponse(
                partitions=[
                    query.Cursor(),
                    query.Cursor(),
                    query.Cursor(),
                ],
                next_page_token="abc",
            ),
            firestore.PartitionQueryResponse(
                partitions=[],
                next_page_token="def",
            ),
            firestore.PartitionQueryResponse(
                partitions=[
                    query.Cursor(),
                ],
                next_page_token="ghi",
            ),
            firestore.PartitionQueryResponse(
                partitions=[
                    query.Cursor(),
                    query.Cursor(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (
            await client.partition_query(request={})
        ).pages:  # pragma: no branch
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.WriteRequest,
        dict,
    ],
)
def test_write(request_type, transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()
    requests = [request]

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.write), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = iter([firestore.WriteResponse()])
        response = client.write(iter(requests))

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert next(args[0]) == request

    # Establish that the response is the type that we expect.
    for message in response:
        assert isinstance(message, firestore.WriteResponse)


@pytest.mark.asyncio
async def test_write_async(
    transport: str = "grpc_asyncio", request_type=firestore.WriteRequest
):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()
    requests = [request]

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.write), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = mock.Mock(aio.StreamStreamCall, autospec=True)
        call.return_value.read = mock.AsyncMock(side_effect=[firestore.WriteResponse()])
        response = await client.write(iter(requests))

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert next(args[0]) == request

    # Establish that the response is the type that we expect.
    message = await response.read()
    assert isinstance(message, firestore.WriteResponse)


@pytest.mark.asyncio
async def test_write_async_from_dict():
    await test_write_async(request_type=dict)


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.ListenRequest,
        dict,
    ],
)
def test_listen(request_type, transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()
    requests = [request]

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.listen), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = iter([firestore.ListenResponse()])
        response = client.listen(iter(requests))

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert next(args[0]) == request

    # Establish that the response is the type that we expect.
    for message in response:
        assert isinstance(message, firestore.ListenResponse)


@pytest.mark.asyncio
async def test_listen_async(
    transport: str = "grpc_asyncio", request_type=firestore.ListenRequest
):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()
    requests = [request]

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.listen), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = mock.Mock(aio.StreamStreamCall, autospec=True)
        call.return_value.read = mock.AsyncMock(
            side_effect=[firestore.ListenResponse()]
        )
        response = await client.listen(iter(requests))

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert next(args[0]) == request

    # Establish that the response is the type that we expect.
    message = await response.read()
    assert isinstance(message, firestore.ListenResponse)


@pytest.mark.asyncio
async def test_listen_async_from_dict():
    await test_listen_async(request_type=dict)


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.ListCollectionIdsRequest,
        dict,
    ],
)
def test_list_collection_ids(request_type, transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_collection_ids), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.ListCollectionIdsResponse(
            collection_ids=["collection_ids_value"],
            next_page_token="next_page_token_value",
        )
        response = client.list_collection_ids(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.ListCollectionIdsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListCollectionIdsPager)
    assert response.collection_ids == ["collection_ids_value"]
    assert response.next_page_token == "next_page_token_value"


def test_list_collection_ids_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_collection_ids), "__call__"
    ) as call:
        client.list_collection_ids()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.ListCollectionIdsRequest()


@pytest.mark.asyncio
async def test_list_collection_ids_async(
    transport: str = "grpc_asyncio", request_type=firestore.ListCollectionIdsRequest
):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_collection_ids), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.ListCollectionIdsResponse(
                collection_ids=["collection_ids_value"],
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_collection_ids(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.ListCollectionIdsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListCollectionIdsAsyncPager)
    assert response.collection_ids == ["collection_ids_value"]
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_collection_ids_async_from_dict():
    await test_list_collection_ids_async(request_type=dict)


def test_list_collection_ids_field_headers():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.ListCollectionIdsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_collection_ids), "__call__"
    ) as call:
        call.return_value = firestore.ListCollectionIdsResponse()
        client.list_collection_ids(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_collection_ids_field_headers_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.ListCollectionIdsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_collection_ids), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.ListCollectionIdsResponse()
        )
        await client.list_collection_ids(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


def test_list_collection_ids_flattened():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_collection_ids), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.ListCollectionIdsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_collection_ids(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_collection_ids_flattened_error():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_collection_ids(
            firestore.ListCollectionIdsRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_collection_ids_flattened_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_collection_ids), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.ListCollectionIdsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.ListCollectionIdsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_collection_ids(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_list_collection_ids_flattened_error_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_collection_ids(
            firestore.ListCollectionIdsRequest(),
            parent="parent_value",
        )


def test_list_collection_ids_pager(transport_name: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials,
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_collection_ids), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            firestore.ListCollectionIdsResponse(
                collection_ids=[
                    str(),
                    str(),
                    str(),
                ],
                next_page_token="abc",
            ),
            firestore.ListCollectionIdsResponse(
                collection_ids=[],
                next_page_token="def",
            ),
            firestore.ListCollectionIdsResponse(
                collection_ids=[
                    str(),
                ],
                next_page_token="ghi",
            ),
            firestore.ListCollectionIdsResponse(
                collection_ids=[
                    str(),
                    str(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_collection_ids(request={})

        assert pager._metadata == metadata

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, str) for i in results)


def test_list_collection_ids_pages(transport_name: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials,
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_collection_ids), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            firestore.ListCollectionIdsResponse(
                collection_ids=[
                    str(),
                    str(),
                    str(),
                ],
                next_page_token="abc",
            ),
            firestore.ListCollectionIdsResponse(
                collection_ids=[],
                next_page_token="def",
            ),
            firestore.ListCollectionIdsResponse(
                collection_ids=[
                    str(),
                ],
                next_page_token="ghi",
            ),
            firestore.ListCollectionIdsResponse(
                collection_ids=[
                    str(),
                    str(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_collection_ids(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_collection_ids_async_pager():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_collection_ids),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            firestore.ListCollectionIdsResponse(
                collection_ids=[
                    str(),
                    str(),
                    str(),
                ],
                next_page_token="abc",
            ),
            firestore.ListCollectionIdsResponse(
                collection_ids=[],
                next_page_token="def",
            ),
            firestore.ListCollectionIdsResponse(
                collection_ids=[
                    str(),
                ],
                next_page_token="ghi",
            ),
            firestore.ListCollectionIdsResponse(
                collection_ids=[
                    str(),
                    str(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_collection_ids(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, str) for i in responses)


@pytest.mark.asyncio
async def test_list_collection_ids_async_pages():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_collection_ids),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            firestore.ListCollectionIdsResponse(
                collection_ids=[
                    str(),
                    str(),
                    str(),
                ],
                next_page_token="abc",
            ),
            firestore.ListCollectionIdsResponse(
                collection_ids=[],
                next_page_token="def",
            ),
            firestore.ListCollectionIdsResponse(
                collection_ids=[
                    str(),
                ],
                next_page_token="ghi",
            ),
            firestore.ListCollectionIdsResponse(
                collection_ids=[
                    str(),
                    str(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (
            await client.list_collection_ids(request={})
        ).pages:  # pragma: no branch
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.BatchWriteRequest,
        dict,
    ],
)
def test_batch_write(request_type, transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.batch_write), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = firestore.BatchWriteResponse()
        response = client.batch_write(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.BatchWriteRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, firestore.BatchWriteResponse)


def test_batch_write_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.batch_write), "__call__") as call:
        client.batch_write()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.BatchWriteRequest()


@pytest.mark.asyncio
async def test_batch_write_async(
    transport: str = "grpc_asyncio", request_type=firestore.BatchWriteRequest
):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.batch_write), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.BatchWriteResponse()
        )
        response = await client.batch_write(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.BatchWriteRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, firestore.BatchWriteResponse)


@pytest.mark.asyncio
async def test_batch_write_async_from_dict():
    await test_batch_write_async(request_type=dict)


def test_batch_write_field_headers():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.BatchWriteRequest()

    request.database = "database_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.batch_write), "__call__") as call:
        call.return_value = firestore.BatchWriteResponse()
        client.batch_write(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "database=database_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_batch_write_field_headers_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.BatchWriteRequest()

    request.database = "database_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.batch_write), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            firestore.BatchWriteResponse()
        )
        await client.batch_write(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "database=database_value",
    ) in kw["metadata"]


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.CreateDocumentRequest,
        dict,
    ],
)
def test_create_document(request_type, transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_document), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = document.Document(
            name="name_value",
        )
        response = client.create_document(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.CreateDocumentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, document.Document)
    assert response.name == "name_value"


def test_create_document_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_document), "__call__") as call:
        client.create_document()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.CreateDocumentRequest()


@pytest.mark.asyncio
async def test_create_document_async(
    transport: str = "grpc_asyncio", request_type=firestore.CreateDocumentRequest
):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_document), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            document.Document(
                name="name_value",
            )
        )
        response = await client.create_document(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == firestore.CreateDocumentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, document.Document)
    assert response.name == "name_value"


@pytest.mark.asyncio
async def test_create_document_async_from_dict():
    await test_create_document_async(request_type=dict)


def test_create_document_field_headers():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.CreateDocumentRequest()

    request.parent = "parent_value"
    request.collection_id = "collection_id_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_document), "__call__") as call:
        call.return_value = document.Document()
        client.create_document(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value&collection_id=collection_id_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_document_field_headers_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = firestore.CreateDocumentRequest()

    request.parent = "parent_value"
    request.collection_id = "collection_id_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_document), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(document.Document())
        await client.create_document(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value&collection_id=collection_id_value",
    ) in kw["metadata"]


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.GetDocumentRequest,
        dict,
    ],
)
def test_get_document_rest(request_type):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/databases/sample2/documents/sample3/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = document.Document(
            name="name_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        pb_return_value = document.Document.pb(return_value)
        json_return_value = json_format.MessageToJson(pb_return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.get_document(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, document.Document)
    assert response.name == "name_value"


def test_get_document_rest_required_fields(request_type=firestore.GetDocumentRequest):
    transport_class = transports.FirestoreRestTransport

    request_init = {}
    request_init["name"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_document._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_document._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        (
            "mask",
            "read_time",
            "transaction",
        )
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = document.Document()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "get",
                "query_params": pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            pb_return_value = document.Document.pb(return_value)
            json_return_value = json_format.MessageToJson(pb_return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.get_document(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_document_rest_unset_required_fields():
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_document._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(
            (
                "mask",
                "readTime",
                "transaction",
            )
        )
        & set(("name",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_document_rest_interceptors(null_interceptor):
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.FirestoreRestInterceptor(),
    )
    client = FirestoreClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FirestoreRestInterceptor, "post_get_document"
    ) as post, mock.patch.object(
        transports.FirestoreRestInterceptor, "pre_get_document"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = firestore.GetDocumentRequest.pb(firestore.GetDocumentRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = document.Document.to_json(document.Document())

        request = firestore.GetDocumentRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = document.Document()

        client.get_document(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_get_document_rest_bad_request(
    transport: str = "rest", request_type=firestore.GetDocumentRequest
):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/databases/sample2/documents/sample3/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get_document(request)


def test_get_document_rest_error():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.ListDocumentsRequest,
        dict,
    ],
)
def test_list_documents_rest(request_type):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/databases/sample2/documents/sample3/sample4",
        "collection_id": "sample5",
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = firestore.ListDocumentsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        pb_return_value = firestore.ListDocumentsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(pb_return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.list_documents(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDocumentsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_documents_rest_required_fields(
    request_type=firestore.ListDocumentsRequest,
):
    transport_class = transports.FirestoreRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_documents._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_documents._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        (
            "mask",
            "order_by",
            "page_size",
            "page_token",
            "read_time",
            "show_missing",
            "transaction",
        )
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = firestore.ListDocumentsResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "get",
                "query_params": pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            pb_return_value = firestore.ListDocumentsResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(pb_return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.list_documents(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_documents_rest_unset_required_fields():
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_documents._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(
            (
                "mask",
                "orderBy",
                "pageSize",
                "pageToken",
                "readTime",
                "showMissing",
                "transaction",
            )
        )
        & set(("parent",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_documents_rest_interceptors(null_interceptor):
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.FirestoreRestInterceptor(),
    )
    client = FirestoreClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FirestoreRestInterceptor, "post_list_documents"
    ) as post, mock.patch.object(
        transports.FirestoreRestInterceptor, "pre_list_documents"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = firestore.ListDocumentsRequest.pb(firestore.ListDocumentsRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = firestore.ListDocumentsResponse.to_json(
            firestore.ListDocumentsResponse()
        )

        request = firestore.ListDocumentsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = firestore.ListDocumentsResponse()

        client.list_documents(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_list_documents_rest_bad_request(
    transport: str = "rest", request_type=firestore.ListDocumentsRequest
):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/databases/sample2/documents/sample3/sample4",
        "collection_id": "sample5",
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.list_documents(request)


def test_list_documents_rest_pager(transport: str = "rest"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                    document.Document(),
                    document.Document(),
                ],
                next_page_token="abc",
            ),
            firestore.ListDocumentsResponse(
                documents=[],
                next_page_token="def",
            ),
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                ],
                next_page_token="ghi",
            ),
            firestore.ListDocumentsResponse(
                documents=[
                    document.Document(),
                    document.Document(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(firestore.ListDocumentsResponse.to_json(x) for x in response)
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {
            "parent": "projects/sample1/databases/sample2/documents/sample3/sample4",
            "collection_id": "sample5",
        }

        pager = client.list_documents(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, document.Document) for i in results)

        pages = list(client.list_documents(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.UpdateDocumentRequest,
        dict,
    ],
)
def test_update_document_rest(request_type):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "document": {
            "name": "projects/sample1/databases/sample2/documents/sample3/sample4"
        }
    }
    request_init["document"] = {
        "name": "projects/sample1/databases/sample2/documents/sample3/sample4",
        "fields": {},
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gf_document.Document(
            name="name_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        pb_return_value = gf_document.Document.pb(return_value)
        json_return_value = json_format.MessageToJson(pb_return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.update_document(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, gf_document.Document)
    assert response.name == "name_value"


def test_update_document_rest_required_fields(
    request_type=firestore.UpdateDocumentRequest,
):
    transport_class = transports.FirestoreRestTransport

    request_init = {}
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_document._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_document._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        (
            "current_document",
            "mask",
            "update_mask",
        )
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone

    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = gf_document.Document()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "patch",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            pb_return_value = gf_document.Document.pb(return_value)
            json_return_value = json_format.MessageToJson(pb_return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.update_document(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_update_document_rest_unset_required_fields():
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.update_document._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(
            (
                "currentDocument",
                "mask",
                "updateMask",
            )
        )
        & set(("document",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_update_document_rest_interceptors(null_interceptor):
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.FirestoreRestInterceptor(),
    )
    client = FirestoreClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FirestoreRestInterceptor, "post_update_document"
    ) as post, mock.patch.object(
        transports.FirestoreRestInterceptor, "pre_update_document"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = firestore.UpdateDocumentRequest.pb(
            firestore.UpdateDocumentRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = gf_document.Document.to_json(gf_document.Document())

        request = firestore.UpdateDocumentRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = gf_document.Document()

        client.update_document(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_update_document_rest_bad_request(
    transport: str = "rest", request_type=firestore.UpdateDocumentRequest
):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "document": {
            "name": "projects/sample1/databases/sample2/documents/sample3/sample4"
        }
    }
    request_init["document"] = {
        "name": "projects/sample1/databases/sample2/documents/sample3/sample4",
        "fields": {},
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.update_document(request)


def test_update_document_rest_flattened():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gf_document.Document()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "document": {
                "name": "projects/sample1/databases/sample2/documents/sample3/sample4"
            }
        }

        # get truthy value for each flattened field
        mock_args = dict(
            document=gf_document.Document(name="name_value"),
            update_mask=common.DocumentMask(field_paths=["field_paths_value"]),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        pb_return_value = gf_document.Document.pb(return_value)
        json_return_value = json_format.MessageToJson(pb_return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.update_document(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{document.name=projects/*/databases/*/documents/*/**}"
            % client.transport._host,
            args[1],
        )


def test_update_document_rest_flattened_error(transport: str = "rest"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_document(
            firestore.UpdateDocumentRequest(),
            document=gf_document.Document(name="name_value"),
            update_mask=common.DocumentMask(field_paths=["field_paths_value"]),
        )


def test_update_document_rest_error():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.DeleteDocumentRequest,
        dict,
    ],
)
def test_delete_document_rest(request_type):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/databases/sample2/documents/sample3/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = ""

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.delete_document(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_document_rest_required_fields(
    request_type=firestore.DeleteDocumentRequest,
):
    transport_class = transports.FirestoreRestTransport

    request_init = {}
    request_init["name"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_document._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_document._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("current_document",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = None
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "delete",
                "query_params": pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = ""

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.delete_document(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_delete_document_rest_unset_required_fields():
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.delete_document._get_unset_required_fields({})
    assert set(unset_fields) == (set(("currentDocument",)) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_document_rest_interceptors(null_interceptor):
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.FirestoreRestInterceptor(),
    )
    client = FirestoreClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FirestoreRestInterceptor, "pre_delete_document"
    ) as pre:
        pre.assert_not_called()
        pb_message = firestore.DeleteDocumentRequest.pb(
            firestore.DeleteDocumentRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()

        request = firestore.DeleteDocumentRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata

        client.delete_document(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()


def test_delete_document_rest_bad_request(
    transport: str = "rest", request_type=firestore.DeleteDocumentRequest
):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/databases/sample2/documents/sample3/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.delete_document(request)


def test_delete_document_rest_flattened():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/databases/sample2/documents/sample3/sample4"
        }

        # get truthy value for each flattened field
        mock_args = dict(
            name="name_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = ""
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.delete_document(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/databases/*/documents/*/**}"
            % client.transport._host,
            args[1],
        )


def test_delete_document_rest_flattened_error(transport: str = "rest"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_document(
            firestore.DeleteDocumentRequest(),
            name="name_value",
        )


def test_delete_document_rest_error():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.BatchGetDocumentsRequest,
        dict,
    ],
)
def test_batch_get_documents_rest(request_type):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"database": "projects/sample1/databases/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = firestore.BatchGetDocumentsResponse(
            transaction=b"transaction_blob",
            found=document.Document(name="name_value"),
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        pb_return_value = firestore.BatchGetDocumentsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(pb_return_value)

        json_return_value = "[{}]".format(json_return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        with mock.patch.object(response_value, "iter_content") as iter_content:
            iter_content.return_value = iter(json_return_value)
            response = client.batch_get_documents(request)

    assert isinstance(response, Iterable)
    response = next(response)

    # Establish that the response is the type that we expect.
    assert isinstance(response, firestore.BatchGetDocumentsResponse)
    assert response.transaction == b"transaction_blob"


def test_batch_get_documents_rest_required_fields(
    request_type=firestore.BatchGetDocumentsRequest,
):
    transport_class = transports.FirestoreRestTransport

    request_init = {}
    request_init["database"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).batch_get_documents._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["database"] = "database_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).batch_get_documents._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "database" in jsonified_request
    assert jsonified_request["database"] == "database_value"

    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = firestore.BatchGetDocumentsResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            pb_return_value = firestore.BatchGetDocumentsResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(pb_return_value)
            json_return_value = "[{}]".format(json_return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            with mock.patch.object(response_value, "iter_content") as iter_content:
                iter_content.return_value = iter(json_return_value)
                response = client.batch_get_documents(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_batch_get_documents_rest_unset_required_fields():
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.batch_get_documents._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("database",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_batch_get_documents_rest_interceptors(null_interceptor):
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.FirestoreRestInterceptor(),
    )
    client = FirestoreClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FirestoreRestInterceptor, "post_batch_get_documents"
    ) as post, mock.patch.object(
        transports.FirestoreRestInterceptor, "pre_batch_get_documents"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = firestore.BatchGetDocumentsRequest.pb(
            firestore.BatchGetDocumentsRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = firestore.BatchGetDocumentsResponse.to_json(
            firestore.BatchGetDocumentsResponse()
        )
        req.return_value._content = "[{}]".format(req.return_value._content)

        request = firestore.BatchGetDocumentsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = firestore.BatchGetDocumentsResponse()

        client.batch_get_documents(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_batch_get_documents_rest_bad_request(
    transport: str = "rest", request_type=firestore.BatchGetDocumentsRequest
):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"database": "projects/sample1/databases/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.batch_get_documents(request)


def test_batch_get_documents_rest_error():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.BeginTransactionRequest,
        dict,
    ],
)
def test_begin_transaction_rest(request_type):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"database": "projects/sample1/databases/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = firestore.BeginTransactionResponse(
            transaction=b"transaction_blob",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        pb_return_value = firestore.BeginTransactionResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(pb_return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.begin_transaction(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, firestore.BeginTransactionResponse)
    assert response.transaction == b"transaction_blob"


def test_begin_transaction_rest_required_fields(
    request_type=firestore.BeginTransactionRequest,
):
    transport_class = transports.FirestoreRestTransport

    request_init = {}
    request_init["database"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).begin_transaction._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["database"] = "database_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).begin_transaction._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "database" in jsonified_request
    assert jsonified_request["database"] == "database_value"

    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = firestore.BeginTransactionResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            pb_return_value = firestore.BeginTransactionResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(pb_return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.begin_transaction(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_begin_transaction_rest_unset_required_fields():
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.begin_transaction._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("database",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_begin_transaction_rest_interceptors(null_interceptor):
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.FirestoreRestInterceptor(),
    )
    client = FirestoreClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FirestoreRestInterceptor, "post_begin_transaction"
    ) as post, mock.patch.object(
        transports.FirestoreRestInterceptor, "pre_begin_transaction"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = firestore.BeginTransactionRequest.pb(
            firestore.BeginTransactionRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = firestore.BeginTransactionResponse.to_json(
            firestore.BeginTransactionResponse()
        )

        request = firestore.BeginTransactionRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = firestore.BeginTransactionResponse()

        client.begin_transaction(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_begin_transaction_rest_bad_request(
    transport: str = "rest", request_type=firestore.BeginTransactionRequest
):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"database": "projects/sample1/databases/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.begin_transaction(request)


def test_begin_transaction_rest_flattened():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = firestore.BeginTransactionResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {"database": "projects/sample1/databases/sample2"}

        # get truthy value for each flattened field
        mock_args = dict(
            database="database_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        pb_return_value = firestore.BeginTransactionResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(pb_return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.begin_transaction(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{database=projects/*/databases/*}/documents:beginTransaction"
            % client.transport._host,
            args[1],
        )


def test_begin_transaction_rest_flattened_error(transport: str = "rest"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.begin_transaction(
            firestore.BeginTransactionRequest(),
            database="database_value",
        )


def test_begin_transaction_rest_error():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.CommitRequest,
        dict,
    ],
)
def test_commit_rest(request_type):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"database": "projects/sample1/databases/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = firestore.CommitResponse()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        pb_return_value = firestore.CommitResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(pb_return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.commit(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, firestore.CommitResponse)


def test_commit_rest_required_fields(request_type=firestore.CommitRequest):
    transport_class = transports.FirestoreRestTransport

    request_init = {}
    request_init["database"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).commit._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["database"] = "database_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).commit._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "database" in jsonified_request
    assert jsonified_request["database"] == "database_value"

    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = firestore.CommitResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            pb_return_value = firestore.CommitResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(pb_return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.commit(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_commit_rest_unset_required_fields():
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.commit._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("database",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_commit_rest_interceptors(null_interceptor):
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.FirestoreRestInterceptor(),
    )
    client = FirestoreClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FirestoreRestInterceptor, "post_commit"
    ) as post, mock.patch.object(
        transports.FirestoreRestInterceptor, "pre_commit"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = firestore.CommitRequest.pb(firestore.CommitRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = firestore.CommitResponse.to_json(
            firestore.CommitResponse()
        )

        request = firestore.CommitRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = firestore.CommitResponse()

        client.commit(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_commit_rest_bad_request(
    transport: str = "rest", request_type=firestore.CommitRequest
):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"database": "projects/sample1/databases/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.commit(request)


def test_commit_rest_flattened():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = firestore.CommitResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {"database": "projects/sample1/databases/sample2"}

        # get truthy value for each flattened field
        mock_args = dict(
            database="database_value",
            writes=[gf_write.Write(update=document.Document(name="name_value"))],
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        pb_return_value = firestore.CommitResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(pb_return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.commit(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{database=projects/*/databases/*}/documents:commit"
            % client.transport._host,
            args[1],
        )


def test_commit_rest_flattened_error(transport: str = "rest"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.commit(
            firestore.CommitRequest(),
            database="database_value",
            writes=[gf_write.Write(update=document.Document(name="name_value"))],
        )


def test_commit_rest_error():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.RollbackRequest,
        dict,
    ],
)
def test_rollback_rest(request_type):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"database": "projects/sample1/databases/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = ""

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.rollback(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_rollback_rest_required_fields(request_type=firestore.RollbackRequest):
    transport_class = transports.FirestoreRestTransport

    request_init = {}
    request_init["database"] = ""
    request_init["transaction"] = b""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).rollback._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["database"] = "database_value"
    jsonified_request["transaction"] = b"transaction_blob"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).rollback._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "database" in jsonified_request
    assert jsonified_request["database"] == "database_value"
    assert "transaction" in jsonified_request
    assert jsonified_request["transaction"] == b"transaction_blob"

    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = None
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = ""

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.rollback(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_rollback_rest_unset_required_fields():
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.rollback._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(())
        & set(
            (
                "database",
                "transaction",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_rollback_rest_interceptors(null_interceptor):
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.FirestoreRestInterceptor(),
    )
    client = FirestoreClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FirestoreRestInterceptor, "pre_rollback"
    ) as pre:
        pre.assert_not_called()
        pb_message = firestore.RollbackRequest.pb(firestore.RollbackRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()

        request = firestore.RollbackRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata

        client.rollback(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()


def test_rollback_rest_bad_request(
    transport: str = "rest", request_type=firestore.RollbackRequest
):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"database": "projects/sample1/databases/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.rollback(request)


def test_rollback_rest_flattened():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # get arguments that satisfy an http rule for this method
        sample_request = {"database": "projects/sample1/databases/sample2"}

        # get truthy value for each flattened field
        mock_args = dict(
            database="database_value",
            transaction=b"transaction_blob",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = ""
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.rollback(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{database=projects/*/databases/*}/documents:rollback"
            % client.transport._host,
            args[1],
        )


def test_rollback_rest_flattened_error(transport: str = "rest"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.rollback(
            firestore.RollbackRequest(),
            database="database_value",
            transaction=b"transaction_blob",
        )


def test_rollback_rest_error():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.RunQueryRequest,
        dict,
    ],
)
def test_run_query_rest(request_type):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/databases/sample2/documents"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = firestore.RunQueryResponse(
            transaction=b"transaction_blob",
            skipped_results=1633,
            done=True,
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        pb_return_value = firestore.RunQueryResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(pb_return_value)

        json_return_value = "[{}]".format(json_return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        with mock.patch.object(response_value, "iter_content") as iter_content:
            iter_content.return_value = iter(json_return_value)
            response = client.run_query(request)

    assert isinstance(response, Iterable)
    response = next(response)

    # Establish that the response is the type that we expect.
    assert isinstance(response, firestore.RunQueryResponse)
    assert response.transaction == b"transaction_blob"
    assert response.skipped_results == 1633


def test_run_query_rest_required_fields(request_type=firestore.RunQueryRequest):
    transport_class = transports.FirestoreRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).run_query._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).run_query._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = firestore.RunQueryResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            pb_return_value = firestore.RunQueryResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(pb_return_value)
            json_return_value = "[{}]".format(json_return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            with mock.patch.object(response_value, "iter_content") as iter_content:
                iter_content.return_value = iter(json_return_value)
                response = client.run_query(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_run_query_rest_unset_required_fields():
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.run_query._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("parent",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_run_query_rest_interceptors(null_interceptor):
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.FirestoreRestInterceptor(),
    )
    client = FirestoreClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FirestoreRestInterceptor, "post_run_query"
    ) as post, mock.patch.object(
        transports.FirestoreRestInterceptor, "pre_run_query"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = firestore.RunQueryRequest.pb(firestore.RunQueryRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = firestore.RunQueryResponse.to_json(
            firestore.RunQueryResponse()
        )
        req.return_value._content = "[{}]".format(req.return_value._content)

        request = firestore.RunQueryRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = firestore.RunQueryResponse()

        client.run_query(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_run_query_rest_bad_request(
    transport: str = "rest", request_type=firestore.RunQueryRequest
):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/databases/sample2/documents"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.run_query(request)


def test_run_query_rest_error():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.RunAggregationQueryRequest,
        dict,
    ],
)
def test_run_aggregation_query_rest(request_type):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/databases/sample2/documents"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = firestore.RunAggregationQueryResponse(
            transaction=b"transaction_blob",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        pb_return_value = firestore.RunAggregationQueryResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(pb_return_value)

        json_return_value = "[{}]".format(json_return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        with mock.patch.object(response_value, "iter_content") as iter_content:
            iter_content.return_value = iter(json_return_value)
            response = client.run_aggregation_query(request)

    assert isinstance(response, Iterable)
    response = next(response)

    # Establish that the response is the type that we expect.
    assert isinstance(response, firestore.RunAggregationQueryResponse)
    assert response.transaction == b"transaction_blob"


def test_run_aggregation_query_rest_required_fields(
    request_type=firestore.RunAggregationQueryRequest,
):
    transport_class = transports.FirestoreRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).run_aggregation_query._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).run_aggregation_query._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = firestore.RunAggregationQueryResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            pb_return_value = firestore.RunAggregationQueryResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(pb_return_value)
            json_return_value = "[{}]".format(json_return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            with mock.patch.object(response_value, "iter_content") as iter_content:
                iter_content.return_value = iter(json_return_value)
                response = client.run_aggregation_query(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_run_aggregation_query_rest_unset_required_fields():
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.run_aggregation_query._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("parent",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_run_aggregation_query_rest_interceptors(null_interceptor):
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.FirestoreRestInterceptor(),
    )
    client = FirestoreClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FirestoreRestInterceptor, "post_run_aggregation_query"
    ) as post, mock.patch.object(
        transports.FirestoreRestInterceptor, "pre_run_aggregation_query"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = firestore.RunAggregationQueryRequest.pb(
            firestore.RunAggregationQueryRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = firestore.RunAggregationQueryResponse.to_json(
            firestore.RunAggregationQueryResponse()
        )
        req.return_value._content = "[{}]".format(req.return_value._content)

        request = firestore.RunAggregationQueryRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = firestore.RunAggregationQueryResponse()

        client.run_aggregation_query(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_run_aggregation_query_rest_bad_request(
    transport: str = "rest", request_type=firestore.RunAggregationQueryRequest
):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/databases/sample2/documents"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.run_aggregation_query(request)


def test_run_aggregation_query_rest_error():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.PartitionQueryRequest,
        dict,
    ],
)
def test_partition_query_rest(request_type):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/databases/sample2/documents"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = firestore.PartitionQueryResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        pb_return_value = firestore.PartitionQueryResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(pb_return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.partition_query(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.PartitionQueryPager)
    assert response.next_page_token == "next_page_token_value"


def test_partition_query_rest_required_fields(
    request_type=firestore.PartitionQueryRequest,
):
    transport_class = transports.FirestoreRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).partition_query._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).partition_query._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = firestore.PartitionQueryResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            pb_return_value = firestore.PartitionQueryResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(pb_return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.partition_query(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_partition_query_rest_unset_required_fields():
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.partition_query._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("parent",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_partition_query_rest_interceptors(null_interceptor):
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.FirestoreRestInterceptor(),
    )
    client = FirestoreClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FirestoreRestInterceptor, "post_partition_query"
    ) as post, mock.patch.object(
        transports.FirestoreRestInterceptor, "pre_partition_query"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = firestore.PartitionQueryRequest.pb(
            firestore.PartitionQueryRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = firestore.PartitionQueryResponse.to_json(
            firestore.PartitionQueryResponse()
        )

        request = firestore.PartitionQueryRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = firestore.PartitionQueryResponse()

        client.partition_query(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_partition_query_rest_bad_request(
    transport: str = "rest", request_type=firestore.PartitionQueryRequest
):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/databases/sample2/documents"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.partition_query(request)


def test_partition_query_rest_pager(transport: str = "rest"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            firestore.PartitionQueryResponse(
                partitions=[
                    query.Cursor(),
                    query.Cursor(),
                    query.Cursor(),
                ],
                next_page_token="abc",
            ),
            firestore.PartitionQueryResponse(
                partitions=[],
                next_page_token="def",
            ),
            firestore.PartitionQueryResponse(
                partitions=[
                    query.Cursor(),
                ],
                next_page_token="ghi",
            ),
            firestore.PartitionQueryResponse(
                partitions=[
                    query.Cursor(),
                    query.Cursor(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(firestore.PartitionQueryResponse.to_json(x) for x in response)
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {"parent": "projects/sample1/databases/sample2/documents"}

        pager = client.partition_query(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, query.Cursor) for i in results)

        pages = list(client.partition_query(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_write_rest_unimplemented():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = firestore.WriteRequest()
    requests = [request]
    with pytest.raises(NotImplementedError):
        client.write(requests)


def test_listen_rest_unimplemented():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = firestore.ListenRequest()
    requests = [request]
    with pytest.raises(NotImplementedError):
        client.listen(requests)


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.ListCollectionIdsRequest,
        dict,
    ],
)
def test_list_collection_ids_rest(request_type):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/databases/sample2/documents"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = firestore.ListCollectionIdsResponse(
            collection_ids=["collection_ids_value"],
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        pb_return_value = firestore.ListCollectionIdsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(pb_return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.list_collection_ids(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListCollectionIdsPager)
    assert response.collection_ids == ["collection_ids_value"]
    assert response.next_page_token == "next_page_token_value"


def test_list_collection_ids_rest_required_fields(
    request_type=firestore.ListCollectionIdsRequest,
):
    transport_class = transports.FirestoreRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_collection_ids._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_collection_ids._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = firestore.ListCollectionIdsResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            pb_return_value = firestore.ListCollectionIdsResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(pb_return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.list_collection_ids(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_collection_ids_rest_unset_required_fields():
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_collection_ids._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("parent",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_collection_ids_rest_interceptors(null_interceptor):
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.FirestoreRestInterceptor(),
    )
    client = FirestoreClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FirestoreRestInterceptor, "post_list_collection_ids"
    ) as post, mock.patch.object(
        transports.FirestoreRestInterceptor, "pre_list_collection_ids"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = firestore.ListCollectionIdsRequest.pb(
            firestore.ListCollectionIdsRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = firestore.ListCollectionIdsResponse.to_json(
            firestore.ListCollectionIdsResponse()
        )

        request = firestore.ListCollectionIdsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = firestore.ListCollectionIdsResponse()

        client.list_collection_ids(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_list_collection_ids_rest_bad_request(
    transport: str = "rest", request_type=firestore.ListCollectionIdsRequest
):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/databases/sample2/documents"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.list_collection_ids(request)


def test_list_collection_ids_rest_flattened():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = firestore.ListCollectionIdsResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {"parent": "projects/sample1/databases/sample2/documents"}

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        pb_return_value = firestore.ListCollectionIdsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(pb_return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.list_collection_ids(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{parent=projects/*/databases/*/documents}:listCollectionIds"
            % client.transport._host,
            args[1],
        )


def test_list_collection_ids_rest_flattened_error(transport: str = "rest"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_collection_ids(
            firestore.ListCollectionIdsRequest(),
            parent="parent_value",
        )


def test_list_collection_ids_rest_pager(transport: str = "rest"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            firestore.ListCollectionIdsResponse(
                collection_ids=[
                    str(),
                    str(),
                    str(),
                ],
                next_page_token="abc",
            ),
            firestore.ListCollectionIdsResponse(
                collection_ids=[],
                next_page_token="def",
            ),
            firestore.ListCollectionIdsResponse(
                collection_ids=[
                    str(),
                ],
                next_page_token="ghi",
            ),
            firestore.ListCollectionIdsResponse(
                collection_ids=[
                    str(),
                    str(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            firestore.ListCollectionIdsResponse.to_json(x) for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {"parent": "projects/sample1/databases/sample2/documents"}

        pager = client.list_collection_ids(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, str) for i in results)

        pages = list(client.list_collection_ids(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.BatchWriteRequest,
        dict,
    ],
)
def test_batch_write_rest(request_type):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"database": "projects/sample1/databases/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = firestore.BatchWriteResponse()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        pb_return_value = firestore.BatchWriteResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(pb_return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.batch_write(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, firestore.BatchWriteResponse)


def test_batch_write_rest_required_fields(request_type=firestore.BatchWriteRequest):
    transport_class = transports.FirestoreRestTransport

    request_init = {}
    request_init["database"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).batch_write._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["database"] = "database_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).batch_write._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "database" in jsonified_request
    assert jsonified_request["database"] == "database_value"

    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = firestore.BatchWriteResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            pb_return_value = firestore.BatchWriteResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(pb_return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.batch_write(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_batch_write_rest_unset_required_fields():
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.batch_write._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("database",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_batch_write_rest_interceptors(null_interceptor):
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.FirestoreRestInterceptor(),
    )
    client = FirestoreClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FirestoreRestInterceptor, "post_batch_write"
    ) as post, mock.patch.object(
        transports.FirestoreRestInterceptor, "pre_batch_write"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = firestore.BatchWriteRequest.pb(firestore.BatchWriteRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = firestore.BatchWriteResponse.to_json(
            firestore.BatchWriteResponse()
        )

        request = firestore.BatchWriteRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = firestore.BatchWriteResponse()

        client.batch_write(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_batch_write_rest_bad_request(
    transport: str = "rest", request_type=firestore.BatchWriteRequest
):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"database": "projects/sample1/databases/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.batch_write(request)


def test_batch_write_rest_error():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        firestore.CreateDocumentRequest,
        dict,
    ],
)
def test_create_document_rest(request_type):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/databases/sample2/documents/sample3",
        "collection_id": "sample4",
    }
    request_init["document"] = {
        "name": "name_value",
        "fields": {},
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = document.Document(
            name="name_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        pb_return_value = document.Document.pb(return_value)
        json_return_value = json_format.MessageToJson(pb_return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.create_document(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, document.Document)
    assert response.name == "name_value"


def test_create_document_rest_required_fields(
    request_type=firestore.CreateDocumentRequest,
):
    transport_class = transports.FirestoreRestTransport

    request_init = {}
    request_init["parent"] = ""
    request_init["collection_id"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).create_document._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"
    jsonified_request["collectionId"] = "collection_id_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).create_document._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        (
            "document_id",
            "mask",
        )
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"
    assert "collectionId" in jsonified_request
    assert jsonified_request["collectionId"] == "collection_id_value"

    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = document.Document()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            pb_return_value = document.Document.pb(return_value)
            json_return_value = json_format.MessageToJson(pb_return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.create_document(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_create_document_rest_unset_required_fields():
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.create_document._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(
            (
                "documentId",
                "mask",
            )
        )
        & set(
            (
                "parent",
                "collectionId",
                "document",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_create_document_rest_interceptors(null_interceptor):
    transport = transports.FirestoreRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.FirestoreRestInterceptor(),
    )
    client = FirestoreClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FirestoreRestInterceptor, "post_create_document"
    ) as post, mock.patch.object(
        transports.FirestoreRestInterceptor, "pre_create_document"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = firestore.CreateDocumentRequest.pb(
            firestore.CreateDocumentRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = document.Document.to_json(document.Document())

        request = firestore.CreateDocumentRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = document.Document()

        client.create_document(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_create_document_rest_bad_request(
    transport: str = "rest", request_type=firestore.CreateDocumentRequest
):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/databases/sample2/documents/sample3",
        "collection_id": "sample4",
    }
    request_init["document"] = {
        "name": "name_value",
        "fields": {},
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.create_document(request)


def test_create_document_rest_error():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.FirestoreGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = FirestoreClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.FirestoreGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = FirestoreClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide an api_key and a transport instance.
    transport = transports.FirestoreGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = FirestoreClient(
            client_options=options,
            transport=transport,
        )

    # It is an error to provide an api_key and a credential.
    options = mock.Mock()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = FirestoreClient(
            client_options=options, credentials=ga_credentials.AnonymousCredentials()
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.FirestoreGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = FirestoreClient(
            client_options={"scopes": ["1", "2"]},
            transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.FirestoreGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    client = FirestoreClient(transport=transport)
    assert client.transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.FirestoreGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.FirestoreGrpcAsyncIOTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.FirestoreGrpcTransport,
        transports.FirestoreGrpcAsyncIOTransport,
        transports.FirestoreRestTransport,
    ],
)
def test_transport_adc(transport_class):
    # Test default credentials are used if not provided.
    with mock.patch.object(google.auth, "default") as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport_class()
        adc.assert_called_once()


@pytest.mark.parametrize(
    "transport_name",
    [
        "grpc",
        "rest",
    ],
)
def test_transport_kind(transport_name):
    transport = FirestoreClient.get_transport_class(transport_name)(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    assert transport.kind == transport_name


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    assert isinstance(
        client.transport,
        transports.FirestoreGrpcTransport,
    )


def test_firestore_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(core_exceptions.DuplicateCredentialArgs):
        transport = transports.FirestoreTransport(
            credentials=ga_credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_firestore_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.firestore_v1.services.firestore.transports.FirestoreTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.FirestoreTransport(
            credentials=ga_credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "get_document",
        "list_documents",
        "update_document",
        "delete_document",
        "batch_get_documents",
        "begin_transaction",
        "commit",
        "rollback",
        "run_query",
        "run_aggregation_query",
        "partition_query",
        "write",
        "listen",
        "list_collection_ids",
        "batch_write",
        "create_document",
        "get_operation",
        "cancel_operation",
        "delete_operation",
        "list_operations",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    with pytest.raises(NotImplementedError):
        transport.close()

    # Catch all for all remaining methods and properties
    remainder = [
        "kind",
    ]
    for r in remainder:
        with pytest.raises(NotImplementedError):
            getattr(transport, r)()


def test_firestore_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch(
        "google.cloud.firestore_v1.services.firestore.transports.FirestoreTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.FirestoreTransport(
            credentials_file="credentials.json",
            quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=None,
            default_scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/datastore",
            ),
            quota_project_id="octopus",
        )


def test_firestore_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(google.auth, "default", autospec=True) as adc, mock.patch(
        "google.cloud.firestore_v1.services.firestore.transports.FirestoreTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.FirestoreTransport()
        adc.assert_called_once()


def test_firestore_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        FirestoreClient()
        adc.assert_called_once_with(
            scopes=None,
            default_scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/datastore",
            ),
            quota_project_id=None,
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.FirestoreGrpcTransport,
        transports.FirestoreGrpcAsyncIOTransport,
    ],
)
def test_firestore_transport_auth_adc(transport_class):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport_class(quota_project_id="octopus", scopes=["1", "2"])
        adc.assert_called_once_with(
            scopes=["1", "2"],
            default_scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/datastore",
            ),
            quota_project_id="octopus",
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.FirestoreGrpcTransport,
        transports.FirestoreGrpcAsyncIOTransport,
        transports.FirestoreRestTransport,
    ],
)
def test_firestore_transport_auth_gdch_credentials(transport_class):
    host = "https://language.com"
    api_audience_tests = [None, "https://language2.com"]
    api_audience_expect = [host, "https://language2.com"]
    for t, e in zip(api_audience_tests, api_audience_expect):
        with mock.patch.object(google.auth, "default", autospec=True) as adc:
            gdch_mock = mock.MagicMock()
            type(gdch_mock).with_gdch_audience = mock.PropertyMock(
                return_value=gdch_mock
            )
            adc.return_value = (gdch_mock, None)
            transport_class(host=host, api_audience=t)
            gdch_mock.with_gdch_audience.assert_called_once_with(e)


@pytest.mark.parametrize(
    "transport_class,grpc_helpers",
    [
        (transports.FirestoreGrpcTransport, grpc_helpers),
        (transports.FirestoreGrpcAsyncIOTransport, grpc_helpers_async),
    ],
)
def test_firestore_transport_create_channel(transport_class, grpc_helpers):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(
        google.auth, "default", autospec=True
    ) as adc, mock.patch.object(
        grpc_helpers, "create_channel", autospec=True
    ) as create_channel:
        creds = ga_credentials.AnonymousCredentials()
        adc.return_value = (creds, None)
        transport_class(quota_project_id="octopus", scopes=["1", "2"])

        create_channel.assert_called_with(
            "firestore.googleapis.com:443",
            credentials=creds,
            credentials_file=None,
            quota_project_id="octopus",
            default_scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/datastore",
            ),
            scopes=["1", "2"],
            default_host="firestore.googleapis.com",
            ssl_credentials=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )


@pytest.mark.parametrize(
    "transport_class",
    [transports.FirestoreGrpcTransport, transports.FirestoreGrpcAsyncIOTransport],
)
def test_firestore_grpc_transport_client_cert_source_for_mtls(transport_class):
    cred = ga_credentials.AnonymousCredentials()

    # Check ssl_channel_credentials is used if provided.
    with mock.patch.object(transport_class, "create_channel") as mock_create_channel:
        mock_ssl_channel_creds = mock.Mock()
        transport_class(
            host="squid.clam.whelk",
            credentials=cred,
            ssl_channel_credentials=mock_ssl_channel_creds,
        )
        mock_create_channel.assert_called_once_with(
            "squid.clam.whelk:443",
            credentials=cred,
            credentials_file=None,
            scopes=None,
            ssl_credentials=mock_ssl_channel_creds,
            quota_project_id=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )

    # Check if ssl_channel_credentials is not provided, then client_cert_source_for_mtls
    # is used.
    with mock.patch.object(transport_class, "create_channel", return_value=mock.Mock()):
        with mock.patch("grpc.ssl_channel_credentials") as mock_ssl_cred:
            transport_class(
                credentials=cred,
                client_cert_source_for_mtls=client_cert_source_callback,
            )
            expected_cert, expected_key = client_cert_source_callback()
            mock_ssl_cred.assert_called_once_with(
                certificate_chain=expected_cert, private_key=expected_key
            )


def test_firestore_http_transport_client_cert_source_for_mtls():
    cred = ga_credentials.AnonymousCredentials()
    with mock.patch(
        "google.auth.transport.requests.AuthorizedSession.configure_mtls_channel"
    ) as mock_configure_mtls_channel:
        transports.FirestoreRestTransport(
            credentials=cred, client_cert_source_for_mtls=client_cert_source_callback
        )
        mock_configure_mtls_channel.assert_called_once_with(client_cert_source_callback)


@pytest.mark.parametrize(
    "transport_name",
    [
        "grpc",
        "grpc_asyncio",
        "rest",
    ],
)
def test_firestore_host_no_port(transport_name):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="firestore.googleapis.com"
        ),
        transport=transport_name,
    )
    assert client.transport._host == (
        "firestore.googleapis.com:443"
        if transport_name in ["grpc", "grpc_asyncio"]
        else "https://firestore.googleapis.com"
    )


@pytest.mark.parametrize(
    "transport_name",
    [
        "grpc",
        "grpc_asyncio",
        "rest",
    ],
)
def test_firestore_host_with_port(transport_name):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="firestore.googleapis.com:8000"
        ),
        transport=transport_name,
    )
    assert client.transport._host == (
        "firestore.googleapis.com:8000"
        if transport_name in ["grpc", "grpc_asyncio"]
        else "https://firestore.googleapis.com:8000"
    )


@pytest.mark.parametrize(
    "transport_name",
    [
        "rest",
    ],
)
def test_firestore_client_transport_session_collision(transport_name):
    creds1 = ga_credentials.AnonymousCredentials()
    creds2 = ga_credentials.AnonymousCredentials()
    client1 = FirestoreClient(
        credentials=creds1,
        transport=transport_name,
    )
    client2 = FirestoreClient(
        credentials=creds2,
        transport=transport_name,
    )
    session1 = client1.transport.get_document._session
    session2 = client2.transport.get_document._session
    assert session1 != session2
    session1 = client1.transport.list_documents._session
    session2 = client2.transport.list_documents._session
    assert session1 != session2
    session1 = client1.transport.update_document._session
    session2 = client2.transport.update_document._session
    assert session1 != session2
    session1 = client1.transport.delete_document._session
    session2 = client2.transport.delete_document._session
    assert session1 != session2
    session1 = client1.transport.batch_get_documents._session
    session2 = client2.transport.batch_get_documents._session
    assert session1 != session2
    session1 = client1.transport.begin_transaction._session
    session2 = client2.transport.begin_transaction._session
    assert session1 != session2
    session1 = client1.transport.commit._session
    session2 = client2.transport.commit._session
    assert session1 != session2
    session1 = client1.transport.rollback._session
    session2 = client2.transport.rollback._session
    assert session1 != session2
    session1 = client1.transport.run_query._session
    session2 = client2.transport.run_query._session
    assert session1 != session2
    session1 = client1.transport.run_aggregation_query._session
    session2 = client2.transport.run_aggregation_query._session
    assert session1 != session2
    session1 = client1.transport.partition_query._session
    session2 = client2.transport.partition_query._session
    assert session1 != session2
    session1 = client1.transport.write._session
    session2 = client2.transport.write._session
    assert session1 != session2
    session1 = client1.transport.listen._session
    session2 = client2.transport.listen._session
    assert session1 != session2
    session1 = client1.transport.list_collection_ids._session
    session2 = client2.transport.list_collection_ids._session
    assert session1 != session2
    session1 = client1.transport.batch_write._session
    session2 = client2.transport.batch_write._session
    assert session1 != session2
    session1 = client1.transport.create_document._session
    session2 = client2.transport.create_document._session
    assert session1 != session2


def test_firestore_grpc_transport_channel():
    channel = grpc.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.FirestoreGrpcTransport(
        host="squid.clam.whelk",
        channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_firestore_grpc_asyncio_transport_channel():
    channel = aio.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.FirestoreGrpcAsyncIOTransport(
        host="squid.clam.whelk",
        channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


# Remove this test when deprecated arguments (api_mtls_endpoint, client_cert_source) are
# removed from grpc/grpc_asyncio transport constructor.
@pytest.mark.parametrize(
    "transport_class",
    [transports.FirestoreGrpcTransport, transports.FirestoreGrpcAsyncIOTransport],
)
def test_firestore_transport_channel_mtls_with_client_cert_source(transport_class):
    with mock.patch(
        "grpc.ssl_channel_credentials", autospec=True
    ) as grpc_ssl_channel_cred:
        with mock.patch.object(
            transport_class, "create_channel"
        ) as grpc_create_channel:
            mock_ssl_cred = mock.Mock()
            grpc_ssl_channel_cred.return_value = mock_ssl_cred

            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel

            cred = ga_credentials.AnonymousCredentials()
            with pytest.warns(DeprecationWarning):
                with mock.patch.object(google.auth, "default") as adc:
                    adc.return_value = (cred, None)
                    transport = transport_class(
                        host="squid.clam.whelk",
                        api_mtls_endpoint="mtls.squid.clam.whelk",
                        client_cert_source=client_cert_source_callback,
                    )
                    adc.assert_called_once()

            grpc_ssl_channel_cred.assert_called_once_with(
                certificate_chain=b"cert bytes", private_key=b"key bytes"
            )
            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=cred,
                credentials_file=None,
                scopes=None,
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            assert transport.grpc_channel == mock_grpc_channel
            assert transport._ssl_channel_credentials == mock_ssl_cred


# Remove this test when deprecated arguments (api_mtls_endpoint, client_cert_source) are
# removed from grpc/grpc_asyncio transport constructor.
@pytest.mark.parametrize(
    "transport_class",
    [transports.FirestoreGrpcTransport, transports.FirestoreGrpcAsyncIOTransport],
)
def test_firestore_transport_channel_mtls_with_adc(transport_class):
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        with mock.patch.object(
            transport_class, "create_channel"
        ) as grpc_create_channel:
            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel
            mock_cred = mock.Mock()

            with pytest.warns(DeprecationWarning):
                transport = transport_class(
                    host="squid.clam.whelk",
                    credentials=mock_cred,
                    api_mtls_endpoint="mtls.squid.clam.whelk",
                    client_cert_source=None,
                )

            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=mock_cred,
                credentials_file=None,
                scopes=None,
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            assert transport.grpc_channel == mock_grpc_channel


def test_common_billing_account_path():
    billing_account = "squid"
    expected = "billingAccounts/{billing_account}".format(
        billing_account=billing_account,
    )
    actual = FirestoreClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "clam",
    }
    path = FirestoreClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = FirestoreClient.parse_common_billing_account_path(path)
    assert expected == actual


def test_common_folder_path():
    folder = "whelk"
    expected = "folders/{folder}".format(
        folder=folder,
    )
    actual = FirestoreClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "octopus",
    }
    path = FirestoreClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = FirestoreClient.parse_common_folder_path(path)
    assert expected == actual


def test_common_organization_path():
    organization = "oyster"
    expected = "organizations/{organization}".format(
        organization=organization,
    )
    actual = FirestoreClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "nudibranch",
    }
    path = FirestoreClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = FirestoreClient.parse_common_organization_path(path)
    assert expected == actual


def test_common_project_path():
    project = "cuttlefish"
    expected = "projects/{project}".format(
        project=project,
    )
    actual = FirestoreClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "mussel",
    }
    path = FirestoreClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = FirestoreClient.parse_common_project_path(path)
    assert expected == actual


def test_common_location_path():
    project = "winkle"
    location = "nautilus"
    expected = "projects/{project}/locations/{location}".format(
        project=project,
        location=location,
    )
    actual = FirestoreClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "scallop",
        "location": "abalone",
    }
    path = FirestoreClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = FirestoreClient.parse_common_location_path(path)
    assert expected == actual


def test_client_with_default_client_info():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.FirestoreTransport, "_prep_wrapped_messages"
    ) as prep:
        client = FirestoreClient(
            credentials=ga_credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.FirestoreTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = FirestoreClient.get_transport_class()
        transport = transport_class(
            credentials=ga_credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)


@pytest.mark.asyncio
async def test_transport_close_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc_asyncio",
    )
    with mock.patch.object(
        type(getattr(client.transport, "grpc_channel")), "close"
    ) as close:
        async with client:
            close.assert_not_called()
        close.assert_called_once()


def test_cancel_operation_rest_bad_request(
    transport: str = "rest", request_type=operations_pb2.CancelOperationRequest
):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/databases/sample2/operations/sample3"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.cancel_operation(request)


@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.CancelOperationRequest,
        dict,
    ],
)
def test_cancel_operation_rest(request_type):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request_init = {"name": "projects/sample1/databases/sample2/operations/sample3"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = "{}"

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.cancel_operation(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_operation_rest_bad_request(
    transport: str = "rest", request_type=operations_pb2.DeleteOperationRequest
):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/databases/sample2/operations/sample3"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.delete_operation(request)


@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.DeleteOperationRequest,
        dict,
    ],
)
def test_delete_operation_rest(request_type):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request_init = {"name": "projects/sample1/databases/sample2/operations/sample3"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = "{}"

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.delete_operation(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_get_operation_rest_bad_request(
    transport: str = "rest", request_type=operations_pb2.GetOperationRequest
):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/databases/sample2/operations/sample3"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get_operation(request)


@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.GetOperationRequest,
        dict,
    ],
)
def test_get_operation_rest(request_type):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request_init = {"name": "projects/sample1/databases/sample2/operations/sample3"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.get_operation(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)


def test_list_operations_rest_bad_request(
    transport: str = "rest", request_type=operations_pb2.ListOperationsRequest
):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/databases/sample2"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.list_operations(request)


@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.ListOperationsRequest,
        dict,
    ],
)
def test_list_operations_rest(request_type):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request_init = {"name": "projects/sample1/databases/sample2"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.ListOperationsResponse()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.list_operations(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.ListOperationsResponse)


def test_delete_operation(transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.DeleteOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.delete_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_delete_operation_async(transport: str = "grpc"):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.DeleteOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.delete_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_operation_field_headers():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.DeleteOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        call.return_value = None

        client.delete_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_operation_field_headers_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.DeleteOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.delete_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


def test_delete_operation_from_dict():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.delete_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_delete_operation_from_dict_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.delete_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_cancel_operation(transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.CancelOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_cancel_operation_async(transport: str = "grpc"):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.CancelOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_operation_field_headers():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.CancelOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        call.return_value = None

        client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_cancel_operation_field_headers_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.CancelOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


def test_cancel_operation_from_dict():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.cancel_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_cancel_operation_from_dict_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.cancel_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_get_operation(transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.GetOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation()
        response = client.get_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)


@pytest.mark.asyncio
async def test_get_operation_async(transport: str = "grpc"):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.GetOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation()
        )
        response = await client.get_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)


def test_get_operation_field_headers():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.GetOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        call.return_value = operations_pb2.Operation()

        client.get_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_operation_field_headers_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.GetOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation()
        )
        await client.get_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


def test_get_operation_from_dict():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation()

        response = client.get_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_get_operation_from_dict_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation()
        )
        response = await client.get_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_list_operations(transport: str = "grpc"):
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.ListOperationsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.ListOperationsResponse()
        response = client.list_operations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.ListOperationsResponse)


@pytest.mark.asyncio
async def test_list_operations_async(transport: str = "grpc"):
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.ListOperationsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.ListOperationsResponse()
        )
        response = await client.list_operations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.ListOperationsResponse)


def test_list_operations_field_headers():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.ListOperationsRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        call.return_value = operations_pb2.ListOperationsResponse()

        client.list_operations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_operations_field_headers_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.ListOperationsRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.ListOperationsResponse()
        )
        await client.list_operations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


def test_list_operations_from_dict():
    client = FirestoreClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.ListOperationsResponse()

        response = client.list_operations(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_list_operations_from_dict_async():
    client = FirestoreAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.ListOperationsResponse()
        )
        response = await client.list_operations(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_transport_close():
    transports = {
        "rest": "_session",
        "grpc": "_grpc_channel",
    }

    for transport, close_name in transports.items():
        client = FirestoreClient(
            credentials=ga_credentials.AnonymousCredentials(), transport=transport
        )
        with mock.patch.object(
            type(getattr(client.transport, close_name)), "close"
        ) as close:
            with client:
                close.assert_not_called()
            close.assert_called_once()


def test_client_ctx():
    transports = [
        "rest",
        "grpc",
    ]
    for transport in transports:
        client = FirestoreClient(
            credentials=ga_credentials.AnonymousCredentials(), transport=transport
        )
        # Test client calls underlying transport.
        with mock.patch.object(type(client.transport), "close") as close:
            close.assert_not_called()
            with client:
                pass
            close.assert_called()


@pytest.mark.parametrize(
    "client_class,transport_class",
    [
        (FirestoreClient, transports.FirestoreGrpcTransport),
        (FirestoreAsyncClient, transports.FirestoreGrpcAsyncIOTransport),
    ],
)
def test_api_key_credentials(client_class, transport_class):
    with mock.patch.object(
        google.auth._default, "get_api_key_credentials", create=True
    ) as get_api_key_credentials:
        mock_cred = mock.Mock()
        get_api_key_credentials.return_value = mock_cred
        options = client_options.ClientOptions()
        options.api_key = "api_key"
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(client_options=options)
            patched.assert_called_once_with(
                credentials=mock_cred,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
                api_audience=None,
            )
