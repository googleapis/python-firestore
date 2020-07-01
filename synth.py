# Copyright 2018 Google LLC
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

"""This script is used to synthesize generated parts of this library."""
import synthtool as s
from synthtool import gcp

AUTOSYNTH_MULTIPLE_PRS = True
AUTOSYNTH_MULTIPLE_COMMITS = True

gapic = gcp.GAPICBazel()
common = gcp.CommonTemplates()
versions = ["v1beta1", "v1"]
admin_versions = ["v1"]


# ----------------------------------------------------------------------------
# Generate firestore GAPIC layer
# ----------------------------------------------------------------------------
for version in versions:
    library = gapic.py_library(
        service="firestore",
        version=version,
        bazel_target=f"//google/firestore/{version}:firestore-{version}-py",
        include_protos=True,
    )

    s.move(library / f"google/cloud/firestore_{version}/proto")
    s.move(library / f"google/cloud/firestore_{version}/gapic")
    s.move(library / f"tests/unit/gapic/{version}")

    s.replace(
        f"tests/unit/gapic/{version}/test_firestore_client_{version}.py",
        f"from google.cloud import firestore_{version}",
        f"from google.cloud.firestore_{version}.gapic import firestore_client",
    )

    s.replace(
        f"tests/unit/gapic/{version}/test_firestore_client_{version}.py",
        f"client = firestore_{version}.FirestoreClient",
        "client = firestore_client.FirestoreClient",
    )

# # TODO(busunkim): remove during microgenerator transition
# # This re-adds a resource helpers that were removed in a regeneration
# n = s.replace("google/cloud/**/firestore_client.py",
# """\s+def __init__\(""",
# '''     @classmethod
#     def any_path_path(cls, project, database, document, any_path):
#         """Return a fully-qualified any_path string."""
#         return google.api_core.path_template.expand(
#             "projects/{project}/databases/{database}/documents/{document}/{any_path=**}",
#             project=project,
#             database=database,
#             document=document,
#             any_path=any_path,
#         )

#     @classmethod
#     def database_root_path(cls, project, database):
#         """Return a fully-qualified database_root string."""
#         return google.api_core.path_template.expand(
#             "projects/{project}/databases/{database}",
#             project=project,
#             database=database,
#         )

#     @classmethod
#     def document_path_path(cls, project, database, document_path):
#         """Return a fully-qualified document_path string."""
#         return google.api_core.path_template.expand(
#             "projects/{project}/databases/{database}/documents/{document_path=**}",
#             project=project,
#             database=database,
#             document_path=document_path,
#         )

#     @classmethod
#     def document_root_path(cls, project, database):
#         """Return a fully-qualified document_root string."""
#         return google.api_core.path_template.expand(
#             "projects/{project}/databases/{database}/documents",
#             project=project,
#             database=database,
#         )'''

# )

# if n != 1:
#     raise Exception("Required replacement in firestore_admin_client.py not made.")

# TODO(busunkim): Remve during microgenerator transition
# Preserve parameter order
n = s.replace(
    "google/cloud/**/firestore_client.py",
    """def create_document\(
\s+self,
\s+parent,
\s+collection_id,
\s+document,
\s+document_id=None,
\s+mask=None,
\s+retry=google.api_core.gapic_v1.method.DEFAULT,
\s+timeout=google.api_core.gapic_v1.method.DEFAULT,
\s+metadata=None\):""",
"""def create_document(
        self,
        parent,
        collection_id,
        document_id,
        document,
        mask=None,
        retry=google.api_core.gapic_v1.method.DEFAULT,
        timeout=google.api_core.gapic_v1.method.DEFAULT,
        metadata=None):"""

)

if n != 2:
    raise Exception("Required replacement was not made in firestore_client.py")


# ----------------------------------------------------------------------------
# Generate firestore admin GAPIC layer
# ----------------------------------------------------------------------------
for version in admin_versions:
    library = gapic.py_library(
        service="firestore_admin",
        version=version,
        bazel_target=f"//google/firestore/admin/{version}:firestore-admin-{version}-py",
        include_protos=True,
    )
    s.move(library / f"google/cloud/firestore_admin_{version}")
    s.move(library / "tests")

    s.replace(
        f"google/cloud/firestore_admin_{version}/gapic/firestore_admin_client.py",
        "'google-cloud-firestore-admin'",
        "'google-cloud-firestore'",
    )

# TODO(busunkim): remove during microgenerator transition
# This re-adds a resource helper that was removed in a regeneration
n = s.replace("google/cloud/**/firestore_admin_client.py",
"""\s+def __init__\(""",
'''    @classmethod
    def parent_path(cls, project, database, collection_id):
        """Return a fully-qualified parent string."""
        return google.api_core.path_template.expand(
            "projects/{project}/databases/{database}/collectionGroups/{collection_id}",
            project=project,
            database=database,
            collection_id=collection_id,
        )

    def __init__('''

)

if n != 1:
    raise Exception("Required replacement was not made.")
# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------
templated_files = common.py_library(unit_cov_level=97, cov_level=99)
s.move(templated_files)

s.replace(
    "noxfile.py",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "FIRESTORE_APPLICATION_CREDENTIALS",
)

s.replace(
    "noxfile.py",
    '"--quiet", system_test',
    '"--verbose", system_test',
)


s.shell.run(["nox", "-s", "blacken"], hide_output=False)
