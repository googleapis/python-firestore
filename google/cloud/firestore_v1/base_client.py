# Copyright 2017 Google LLC All rights reserved.
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

"""Client for interacting with the Google Cloud Firestore API.

This is the base from which all interactions with the API occur.

In the hierarchy of API concepts

* a :class:`~google.cloud.firestore_v1.client.Client` owns a
  :class:`~google.cloud.firestore_v1.collection.CollectionReference`
* a :class:`~google.cloud.firestore_v1.client.Client` owns a
  :class:`~google.cloud.firestore_v1.document.DocumentReference`
"""
import os

import google.api_core.client_options
import google.api_core.path_template
from google.api_core.gapic_v1 import client_info
from google.cloud.client import ClientWithProject

from google.cloud.firestore_v1 import _helpers
from google.cloud.firestore_v1 import __version__
from google.cloud.firestore_v1 import types
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.field_path import render_field_path
from google.cloud.firestore_v1.services.firestore import client as firestore_client
from google.cloud.firestore_v1.services.firestore.transports import (
    grpc as firestore_grpc_transport,
)

DEFAULT_DATABASE = "(default)"
"""str: The default database used in a :class:`~google.cloud.firestore_v1.client.Client`."""
_BAD_OPTION_ERR = (
    "Exactly one of ``last_update_time`` or ``exists`` " "must be provided."
)
_BAD_DOC_TEMPLATE = (
    "Document {!r} appeared in response but was not present among references"
)
_ACTIVE_TXN = "There is already an active transaction."
_INACTIVE_TXN = "There is no active transaction."
_CLIENT_INFO = client_info.ClientInfo(client_library_version=__version__)
_FIRESTORE_EMULATOR_HOST = "FIRESTORE_EMULATOR_HOST"


