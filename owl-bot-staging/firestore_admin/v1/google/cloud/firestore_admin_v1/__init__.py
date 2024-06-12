# -*- coding: utf-8 -*-
# Copyright 2024 Google LLC
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

from .types.backup import Backup
from .types.database import Database
from .types.field import Field
from .types.firestore_admin import BulkDeleteDocumentsRequest
from .types.firestore_admin import BulkDeleteDocumentsResponse
from .types.firestore_admin import CreateBackupScheduleRequest
from .types.firestore_admin import CreateDatabaseMetadata
from .types.firestore_admin import CreateDatabaseRequest
from .types.firestore_admin import CreateIndexRequest
from .types.firestore_admin import DeleteBackupRequest
from .types.firestore_admin import DeleteBackupScheduleRequest
from .types.firestore_admin import DeleteDatabaseMetadata
from .types.firestore_admin import DeleteDatabaseRequest
from .types.firestore_admin import DeleteIndexRequest
from .types.firestore_admin import ExportDocumentsRequest
from .types.firestore_admin import GetBackupRequest
from .types.firestore_admin import GetBackupScheduleRequest
from .types.firestore_admin import GetDatabaseRequest
from .types.firestore_admin import GetFieldRequest
from .types.firestore_admin import GetIndexRequest
from .types.firestore_admin import ImportDocumentsRequest
from .types.firestore_admin import ListBackupSchedulesRequest
from .types.firestore_admin import ListBackupSchedulesResponse
from .types.firestore_admin import ListBackupsRequest
from .types.firestore_admin import ListBackupsResponse
from .types.firestore_admin import ListDatabasesRequest
from .types.firestore_admin import ListDatabasesResponse
from .types.firestore_admin import ListFieldsRequest
from .types.firestore_admin import ListFieldsResponse
from .types.firestore_admin import ListIndexesRequest
from .types.firestore_admin import ListIndexesResponse
from .types.firestore_admin import RestoreDatabaseRequest
from .types.firestore_admin import UpdateBackupScheduleRequest
from .types.firestore_admin import UpdateDatabaseMetadata
from .types.firestore_admin import UpdateDatabaseRequest
from .types.firestore_admin import UpdateFieldRequest
from .types.index import Index
from .types.location import LocationMetadata
from .types.operation import BulkDeleteDocumentsMetadata
from .types.operation import ExportDocumentsMetadata
from .types.operation import ExportDocumentsResponse
from .types.operation import FieldOperationMetadata
from .types.operation import ImportDocumentsMetadata
from .types.operation import IndexOperationMetadata
from .types.operation import Progress
from .types.operation import RestoreDatabaseMetadata
from .types.operation import OperationState
from .types.schedule import BackupSchedule
from .types.schedule import DailyRecurrence
from .types.schedule import WeeklyRecurrence

__all__ = (
    'FirestoreAdminAsyncClient',
'Backup',
'BackupSchedule',
'BulkDeleteDocumentsMetadata',
'BulkDeleteDocumentsRequest',
'BulkDeleteDocumentsResponse',
'CreateBackupScheduleRequest',
'CreateDatabaseMetadata',
'CreateDatabaseRequest',
'CreateIndexRequest',
'DailyRecurrence',
'Database',
'DeleteBackupRequest',
'DeleteBackupScheduleRequest',
'DeleteDatabaseMetadata',
'DeleteDatabaseRequest',
'DeleteIndexRequest',
'ExportDocumentsMetadata',
'ExportDocumentsRequest',
'ExportDocumentsResponse',
'Field',
'FieldOperationMetadata',
'FirestoreAdminClient',
'GetBackupRequest',
'GetBackupScheduleRequest',
'GetDatabaseRequest',
'GetFieldRequest',
'GetIndexRequest',
'ImportDocumentsMetadata',
'ImportDocumentsRequest',
'Index',
'IndexOperationMetadata',
'ListBackupSchedulesRequest',
'ListBackupSchedulesResponse',
'ListBackupsRequest',
'ListBackupsResponse',
'ListDatabasesRequest',
'ListDatabasesResponse',
'ListFieldsRequest',
'ListFieldsResponse',
'ListIndexesRequest',
'ListIndexesResponse',
'LocationMetadata',
'OperationState',
'Progress',
'RestoreDatabaseMetadata',
'RestoreDatabaseRequest',
'UpdateBackupScheduleRequest',
'UpdateDatabaseMetadata',
'UpdateDatabaseRequest',
'UpdateFieldRequest',
'WeeklyRecurrence',
)
