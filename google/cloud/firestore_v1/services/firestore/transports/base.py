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

import abc
import typing

from google import auth
from google.auth import credentials  # type: ignore

from google.firestore_v1.types import document
from google.firestore_v1.types import document as gf_document
from google.firestore_v1.types import firestore
from google.protobuf import empty_pb2 as empty  # type: ignore


class FirestoreTransport(metaclass=abc.ABCMeta):
    """Abstract transport class for Firestore."""

    AUTH_SCOPES = (
        'https://www.googleapis.com/auth/cloud-platform',
        'https://www.googleapis.com/auth/datastore',
    )

    def __init__(
            self, *,
            host: str = 'firestore.googleapis.com',
            credentials: credentials.Credentials = None,
            ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]): The hostname to connect to.
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
        """
        # Save the hostname. Default to port 443 (HTTPS) if none is specified.
        if ':' not in host:
            host += ':443'
        self._host = host

        # If no credentials are provided, then determine the appropriate
        # defaults.
        if credentials is None:
            credentials, _ = auth.default(scopes=self.AUTH_SCOPES)

        # Save the credentials.
        self._credentials = credentials

    @property
    def get_document(self) -> typing.Callable[
            [firestore.GetDocumentRequest],
            document.Document]:
        raise NotImplementedError

    @property
    def list_documents(self) -> typing.Callable[
            [firestore.ListDocumentsRequest],
            firestore.ListDocumentsResponse]:
        raise NotImplementedError

    @property
    def update_document(self) -> typing.Callable[
            [firestore.UpdateDocumentRequest],
            gf_document.Document]:
        raise NotImplementedError

    @property
    def delete_document(self) -> typing.Callable[
            [firestore.DeleteDocumentRequest],
            empty.Empty]:
        raise NotImplementedError

    @property
    def batch_get_documents(self) -> typing.Callable[
            [firestore.BatchGetDocumentsRequest],
            firestore.BatchGetDocumentsResponse]:
        raise NotImplementedError

    @property
    def begin_transaction(self) -> typing.Callable[
            [firestore.BeginTransactionRequest],
            firestore.BeginTransactionResponse]:
        raise NotImplementedError

    @property
    def commit(self) -> typing.Callable[
            [firestore.CommitRequest],
            firestore.CommitResponse]:
        raise NotImplementedError

    @property
    def rollback(self) -> typing.Callable[
            [firestore.RollbackRequest],
            empty.Empty]:
        raise NotImplementedError

    @property
    def run_query(self) -> typing.Callable[
            [firestore.RunQueryRequest],
            firestore.RunQueryResponse]:
        raise NotImplementedError

    @property
    def partition_query(self) -> typing.Callable[
            [firestore.PartitionQueryRequest],
            firestore.PartitionQueryResponse]:
        raise NotImplementedError

    @property
    def write(self) -> typing.Callable[
            [firestore.WriteRequest],
            firestore.WriteResponse]:
        raise NotImplementedError

    @property
    def listen(self) -> typing.Callable[
            [firestore.ListenRequest],
            firestore.ListenResponse]:
        raise NotImplementedError

    @property
    def list_collection_ids(self) -> typing.Callable[
            [firestore.ListCollectionIdsRequest],
            firestore.ListCollectionIdsResponse]:
        raise NotImplementedError

    @property
    def batch_write(self) -> typing.Callable[
            [firestore.BatchWriteRequest],
            firestore.BatchWriteResponse]:
        raise NotImplementedError

    @property
    def create_document(self) -> typing.Callable[
            [firestore.CreateDocumentRequest],
            document.Document]:
        raise NotImplementedError


__all__ = (
    'FirestoreTransport',
)