class BaseClient(ClientWithProject):
    """Client for interacting with Google Cloud Firestore API.

    .. note::

        Since the Cloud Firestore API requires the gRPC transport, no
        ``_http`` argument is accepted by this class.

    Args:
        project (Optional[str]): The project which the client acts on behalf
            of. If not passed, falls back to the default inferred
            from the environment.
        credentials (Optional[~google.auth.credentials.Credentials]): The
            OAuth2 Credentials to use for this client. If not passed, falls
            back to the default inferred from the environment.
        database (Optional[str]): The database name that the client targets.
            For now, :attr:`DEFAULT_DATABASE` (the default value) is the
            only valid database.
        client_info (Optional[google.api_core.gapic_v1.client_info.ClientInfo]):
            The client info used to send a user-agent string along with API
            requests. If ``None``, then default info will be used. Generally,
            you only need to set this if you're developing your own library
            or partner tool.
        client_options (Union[dict, google.api_core.client_options.ClientOptions]):
            Client options used to set user options on the client. API Endpoint
            should be set through client_options.
    """

    SCOPE = (
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/datastore",
    )
    """The scopes required for authenticating with the Firestore service."""

    _firestore_api_internal = None
    _database_string_internal = None
    _rpc_metadata_internal = None

    def __init__(
        self,
        project=None,
        credentials=None,
        database=DEFAULT_DATABASE,
        client_info=_CLIENT_INFO,
        client_options=None,
    ):
        # NOTE: This API has no use for the _http argument, but sending it
        #       will have no impact since the _http() @property only lazily
        #       creates a working HTTP object.
        super(BaseClient, self).__init__(
            project=project, credentials=credentials, _http=None
        )
        self._client_info = client_info
        if client_options:
            if type(client_options) == dict:
                client_options = google.api_core.client_options.from_dict(
                    client_options
                )
        self._client_options = client_options

        self._database = database
        self._emulator_host = os.getenv(_FIRESTORE_EMULATOR_HOST)

    @property
    def _firestore_api(self):
        """Lazy-loading getter GAPIC Firestore API.
        Returns:
            :class:`~google.cloud.gapic.firestore.v1`.firestore_client.FirestoreClient:
            <The GAPIC client with the credentials of the current client.
        """
        if self._firestore_api_internal is None:
            # Use a custom channel.
            # We need this in order to set appropriate keepalive options.

            if self._emulator_host is not None:
                # TODO(microgen): this likely needs to be adapted to use insecure_channel
                # on new generated surface.
                channel = firestore_grpc_transport.FirestoreGrpcTransport.create_channel(
                    host=self._emulator_host
                )
            else:
                channel = firestore_grpc_transport.FirestoreGrpcTransport.create_channel(
                    self._target,
                    credentials=self._credentials,
                    options={"grpc.keepalive_time_ms": 30000}.items(),
                )

            self._transport = firestore_grpc_transport.FirestoreGrpcTransport(
                host=self._target, channel=channel
            )

            self._firestore_api_internal = firestore_client.FirestoreClient(
                transport=self._transport, client_options=self._client_options
            )
            firestore_client._client_info = self._client_info

        return self._firestore_api_internal

    @property
    def _target(self):
        """Return the target (where the API is).

        Returns:
            str: The location of the API.
        """
        if self._emulator_host is not None:
            return self._emulator_host
        elif self._client_options and self._client_options.api_endpoint:
            return self._client_options.api_endpoint
        else:
            return firestore_client.FirestoreClient.DEFAULT_ENDPOINT

    @property
    def _database_string(self):
        """The database string corresponding to this client's project.

        This value is lazy-loaded and cached.

        Will be of the form

            ``projects/{project_id}/databases/{database_id}``

        but ``database_id == '(default)'`` for the time being.

        Returns:
            str: The fully-qualified database string for the current
            project. (The default database is also in this string.)
        """
        if self._database_string_internal is None:
            db_str = google.api_core.path_template.expand(
                "projects/{project}/databases/{database}",
                project=self.project,
                database=self._database,
            )

            self._database_string_internal = db_str

        return self._database_string_internal

    @property
    def _rpc_metadata(self):
        """The RPC metadata for this client's associated database.

        Returns:
            Sequence[Tuple(str, str)]: RPC metadata with resource prefix
            for the database associated with this client.
        """
        if self._rpc_metadata_internal is None:
            self._rpc_metadata_internal = _helpers.metadata_with_prefix(
                self._database_string
            )

            if self._emulator_host is not None:
                # The emulator requires additional metadata to be set.
                self._rpc_metadata_internal.append(("authorization", "Bearer owner"))

        return self._rpc_metadata_internal

    def collection(self, *collection_path):
        raise NotImplementedError

    def collection_group(self, collection_id):
        raise NotImplementedError

    def _get_collection_reference(self, collection_id):
        """Checks validity of collection_id and then uses subclasses collection implementation.

        Args:
            collection_id (str) Identifies the collections to query over.

                Every collection or subcollection with this ID as the last segment of its
                path will be included. Cannot contain a slash.

        Returns:
            The created collection.
        """
        if "/" in collection_id:
            raise ValueError(
                "Invalid collection_id "
                + collection_id
                + ". Collection IDs must not contain '/'."
            )

        return self.collection(collection_id)

    def document(self, *document_path):
        raise NotImplementedError

    def _document_path_helper(self, *document_path):
        """Standardize the format of path to tuple of path segments and strip the database string from path if present.

        Args:
            document_path (Tuple[str, ...]): Can either be

                * A single ``/``-delimited path to a document
                * A tuple of document path segments
        """
        path = _path_helper(document_path)
        base_path = self._database_string + "/documents/"
        joined_path = _helpers.DOCUMENT_PATH_DELIMITER.join(path)
        if joined_path.startswith(base_path):
            joined_path = joined_path[len(base_path) :]
        return joined_path.split(_helpers.DOCUMENT_PATH_DELIMITER)

    @staticmethod
    def field_path(*field_names):
        """Create a **field path** from a list of nested field names.

        A **field path** is a ``.``-delimited concatenation of the field
        names. It is used to represent a nested field. For example,
        in the data

        .. code-block:: python

           data = {
              'aa': {
                  'bb': {
                      'cc': 10,
                  },
              },
           }

        the field path ``'aa.bb.cc'`` represents the data stored in
        ``data['aa']['bb']['cc']``.

        Args:
            field_names (Tuple[str, ...]): The list of field names.

        Returns:
            str: The ``.``-delimited field path.
        """
        return render_field_path(field_names)

    @staticmethod
    def write_option(**kwargs):
        """Create a write option for write operations.

        Write operations include :meth:`~google.cloud.DocumentReference.set`,
        :meth:`~google.cloud.DocumentReference.update` and
        :meth:`~google.cloud.DocumentReference.delete`.

        One of the following keyword arguments must be provided:

        * ``last_update_time`` (:class:`google.protobuf.timestamp_pb2.\
               Timestamp`): A timestamp. When set, the target document must
               exist and have been last updated at that time. Protobuf
               ``update_time`` timestamps are typically returned from methods
               that perform write operations as part of a "write result"
               protobuf or directly.
        * ``exists`` (:class:`bool`): Indicates if the document being modified
              should already exist.

        Providing no argument would make the option have no effect (so
        it is not allowed). Providing multiple would be an apparent
        contradiction, since ``last_update_time`` assumes that the
        document **was** updated (it can't have been updated if it
        doesn't exist) and ``exists`` indicate that it is unknown if the
        document exists or not.

        Args:
            kwargs (Dict[str, Any]): The keyword arguments described above.

        Raises:
            TypeError: If anything other than exactly one argument is
                provided by the caller.

        Returns:
            :class:`~google.cloud.firestore_v1.client.WriteOption`:
            The option to be used to configure a write message.
        """
        if len(kwargs) != 1:
            raise TypeError(_BAD_OPTION_ERR)

        name, value = kwargs.popitem()
        if name == "last_update_time":
            return _helpers.LastUpdateOption(value)
        elif name == "exists":
            return _helpers.ExistsOption(value)
        else:
            extra = "{!r} was provided".format(name)
            raise TypeError(_BAD_OPTION_ERR, extra)

    def get_all(self, references, field_paths=None, transaction=None):
        raise NotImplementedError

    def collections(self):
        raise NotImplementedError

    def batch(self):
        raise NotImplementedError

    def transaction(self, **kwargs):
        raise NotImplementedError


