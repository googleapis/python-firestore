# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/cloud/firestore_admin_v1/proto/location.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.type import latlng_pb2 as google_dot_type_dot_latlng__pb2
from google.api import annotations_pb2 as google_dot_api_dot_annotations__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
    name="google/cloud/firestore_admin_v1/proto/location.proto",
    package="google.firestore.admin.v1",
    syntax="proto3",
    serialized_options=b"\n\035com.google.firestore.admin.v1B\rLocationProtoP\001Z>google.golang.org/genproto/googleapis/firestore/admin/v1;admin\242\002\004GCFS\252\002\037Google.Cloud.Firestore.Admin.V1\312\002\037Google\\Cloud\\Firestore\\Admin\\V1",
    serialized_pb=b'\n4google/cloud/firestore_admin_v1/proto/location.proto\x12\x19google.firestore.admin.v1\x1a\x18google/type/latlng.proto\x1a\x1cgoogle/api/annotations.proto"\x12\n\x10LocationMetadataB\xbb\x01\n\x1d\x63om.google.firestore.admin.v1B\rLocationProtoP\x01Z>google.golang.org/genproto/googleapis/firestore/admin/v1;admin\xa2\x02\x04GCFS\xaa\x02\x1fGoogle.Cloud.Firestore.Admin.V1\xca\x02\x1fGoogle\\Cloud\\Firestore\\Admin\\V1b\x06proto3',
    dependencies=[
        google_dot_type_dot_latlng__pb2.DESCRIPTOR,
        google_dot_api_dot_annotations__pb2.DESCRIPTOR,
    ],
)


_LOCATIONMETADATA = _descriptor.Descriptor(
    name="LocationMetadata",
    full_name="google.firestore.admin.v1.LocationMetadata",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=139,
    serialized_end=157,
)

DESCRIPTOR.message_types_by_name["LocationMetadata"] = _LOCATIONMETADATA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

LocationMetadata = _reflection.GeneratedProtocolMessageType(
    "LocationMetadata",
    (_message.Message,),
    {
        "DESCRIPTOR": _LOCATIONMETADATA,
        "__module__": "google.cloud.firestore_admin_v1.proto.location_pb2",
        "__doc__": """The metadata message for
  [google.cloud.location.Location.metadata][google.cloud.location.Location.metadata].
  
  """,
        # @@protoc_insertion_point(class_scope:google.firestore.admin.v1.LocationMetadata)
    },
)
_sym_db.RegisterMessage(LocationMetadata)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
