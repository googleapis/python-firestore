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
  :class:`~google.cloud.firestore_v1.async_collection.AsyncCollectionReference`
* a :class:`~google.cloud.firestore_v1.client.Client` owns a
  :class:`~google.cloud.firestore_v1.async_document.AsyncDocumentReference`
"""

from google.cloud.firestore_v1.client import (
    Client,
    DEFAULT_DATABASE,
    _CLIENT_INFO,
    _reference_info,
    _parse_batch_get,
    _get_doc_mask,
    _item_to_collection_ref,
)

from google.cloud.firestore_v1 import _helpers
from google.cloud.firestore_v1.async_query import AsyncQuery
from google.cloud.firestore_v1.async_batch import AsyncWriteBatch
from google.cloud.firestore_v1.async_collection import AsyncCollectionReference
from google.cloud.firestore_v1.async_document import AsyncDocumentReference
from google.cloud.firestore_v1.async_transaction import AsyncTransaction


class AsyncClient(Client):
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
        super(AsyncClient, self).__init__(
            project=project,
            credentials=credentials,
            database=database,
            client_info=client_info,
            client_options=client_options,
        )

    def collection(self, *collection_path):
        """Get a reference to a collection.

        For a top-level collection:

        .. code-block:: python

            >>> client.collection('top')

        For a sub-collection:

        .. code-block:: python

            >>> client.collection('mydocs/doc/subcol')
            >>> # is the same as
            >>> client.collection('mydocs', 'doc', 'subcol')

        Sub-collections can be nested deeper in a similar fashion.

        Args:
            collection_path (Tuple[str, ...]): Can either be

                * A single ``/``-delimited path to a collection
                * A tuple of collection path segments

        Returns:
            :class:`~google.cloud.firestore_v1.async_collection.AsyncCollectionReference`:
            A reference to a collection in the Firestore database.
        """
        if len(collection_path) == 1:
            path = collection_path[0].split(_helpers.DOCUMENT_PATH_DELIMITER)
        else:
            path = collection_path

        return AsyncCollectionReference(*path, client=self)

    def collection_group(self, collection_id):
        """
        Creates and returns a new AsyncQuery that includes all documents in the
        database that are contained in a collection or subcollection with the
        given collection_id.

        .. code-block:: python

            >>> query = client.collection_group('mygroup')

        @param {string} collectionId Identifies the collections to query over.
        Every collection or subcollection with this ID as the last segment of its
        path will be included. Cannot contain a slash.
        @returns {AsyncQuery} The created AsyncQuery.
        """
        if "/" in collection_id:
            raise ValueError(
                "Invalid collection_id "
                + collection_id
                + ". Collection IDs must not contain '/'."
            )

        collection = self.collection(collection_id)
        return AsyncQuery(collection, all_descendants=True)

    def document(self, *document_path):
        """Get a reference to a document in a collection.

        For a top-level document:

        .. code-block:: python

            >>> client.document('collek/shun')
            >>> # is the same as
            >>> client.document('collek', 'shun')

        For a document in a sub-collection:

        .. code-block:: python

            >>> client.document('mydocs/doc/subcol/child')
            >>> # is the same as
            >>> client.document('mydocs', 'doc', 'subcol', 'child')

        Documents in sub-collections can be nested deeper in a similar fashion.

        Args:
            document_path (Tuple[str, ...]): Can either be

                * A single ``/``-delimited path to a document
                * A tuple of document path segments

        Returns:
            :class:`~google.cloud.firestore_v1.document.AsyncDocumentReference`:
            A reference to a document in a collection.
        """
        if len(document_path) == 1:
            path = document_path[0].split(_helpers.DOCUMENT_PATH_DELIMITER)
        else:
            path = document_path

        # AsyncDocumentReference takes a relative path. Strip the database string if present.
        base_path = self._database_string + "/documents/"
        joined_path = _helpers.DOCUMENT_PATH_DELIMITER.join(path)
        if joined_path.startswith(base_path):
            joined_path = joined_path[len(base_path) :]
        path = joined_path.split(_helpers.DOCUMENT_PATH_DELIMITER)

        return AsyncDocumentReference(*path, client=self)

    async def get_all(self, references, field_paths=None, transaction=None):
        """Retrieve a batch of documents.

        .. note::

           Documents returned by this method are not guaranteed to be
           returned in the same order that they are given in ``references``.

        .. note::

           If multiple ``references`` refer to the same document, the server
           will only return one result.

        See :meth:`~google.cloud.firestore_v1.client.Client.field_path` for
        more information on **field paths**.

        If a ``transaction`` is used and it already has write operations
        added, this method cannot be used (i.e. read-after-write is not
        allowed).

        Args:
            references (List[.AsyncDocumentReference, ...]): Iterable of document
                references to be retrieved.
            field_paths (Optional[Iterable[str, ...]]): An iterable of field
                paths (``.``-delimited list of field names) to use as a
                projection of document fields in the returned results. If
                no value is provided, all fields will be returned.
            transaction (Optional[:class:`~google.cloud.firestore_v1.async_transaction.AsyncTransaction`]):
                An existing transaction that these ``references`` will be
                retrieved in.

        Yields:
            .DocumentSnapshot: The next document snapshot that fulfills the
            query, or :data:`None` if the document does not exist.
        """
        document_paths, reference_map = _reference_info(references)
        mask = _get_doc_mask(field_paths)
        response_iterator = self._firestore_api.batch_get_documents(
            self._database_string,
            document_paths,
            mask,
            transaction=_helpers.get_transaction_id(transaction),
            metadata=self._rpc_metadata,
        )

        for get_doc_response in response_iterator:
            yield _parse_batch_get(get_doc_response, reference_map, self)

    async def collections(self):
        """List top-level collections of the client's database.

        Returns:
            Sequence[:class:`~google.cloud.firestore_v1.async_collection.AsyncCollectionReference`]:
                iterator of subcollections of the current document.
        """
        iterator = self._firestore_api.list_collection_ids(
            "{}/documents".format(self._database_string), metadata=self._rpc_metadata
        )
        iterator.client = self
        iterator.item_to_value = _item_to_collection_ref
        return iterator

    def batch(self):
        """Get a batch instance from this client.

        Returns:
            :class:`~google.cloud.firestore_v1.async_batch.AsyncWriteBatch`:
            A "write" batch to be used for accumulating document changes and
            sending the changes all at once.
        """
        return AsyncWriteBatch(self)

    def transaction(self, **kwargs):
        """Get a transaction that uses this client.

        See :class:`~google.cloud.firestore_v1.async_transaction.AsyncTransaction` for
        more information on transactions and the constructor arguments.

        Args:
            kwargs (Dict[str, Any]): The keyword arguments (other than
                ``client``) to pass along to the
                :class:`~google.cloud.firestore_v1.async_transaction.AsyncTransaction`
                constructor.

        Returns:
            :class:`~google.cloud.firestore_v1.async_transaction.AsyncTransaction`:
            A transaction attached to this client.
        """
        return AsyncTransaction(self, **kwargs)
