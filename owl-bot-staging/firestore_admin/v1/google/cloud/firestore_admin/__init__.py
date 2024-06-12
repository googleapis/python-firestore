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
from google.cloud.firestore_admin import gapic_version as package_version

__version__ = package_version.__version__


from google.cloud.firestore_admin_v1.services.firestore_admin.client import FirestoreAdminClient
from google.cloud.firestore_admin_v1.services.firestore_admin.async_client import FirestoreAdminAsyncClient

from google.cloud.firestore_admin_v1.types.backup import Backup
from google.cloud.firestore_admin_v1.types.database import Database
from google.cloud.firestore_admin_v1.types.field import Field
from google.cloud.firestore_admin_v1.types.firestore_admin import BulkDeleteDocumentsRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import BulkDeleteDocumentsResponse
from google.cloud.firestore_admin_v1.types.firestore_admin import CreateBackupScheduleRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import CreateDatabaseMetadata
from google.cloud.firestore_admin_v1.types.firestore_admin import CreateDatabaseRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import CreateIndexRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import DeleteBackupRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import DeleteBackupScheduleRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import DeleteDatabaseMetadata
from google.cloud.firestore_admin_v1.types.firestore_admin import DeleteDatabaseRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import DeleteIndexRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import ExportDocumentsRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import GetBackupRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import GetBackupScheduleRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import GetDatabaseRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import GetFieldRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import GetIndexRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import ImportDocumentsRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import ListBackupSchedulesRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import ListBackupSchedulesResponse
from google.cloud.firestore_admin_v1.types.firestore_admin import ListBackupsRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import ListBackupsResponse
from google.cloud.firestore_admin_v1.types.firestore_admin import ListDatabasesRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import ListDatabasesResponse
from google.cloud.firestore_admin_v1.types.firestore_admin import ListFieldsRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import ListFieldsResponse
from google.cloud.firestore_admin_v1.types.firestore_admin import ListIndexesRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import ListIndexesResponse
from google.cloud.firestore_admin_v1.types.firestore_admin import RestoreDatabaseRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import UpdateBackupScheduleRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import UpdateDatabaseMetadata
from google.cloud.firestore_admin_v1.types.firestore_admin import UpdateDatabaseRequest
from google.cloud.firestore_admin_v1.types.firestore_admin import UpdateFieldRequest
from google.cloud.firestore_admin_v1.types.index import Index
from google.cloud.firestore_admin_v1.types.location import LocationMetadata
from google.cloud.firestore_admin_v1.types.operation import BulkDeleteDocumentsMetadata
from google.cloud.firestore_admin_v1.types.operation import ExportDocumentsMetadata
from google.cloud.firestore_admin_v1.types.operation import ExportDocumentsResponse
from google.cloud.firestore_admin_v1.types.operation import FieldOperationMetadata
from google.cloud.firestore_admin_v1.types.operation import ImportDocumentsMetadata
from google.cloud.firestore_admin_v1.types.operation import IndexOperationMetadata
from google.cloud.firestore_admin_v1.types.operation import Progress
from google.cloud.firestore_admin_v1.types.operation import RestoreDatabaseMetadata
from google.cloud.firestore_admin_v1.types.operation import OperationState
from google.cloud.firestore_admin_v1.types.schedule import BackupSchedule
from google.cloud.firestore_admin_v1.types.schedule import DailyRecurrence
from google.cloud.firestore_admin_v1.types.schedule import WeeklyRecurrence

__all__ = ('FirestoreAdminClient',
    'FirestoreAdminAsyncClient',
    'Backup',
    'Database',
    'Field',
    'BulkDeleteDocumentsRequest',
    'BulkDeleteDocumentsResponse',
    'CreateBackupScheduleRequest',
    'CreateDatabaseMetadata',
    'CreateDatabaseRequest',
    'CreateIndexRequest',
    'DeleteBackupRequest',
    'DeleteBackupScheduleRequest',
    'DeleteDatabaseMetadata',
    'DeleteDatabaseRequest',
    'DeleteIndexRequest',
    'ExportDocumentsRequest',
    'GetBackupRequest',
    'GetBackupScheduleRequest',
    'GetDatabaseRequest',
    'GetFieldRequest',
    'GetIndexRequest',
    'ImportDocumentsRequest',
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
    'RestoreDatabaseRequest',
    'UpdateBackupScheduleRequest',
    'UpdateDatabaseMetadata',
    'UpdateDatabaseRequest',
    'UpdateFieldRequest',
    'Index',
    'LocationMetadata',
    'BulkDeleteDocumentsMetadata',
    'ExportDocumentsMetadata',
    'ExportDocumentsResponse',
    'FieldOperationMetadata',
    'ImportDocumentsMetadata',
    'IndexOperationMetadata',
    'Progress',
    'RestoreDatabaseMetadata',
    'OperationState',
    'BackupSchedule',
    'DailyRecurrence',
    'WeeklyRecurrence',
)
