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
# Generated code. DO NOT EDIT!
#
# Snippet for Rollback
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-firestore


# [START firestore_v1_generated_Firestore_Rollback_async]
from google.cloud import firestore_v1


async def sample_rollback():
    # Create a client
    client = firestore_v1.FirestoreAsyncClient()

    # Initialize request argument(s)
    request = firestore_v1.RollbackRequest(
        database="database_value",
        transaction=b'transaction_blob',
    )

    # Make the request
    await client.rollback(request=request)


# [END firestore_v1_generated_Firestore_Rollback_async]