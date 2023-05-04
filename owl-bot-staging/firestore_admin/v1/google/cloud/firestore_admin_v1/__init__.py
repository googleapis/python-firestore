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
from google.cloud.firestore_admin_v1 import gapic_version as package_version

__version__ = package_version.__version__


from .services.firestore_admin import FirestoreAdminClient
from .services.firestore_admin import FirestoreAdminAsyncClient

from .types.database import Database
from .types.field import Field
from .types.firestore_admin import CreateIndexRequest
from .types.firestore_admin import DeleteIndexRequest
from .types.firestore_admin import ExportDocumentsRequest
from .types.firestore_admin import GetDatabaseRequest
from .types.firestore_admin import GetFieldRequest
from .types.firestore_admin import GetIndexRequest
from .types.firestore_admin import ImportDocumentsRequest
from .types.firestore_admin import ListDatabasesRequest
from .types.firestore_admin import ListDatabasesResponse
from .types.firestore_admin import ListFieldsRequest
from .types.firestore_admin import ListFieldsResponse
from .types.firestore_admin import ListIndexesRequest
from .types.firestore_admin import ListIndexesResponse
from .types.firestore_admin import UpdateDatabaseMetadata
from .types.firestore_admin import UpdateDatabaseRequest
from .types.firestore_admin import UpdateFieldRequest
from .types.index import Index
from .types.location import LocationMetadata
from .types.operation import ExportDocumentsMetadata
from .types.operation import ExportDocumentsResponse
from .types.operation import FieldOperationMetadata
from .types.operation import ImportDocumentsMetadata
from .types.operation import IndexOperationMetadata
from .types.operation import Progress
from .types.operation import OperationState

__all__ = (
    'FirestoreAdminAsyncClient',
'CreateIndexRequest',
'Database',
'DeleteIndexRequest',
'ExportDocumentsMetadata',
'ExportDocumentsRequest',
'ExportDocumentsResponse',
'Field',
'FieldOperationMetadata',
'FirestoreAdminClient',
'GetDatabaseRequest',
'GetFieldRequest',
'GetIndexRequest',
'ImportDocumentsMetadata',
'ImportDocumentsRequest',
'Index',
'IndexOperationMetadata',
'ListDatabasesRequest',
'ListDatabasesResponse',
'ListFieldsRequest',
'ListFieldsResponse',
'ListIndexesRequest',
'ListIndexesResponse',
'LocationMetadata',
'OperationState',
'Progress',
'UpdateDatabaseMetadata',
'UpdateDatabaseRequest',
'UpdateFieldRequest',
)