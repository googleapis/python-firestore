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

from google.cloud.firestore_admin_v1.services.firestore_admin.client import FirestoreAdminClient
from google.cloud.firestore_admin_v1.services.firestore_admin.async_client import FirestoreAdminAsyncClient

from google.cloud.firestore_admin_v1.types.database import Database
from google.cloud.firestore_admin_v1.types.field import Field
from google.cloud.firestore_admin_v1.types.firestore_admin import CreateIndexRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import DeleteIndexRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import ExportDocumentsRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import GetDatabaseRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import GetFieldRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import GetIndexRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import ImportDocumentsRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import ListDatabasesRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import ListDatabasesResponse
from google.cloud.firestore_admin_v1.types.firestore_admin import ListFieldsRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import ListFieldsResponse
from google.cloud.firestore_admin_v1.types.firestore_admin import ListIndexesRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import ListIndexesResponse
from google.cloud.firestore_admin_v1.types.firestore_admin import UpdateDatabaseMetadata
from google.cloud.firestore_admin_v1.types.firestore_admin import UpdateDatabaseRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import UpdateFieldRequest
from google.cloud.firestore_admin_v1.types.index import Index
from google.cloud.firestore_admin_v1.types.location import LocationMetadata
from google.cloud.firestore_admin_v1.types.operation import ExportDocumentsMetadata
from google.cloud.firestore_admin_v1.types.operation import ExportDocumentsResponse
from google.cloud.firestore_admin_v1.types.operation import FieldOperationMetadata
from google.cloud.firestore_admin_v1.types.operation import ImportDocumentsMetadata
from google.cloud.firestore_admin_v1.types.operation import IndexOperationMetadata
from google.cloud.firestore_admin_v1.types.operation import Progress
from google.cloud.firestore_admin_v1.types.operation import OperationState

__all__ = ('FirestoreAdminClient',
    'FirestoreAdminAsyncClient',
    'Database',
    'Field',
    'CreateIndexRequest',
    'DeleteIndexRequest',
    'ExportDocumentsRequest',
    'GetDatabaseRequest',
    'GetFieldRequest',
    'GetIndexRequest',
    'ImportDocumentsRequest',
    'ListDatabasesRequest',
    'ListDatabasesResponse',
    'ListFieldsRequest',
    'ListFieldsResponse',
    'ListIndexesRequest',
    'ListIndexesResponse',
    'UpdateDatabaseMetadata',
    'UpdateDatabaseRequest',
    'UpdateFieldRequest',
    'Index',
    'LocationMetadata',
    'ExportDocumentsMetadata',
    'ExportDocumentsResponse',
    'FieldOperationMetadata',
    'ImportDocumentsMetadata',
    'IndexOperationMetadata',
    'Progress',
    'OperationState',
)
