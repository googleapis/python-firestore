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

"""Python idiomatic client for Google Cloud Firestore."""

from pkg_resources import get_distribution
import warnings

__version__ = get_distribution("google-cloud-firestore").version

from google.cloud.firestore_v1beta1 import types
from google.cloud.firestore_v1beta1._helpers import GeoPoint
from google.cloud.firestore_v1beta1._helpers import ExistsOption
from google.cloud.firestore_v1beta1._helpers import LastUpdateOption
from google.cloud.firestore_v1beta1._helpers import ReadAfterWriteError
from google.cloud.firestore_v1beta1._helpers import WriteOption
from google.cloud.firestore_v1beta1.batch import WriteBatch
from google.cloud.firestore_v1beta1.client import Client
from google.cloud.firestore_v1beta1.collection import CollectionReference
from google.cloud.firestore_v1beta1.transforms import ArrayRemove
from google.cloud.firestore_v1beta1.transforms import ArrayUnion
from google.cloud.firestore_v1beta1.transforms import DELETE_FIELD
from google.cloud.firestore_v1beta1.transforms import SERVER_TIMESTAMP
from google.cloud.firestore_v1beta1.document import DocumentReference
from google.cloud.firestore_v1beta1.document import DocumentSnapshot
from google.cloud.firestore_v1beta1.gapic import enums
from google.cloud.firestore_v1beta1.query import Query
from google.cloud.firestore_v1beta1.transaction import Transaction
from google.cloud.firestore_v1beta1.transaction import transactional
from google.cloud.firestore_v1beta1.watch import Watch


_V1BETA1_DEPRECATED_MESSAGE = (
    "The 'v1beta1' API endpoint is deprecated. "
    "The client/library which supports it will be removed in a future release."
)
warnings.warn(_V1BETA1_DEPRECATED_MESSAGE, DeprecationWarning)


__all__ = [
    "__version__",
    "ArrayRemove",
    "ArrayUnion",
    "Client",
    "CollectionReference",
    "DELETE_FIELD",
    "DocumentReference",
    "DocumentSnapshot",
    "enums",
    "ExistsOption",
    "GeoPoint",
    "LastUpdateOption",
    "Query",
    "ReadAfterWriteError",
    "SERVER_TIMESTAMP",
    "Transaction",
    "transactional",
    "types",
    "Watch",
    "WriteBatch",
    "WriteOption",
]