def _reference_info(references):
    """Get information about document references.

    Helper for :meth:`~google.cloud.firestore_v1.client.Client.get_all`.

    Args:
        references (List[.DocumentReference, ...]): Iterable of document
            references.

    Returns:
        Tuple[List[str, ...], Dict[str, .DocumentReference]]: A two-tuple of

        * fully-qualified documents paths for each reference in ``references``
        * a mapping from the paths to the original reference. (If multiple
          ``references`` contains multiple references to the same document,
          that key will be overwritten in the result.)
    """
    document_paths = []
    reference_map = {}
    for reference in references:
        doc_path = reference._document_path
        document_paths.append(doc_path)
        reference_map[doc_path] = reference

    return document_paths, reference_map


def _get_reference(document_path, reference_map):
    """Get a document reference from a dictionary.

    This just wraps a simple dictionary look-up with a helpful error that is
    specific to :meth:`~google.cloud.firestore.client.Client.get_all`, the
    **public** caller of this function.

    Args:
        document_path (str): A fully-qualified document path.
        reference_map (Dict[str, .DocumentReference]): A mapping (produced
            by :func:`_reference_info`) of fully-qualified document paths to
            document references.

    Returns:
        .DocumentReference: The matching reference.

    Raises:
        ValueError: If ``document_path`` has not been encountered.
    """
    try:
        return reference_map[document_path]
    except KeyError:
        msg = _BAD_DOC_TEMPLATE.format(document_path)
        raise ValueError(msg)


def _parse_batch_get(get_doc_response, reference_map, client):
    """Parse a `BatchGetDocumentsResponse` protobuf.

    Args:
        get_doc_response (~google.cloud.proto.firestore.v1.\
            firestore.BatchGetDocumentsResponse): A single response (from
            a stream) containing the "get" response for a document.
        reference_map (Dict[str, .DocumentReference]): A mapping (produced
            by :func:`_reference_info`) of fully-qualified document paths to
            document references.
        client (:class:`~google.cloud.firestore_v1.client.Client`):
            A client that has a document factory.

    Returns:
       [.DocumentSnapshot]: The retrieved snapshot.

    Raises:
        ValueError: If the response has a ``result`` field (a oneof) other
            than ``found`` or ``missing``.
    """
    result_type = get_doc_response._pb.WhichOneof("result")
    if result_type == "found":
        reference = _get_reference(get_doc_response.found.name, reference_map)
        data = _helpers.decode_dict(get_doc_response.found.fields, client)
        snapshot = DocumentSnapshot(
            reference,
            data,
            exists=True,
            read_time=get_doc_response.read_time,
            create_time=get_doc_response.found.create_time,
            update_time=get_doc_response.found.update_time,
        )
    elif result_type == "missing":
        reference = _get_reference(get_doc_response.missing, reference_map)
        snapshot = DocumentSnapshot(
            reference,
            None,
            exists=False,
            read_time=get_doc_response.read_time,
            create_time=None,
            update_time=None,
        )
    else:
        raise ValueError(
            "`BatchGetDocumentsResponse.result` (a oneof) had a field other "
            "than `found` or `missing` set, or was unset"
        )
    return snapshot


def _get_doc_mask(field_paths):
    """Get a document mask if field paths are provided.

    Args:
        field_paths (Optional[Iterable[str, ...]]): An iterable of field
            paths (``.``-delimited list of field names) to use as a
            projection of document fields in the returned results.

    Returns:
        Optional[google.cloud.firestore_v1.types.DocumentMask]: A mask
            to project documents to a restricted set of field paths.
    """
    if field_paths is None:
        return None
    else:
        return types.DocumentMask(field_paths=field_paths)


def _item_to_collection_ref(iterator, item):
    """Convert collection ID to collection ref.

    Args:
        iterator (google.api_core.page_iterator.GRPCIterator):
            iterator response
        item (str): ID of the collection
    """
    return iterator.client.collection(item)


def _path_helper(path):
    """Standardize path into a tuple of path segments.

    Args:
        path (Tuple[str, ...]): Can either be

            * A single ``/``-delimited path
            * A tuple of path segments
    """
    if len(path) == 1:
        return path[0].split(_helpers.DOCUMENT_PATH_DELIMITER)
    else:
        return path
