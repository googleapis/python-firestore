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

from google.cloud.firestore_v1.base_client import (
    BaseClient,
    DEFAULT_DATABASE,
    _CLIENT_INFO,
    _reference_info,
    _parse_batch_get,
    _get_doc_mask,
    _path_helper,
)

from google.cloud.firestore_v1 import _helpers
from google.cloud.firestore_v1.query import Query
from google.cloud.firestore_v1.batch import WriteBatch
from google.cloud.firestore_v1.collection import CollectionReference
from google.cloud.firestore_v1.document import DocumentReference
from google.cloud.firestore_v1.transaction import Transaction


class Client(BaseClient):
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
        super(Client, self).__init__(
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
            :class:`~google.cloud.firestore_v1.collection.CollectionReference`:
            A reference to a collection in the Firestore database.
        """
        return CollectionReference(*_path_helper(collection_path), client=self)

    def collection_group(self, collection_id):
        """
        Creates and returns a new Query that includes all documents in the
        database that are contained in a collection or subcollection with the
        given collection_id.

        .. code-block:: python

            >>> query = client.collection_group('mygroup')

        Args:
            collection_id (str) Identifies the collections to query over.

                Every collection or subcollection with this ID as the last segment of its
                path will be included. Cannot contain a slash.

        Returns:
            :class:`~google.cloud.firestore_v1.query.Query`:
            The created Query.
        """
        return Query(
            self._get_collection_reference(collection_id), all_descendants=True
        )

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
            :class:`~google.cloud.firestore_v1.document.DocumentReference`:
            A reference to a document in a collection.
        """
        return DocumentReference(
            *self._document_path_helper(*document_path), client=self
        )

    def get_all(self, references, field_paths=None, transaction=None):
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
            references (List[.DocumentReference, ...]): Iterable of document
                references to be retrieved.
            field_paths (Optional[Iterable[str, ...]]): An iterable of field
                paths (``.``-delimited list of field names) to use as a
                projection of document fields in the returned results. If
                no value is provided, all fields will be returned.
            transaction (Optional[:class:`~google.cloud.firestore_v1.transaction.Transaction`]):
                An existing transaction that these ``references`` will be
                retrieved in.

        Yields:
            .DocumentSnapshot: The next document snapshot that fulfills the
            query, or :data:`None` if the document does not exist.
        """
        document_paths, reference_map = _reference_info(references)
        mask = _get_doc_mask(field_paths)
        response_iterator = self._firestore_api.batch_get_documents(
            request={
                "database": self._database_string,
                "documents": document_paths,
                "mask": mask,
                "transaction": _helpers.get_transaction_id(transaction),
            },
            metadata=self._rpc_metadata,
        )

        for get_doc_response in response_iterator:
            yield _parse_batch_get(get_doc_response, reference_map, self)

    def collections(self):
        """List top-level collections of the client's database.

        Returns:
            Sequence[:class:`~google.cloud.firestore_v1.collection.CollectionReference`]:
                iterator of subcollections of the current document.
        """
        iterator = self._firestore_api.list_collection_ids(
            request={"parent": "{}/documents".format(self._database_string)},
            metadata=self._rpc_metadata,
        )

        while True:
            for i in iterator.collection_ids:
                yield self.collection(i)
            if iterator.next_page_token:
                iterator = self._firestore_api.list_collection_ids(
                    request={
                        "parent": "{}/documents".format(self._database_string),
                        "page_token": iterator.next_page_token,
                    },
                    metadata=self._rpc_metadata,
                )
            else:
                return

        # TODO(microgen): currently this method is rewritten to iterate/page itself.
        # https://github.com/googleapis/gapic-generator-python/issues/516
        # it seems the generator ought to be able to do this itself.
        # iterator.client = self
        # iterator.item_to_value = _item_to_collection_ref
        # return iterator

    def batch(self):
        """Get a batch instance from this client.

        Returns:
            :class:`~google.cloud.firestore_v1.batch.WriteBatch`:
            A "write" batch to be used for accumulating document changes and
            sending the changes all at once.
        """
        return WriteBatch(self)

    def transaction(self, **kwargs):
        """Get a transaction that uses this client.

        See :class:`~google.cloud.firestore_v1.transaction.Transaction` for
        more information on transactions and the constructor arguments.

        Args:
            kwargs (Dict[str, Any]): The keyword arguments (other than
                ``client``) to pass along to the
                :class:`~google.cloud.firestore_v1.transaction.Transaction`
                constructor.

        Returns:
            :class:`~google.cloud.firestore_v1.transaction.Transaction`:
            A transaction attached to this client.
        """
        return Transaction(self, **kwargs)
