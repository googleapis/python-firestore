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
from google.cloud.firestore import gapic_version as package_version

__version__ = package_version.__version__


from google.cloud.firestore_v1.services.firestore.client import FirestoreClient
from google.cloud.firestore_v1.services.firestore.async_client import FirestoreAsyncClient

from google.cloud.firestore_v1.types.aggregation_result import AggregationResult
from google.cloud.firestore_v1.types.bloom_filter import BitSequence
from google.cloud.firestore_v1.types.bloom_filter import BloomFilter
from google.cloud.firestore_v1.types.common import DocumentMask
from google.cloud.firestore_v1.types.common import Precondition
from google.cloud.firestore_v1.types.common import TransactionOptions
from google.cloud.firestore_v1.types.document import ArrayValue
from google.cloud.firestore_v1.types.document import Document
from google.cloud.firestore_v1.types.document import MapValue
from google.cloud.firestore_v1.types.document import Value
from google.cloud.firestore_v1.types.firestore import BatchGetDocumentsRequest
from google.cloud.firestore_v1.types.firestore import BatchGetDocumentsResponse
from google.cloud.firestore_v1.types.firestore import BatchWriteRequest
from google.cloud.firestore_v1.types.firestore import BatchWriteResponse
from google.cloud.firestore_v1.types.firestore import BeginTransactionRequest
from google.cloud.firestore_v1.types.firestore import BeginTransactionResponse
from google.cloud.firestore_v1.types.firestore import CommitRequest
from google.cloud.firestore_v1.types.firestore import CommitResponse
from google.cloud.firestore_v1.types.firestore import CreateDocumentRequest
from google.cloud.firestore_v1.types.firestore import DeleteDocumentRequest
from google.cloud.firestore_v1.types.firestore import GetDocumentRequest
from google.cloud.firestore_v1.types.firestore import ListCollectionIdsRequest
from google.cloud.firestore_v1.types.firestore import ListCollectionIdsResponse
from google.cloud.firestore_v1.types.firestore import ListDocumentsRequest
from google.cloud.firestore_v1.types.firestore import ListDocumentsResponse
from google.cloud.firestore_v1.types.firestore import ListenRequest
from google.cloud.firestore_v1.types.firestore import ListenResponse
from google.cloud.firestore_v1.types.firestore import PartitionQueryRequest
from google.cloud.firestore_v1.types.firestore import PartitionQueryResponse
from google.cloud.firestore_v1.types.firestore import RollbackRequest
from google.cloud.firestore_v1.types.firestore import RunAggregationQueryRequest
from google.cloud.firestore_v1.types.firestore import RunAggregationQueryResponse
from google.cloud.firestore_v1.types.firestore import RunQueryRequest
from google.cloud.firestore_v1.types.firestore import RunQueryResponse
from google.cloud.firestore_v1.types.firestore import Target
from google.cloud.firestore_v1.types.firestore import TargetChange
from google.cloud.firestore_v1.types.firestore import UpdateDocumentRequest
from google.cloud.firestore_v1.types.firestore import WriteRequest
from google.cloud.firestore_v1.types.firestore import WriteResponse
from google.cloud.firestore_v1.types.query import Cursor
from google.cloud.firestore_v1.types.query import StructuredAggregationQuery
from google.cloud.firestore_v1.types.query import StructuredQuery
from google.cloud.firestore_v1.types.write import DocumentChange
from google.cloud.firestore_v1.types.write import DocumentDelete
from google.cloud.firestore_v1.types.write import DocumentRemove
from google.cloud.firestore_v1.types.write import DocumentTransform
from google.cloud.firestore_v1.types.write import ExistenceFilter
from google.cloud.firestore_v1.types.write import Write
from google.cloud.firestore_v1.types.write import WriteResult

__all__ = ('FirestoreClient',
    'FirestoreAsyncClient',
    'AggregationResult',
    'BitSequence',
    'BloomFilter',
    'DocumentMask',
    'Precondition',
    'TransactionOptions',
    'ArrayValue',
    'Document',
    'MapValue',
    'Value',
    'BatchGetDocumentsRequest',
    'BatchGetDocumentsResponse',
    'BatchWriteRequest',
    'BatchWriteResponse',
    'BeginTransactionRequest',
    'BeginTransactionResponse',
    'CommitRequest',
    'CommitResponse',
    'CreateDocumentRequest',
    'DeleteDocumentRequest',
    'GetDocumentRequest',
    'ListCollectionIdsRequest',
    'ListCollectionIdsResponse',
    'ListDocumentsRequest',
    'ListDocumentsResponse',
    'ListenRequest',
    'ListenResponse',
    'PartitionQueryRequest',
    'PartitionQueryResponse',
    'RollbackRequest',
    'RunAggregationQueryRequest',
    'RunAggregationQueryResponse',
    'RunQueryRequest',
    'RunQueryResponse',
    'Target',
    'TargetChange',
    'UpdateDocumentRequest',
    'WriteRequest',
    'WriteResponse',
    'Cursor',
    'StructuredAggregationQuery',
    'StructuredQuery',
    'DocumentChange',
    'DocumentDelete',
    'DocumentRemove',
    'DocumentTransform',
    'ExistenceFilter',
    'Write',
    'WriteResult',
)
