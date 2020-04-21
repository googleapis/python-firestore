# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/cloud/firestore/admin_v1/proto/operation.proto

import sys

_b = sys.version_info[0] < 3 and (lambda x: x) or (lambda x: x.encode("latin1"))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.cloud.firestore_admin_v1.proto import (
    index_pb2 as google_dot_cloud_dot_firestore_dot_admin__v1_dot_proto_dot_index__pb2,
)
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.api import annotations_pb2 as google_dot_api_dot_annotations__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
    name="google/cloud/firestore/admin_v1/proto/operation.proto",
    package="google.firestore.admin.v1",
    syntax="proto3",
    serialized_options=_b(
        "\n\035com.google.firestore.admin.v1B\016OperationProtoP\001Z>google.golang.org/genproto/googleapis/firestore/admin/v1;admin\242\002\004GCFS\252\002\037Google.Cloud.Firestore.Admin.V1\312\002\037Google\\Cloud\\Firestore\\Admin\\V1"
    ),
    serialized_pb=_b(
        '\n5google/cloud/firestore/admin_v1/proto/operation.proto\x12\x19google.firestore.admin.v1\x1a\x31google/cloud/firestore/admin_v1/proto/index.proto\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1cgoogle/api/annotations.proto"\xbd\x02\n\x16IndexOperationMetadata\x12.\n\nstart_time\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12,\n\x08\x65nd_time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\r\n\x05index\x18\x03 \x01(\t\x12\x38\n\x05state\x18\x04 \x01(\x0e\x32).google.firestore.admin.v1.OperationState\x12?\n\x12progress_documents\x18\x05 \x01(\x0b\x32#.google.firestore.admin.v1.Progress\x12;\n\x0eprogress_bytes\x18\x06 \x01(\x0b\x32#.google.firestore.admin.v1.Progress"\x88\x05\n\x16\x46ieldOperationMetadata\x12.\n\nstart_time\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12,\n\x08\x65nd_time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\r\n\x05\x66ield\x18\x03 \x01(\t\x12_\n\x13index_config_deltas\x18\x04 \x03(\x0b\x32\x42.google.firestore.admin.v1.FieldOperationMetadata.IndexConfigDelta\x12\x38\n\x05state\x18\x05 \x01(\x0e\x32).google.firestore.admin.v1.OperationState\x12?\n\x12progress_documents\x18\x06 \x01(\x0b\x32#.google.firestore.admin.v1.Progress\x12;\n\x0eprogress_bytes\x18\x07 \x01(\x0b\x32#.google.firestore.admin.v1.Progress\x1a\xe7\x01\n\x10IndexConfigDelta\x12\x62\n\x0b\x63hange_type\x18\x01 \x01(\x0e\x32M.google.firestore.admin.v1.FieldOperationMetadata.IndexConfigDelta.ChangeType\x12/\n\x05index\x18\x02 \x01(\x0b\x32 .google.firestore.admin.v1.Index">\n\nChangeType\x12\x1b\n\x17\x43HANGE_TYPE_UNSPECIFIED\x10\x00\x12\x07\n\x03\x41\x44\x44\x10\x01\x12\n\n\x06REMOVE\x10\x02"\xec\x02\n\x17\x45xportDocumentsMetadata\x12.\n\nstart_time\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12,\n\x08\x65nd_time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x42\n\x0foperation_state\x18\x03 \x01(\x0e\x32).google.firestore.admin.v1.OperationState\x12?\n\x12progress_documents\x18\x04 \x01(\x0b\x32#.google.firestore.admin.v1.Progress\x12;\n\x0eprogress_bytes\x18\x05 \x01(\x0b\x32#.google.firestore.admin.v1.Progress\x12\x16\n\x0e\x63ollection_ids\x18\x06 \x03(\t\x12\x19\n\x11output_uri_prefix\x18\x07 \x01(\t"\xeb\x02\n\x17ImportDocumentsMetadata\x12.\n\nstart_time\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12,\n\x08\x65nd_time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x42\n\x0foperation_state\x18\x03 \x01(\x0e\x32).google.firestore.admin.v1.OperationState\x12?\n\x12progress_documents\x18\x04 \x01(\x0b\x32#.google.firestore.admin.v1.Progress\x12;\n\x0eprogress_bytes\x18\x05 \x01(\x0b\x32#.google.firestore.admin.v1.Progress\x12\x16\n\x0e\x63ollection_ids\x18\x06 \x03(\t\x12\x18\n\x10input_uri_prefix\x18\x07 \x01(\t"4\n\x17\x45xportDocumentsResponse\x12\x19\n\x11output_uri_prefix\x18\x01 \x01(\t":\n\x08Progress\x12\x16\n\x0e\x65stimated_work\x18\x01 \x01(\x03\x12\x16\n\x0e\x63ompleted_work\x18\x02 \x01(\x03*\x9e\x01\n\x0eOperationState\x12\x1f\n\x1bOPERATION_STATE_UNSPECIFIED\x10\x00\x12\x10\n\x0cINITIALIZING\x10\x01\x12\x0e\n\nPROCESSING\x10\x02\x12\x0e\n\nCANCELLING\x10\x03\x12\x0e\n\nFINALIZING\x10\x04\x12\x0e\n\nSUCCESSFUL\x10\x05\x12\n\n\x06\x46\x41ILED\x10\x06\x12\r\n\tCANCELLED\x10\x07\x42\xbc\x01\n\x1d\x63om.google.firestore.admin.v1B\x0eOperationProtoP\x01Z>google.golang.org/genproto/googleapis/firestore/admin/v1;admin\xa2\x02\x04GCFS\xaa\x02\x1fGoogle.Cloud.Firestore.Admin.V1\xca\x02\x1fGoogle\\Cloud\\Firestore\\Admin\\V1b\x06proto3'
    ),
    dependencies=[
        google_dot_cloud_dot_firestore_dot_admin__v1_dot_proto_dot_index__pb2.DESCRIPTOR,
        google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,
        google_dot_api_dot_annotations__pb2.DESCRIPTOR,
    ],
)

_OPERATIONSTATE = _descriptor.EnumDescriptor(
    name="OperationState",
    full_name="google.firestore.admin.v1.OperationState",
    filename=None,
    file=DESCRIPTOR,
    values=[
        _descriptor.EnumValueDescriptor(
            name="OPERATION_STATE_UNSPECIFIED",
            index=0,
            number=0,
            serialized_options=None,
            type=None,
        ),
        _descriptor.EnumValueDescriptor(
            name="INITIALIZING", index=1, number=1, serialized_options=None, type=None
        ),
        _descriptor.EnumValueDescriptor(
            name="PROCESSING", index=2, number=2, serialized_options=None, type=None
        ),
        _descriptor.EnumValueDescriptor(
            name="CANCELLING", index=3, number=3, serialized_options=None, type=None
        ),
        _descriptor.EnumValueDescriptor(
            name="FINALIZING", index=4, number=4, serialized_options=None, type=None
        ),
        _descriptor.EnumValueDescriptor(
            name="SUCCESSFUL", index=5, number=5, serialized_options=None, type=None
        ),
        _descriptor.EnumValueDescriptor(
            name="FAILED", index=6, number=6, serialized_options=None, type=None
        ),
        _descriptor.EnumValueDescriptor(
            name="CANCELLED", index=7, number=7, serialized_options=None, type=None
        ),
    ],
    containing_type=None,
    serialized_options=None,
    serialized_start=2017,
    serialized_end=2175,
)
_sym_db.RegisterEnumDescriptor(_OPERATIONSTATE)

OperationState = enum_type_wrapper.EnumTypeWrapper(_OPERATIONSTATE)
OPERATION_STATE_UNSPECIFIED = 0
INITIALIZING = 1
PROCESSING = 2
CANCELLING = 3
FINALIZING = 4
SUCCESSFUL = 5
FAILED = 6
CANCELLED = 7


_FIELDOPERATIONMETADATA_INDEXCONFIGDELTA_CHANGETYPE = _descriptor.EnumDescriptor(
    name="ChangeType",
    full_name="google.firestore.admin.v1.FieldOperationMetadata.IndexConfigDelta.ChangeType",
    filename=None,
    file=DESCRIPTOR,
    values=[
        _descriptor.EnumValueDescriptor(
            name="CHANGE_TYPE_UNSPECIFIED",
            index=0,
            number=0,
            serialized_options=None,
            type=None,
        ),
        _descriptor.EnumValueDescriptor(
            name="ADD", index=1, number=1, serialized_options=None, type=None
        ),
        _descriptor.EnumValueDescriptor(
            name="REMOVE", index=2, number=2, serialized_options=None, type=None
        ),
    ],
    containing_type=None,
    serialized_options=None,
    serialized_start=1105,
    serialized_end=1167,
)
_sym_db.RegisterEnumDescriptor(_FIELDOPERATIONMETADATA_INDEXCONFIGDELTA_CHANGETYPE)


_INDEXOPERATIONMETADATA = _descriptor.Descriptor(
    name="IndexOperationMetadata",
    full_name="google.firestore.admin.v1.IndexOperationMetadata",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name="start_time",
            full_name="google.firestore.admin.v1.IndexOperationMetadata.start_time",
            index=0,
            number=1,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="end_time",
            full_name="google.firestore.admin.v1.IndexOperationMetadata.end_time",
            index=1,
            number=2,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="index",
            full_name="google.firestore.admin.v1.IndexOperationMetadata.index",
            index=2,
            number=3,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=_b("").decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="state",
            full_name="google.firestore.admin.v1.IndexOperationMetadata.state",
            index=3,
            number=4,
            type=14,
            cpp_type=8,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="progress_documents",
            full_name="google.firestore.admin.v1.IndexOperationMetadata.progress_documents",
            index=4,
            number=5,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="progress_bytes",
            full_name="google.firestore.admin.v1.IndexOperationMetadata.progress_bytes",
            index=5,
            number=6,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=199,
    serialized_end=516,
)


_FIELDOPERATIONMETADATA_INDEXCONFIGDELTA = _descriptor.Descriptor(
    name="IndexConfigDelta",
    full_name="google.firestore.admin.v1.FieldOperationMetadata.IndexConfigDelta",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name="change_type",
            full_name="google.firestore.admin.v1.FieldOperationMetadata.IndexConfigDelta.change_type",
            index=0,
            number=1,
            type=14,
            cpp_type=8,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="index",
            full_name="google.firestore.admin.v1.FieldOperationMetadata.IndexConfigDelta.index",
            index=1,
            number=2,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[_FIELDOPERATIONMETADATA_INDEXCONFIGDELTA_CHANGETYPE],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=936,
    serialized_end=1167,
)

_FIELDOPERATIONMETADATA = _descriptor.Descriptor(
    name="FieldOperationMetadata",
    full_name="google.firestore.admin.v1.FieldOperationMetadata",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name="start_time",
            full_name="google.firestore.admin.v1.FieldOperationMetadata.start_time",
            index=0,
            number=1,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="end_time",
            full_name="google.firestore.admin.v1.FieldOperationMetadata.end_time",
            index=1,
            number=2,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="field",
            full_name="google.firestore.admin.v1.FieldOperationMetadata.field",
            index=2,
            number=3,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=_b("").decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="index_config_deltas",
            full_name="google.firestore.admin.v1.FieldOperationMetadata.index_config_deltas",
            index=3,
            number=4,
            type=11,
            cpp_type=10,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="state",
            full_name="google.firestore.admin.v1.FieldOperationMetadata.state",
            index=4,
            number=5,
            type=14,
            cpp_type=8,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="progress_documents",
            full_name="google.firestore.admin.v1.FieldOperationMetadata.progress_documents",
            index=5,
            number=6,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="progress_bytes",
            full_name="google.firestore.admin.v1.FieldOperationMetadata.progress_bytes",
            index=6,
            number=7,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
    ],
    extensions=[],
    nested_types=[_FIELDOPERATIONMETADATA_INDEXCONFIGDELTA],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=519,
    serialized_end=1167,
)


_EXPORTDOCUMENTSMETADATA = _descriptor.Descriptor(
    name="ExportDocumentsMetadata",
    full_name="google.firestore.admin.v1.ExportDocumentsMetadata",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name="start_time",
            full_name="google.firestore.admin.v1.ExportDocumentsMetadata.start_time",
            index=0,
            number=1,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="end_time",
            full_name="google.firestore.admin.v1.ExportDocumentsMetadata.end_time",
            index=1,
            number=2,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="operation_state",
            full_name="google.firestore.admin.v1.ExportDocumentsMetadata.operation_state",
            index=2,
            number=3,
            type=14,
            cpp_type=8,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="progress_documents",
            full_name="google.firestore.admin.v1.ExportDocumentsMetadata.progress_documents",
            index=3,
            number=4,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="progress_bytes",
            full_name="google.firestore.admin.v1.ExportDocumentsMetadata.progress_bytes",
            index=4,
            number=5,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="collection_ids",
            full_name="google.firestore.admin.v1.ExportDocumentsMetadata.collection_ids",
            index=5,
            number=6,
            type=9,
            cpp_type=9,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="output_uri_prefix",
            full_name="google.firestore.admin.v1.ExportDocumentsMetadata.output_uri_prefix",
            index=6,
            number=7,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=_b("").decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=1170,
    serialized_end=1534,
)


_IMPORTDOCUMENTSMETADATA = _descriptor.Descriptor(
    name="ImportDocumentsMetadata",
    full_name="google.firestore.admin.v1.ImportDocumentsMetadata",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name="start_time",
            full_name="google.firestore.admin.v1.ImportDocumentsMetadata.start_time",
            index=0,
            number=1,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="end_time",
            full_name="google.firestore.admin.v1.ImportDocumentsMetadata.end_time",
            index=1,
            number=2,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="operation_state",
            full_name="google.firestore.admin.v1.ImportDocumentsMetadata.operation_state",
            index=2,
            number=3,
            type=14,
            cpp_type=8,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="progress_documents",
            full_name="google.firestore.admin.v1.ImportDocumentsMetadata.progress_documents",
            index=3,
            number=4,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="progress_bytes",
            full_name="google.firestore.admin.v1.ImportDocumentsMetadata.progress_bytes",
            index=4,
            number=5,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="collection_ids",
            full_name="google.firestore.admin.v1.ImportDocumentsMetadata.collection_ids",
            index=5,
            number=6,
            type=9,
            cpp_type=9,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="input_uri_prefix",
            full_name="google.firestore.admin.v1.ImportDocumentsMetadata.input_uri_prefix",
            index=6,
            number=7,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=_b("").decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=1537,
    serialized_end=1900,
)


_EXPORTDOCUMENTSRESPONSE = _descriptor.Descriptor(
    name="ExportDocumentsResponse",
    full_name="google.firestore.admin.v1.ExportDocumentsResponse",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name="output_uri_prefix",
            full_name="google.firestore.admin.v1.ExportDocumentsResponse.output_uri_prefix",
            index=0,
            number=1,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=_b("").decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        )
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=1902,
    serialized_end=1954,
)


_PROGRESS = _descriptor.Descriptor(
    name="Progress",
    full_name="google.firestore.admin.v1.Progress",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name="estimated_work",
            full_name="google.firestore.admin.v1.Progress.estimated_work",
            index=0,
            number=1,
            type=3,
            cpp_type=2,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
        _descriptor.FieldDescriptor(
            name="completed_work",
            full_name="google.firestore.admin.v1.Progress.completed_work",
            index=1,
            number=2,
            type=3,
            cpp_type=2,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=1956,
    serialized_end=2014,
)

_INDEXOPERATIONMETADATA.fields_by_name[
    "start_time"
].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_INDEXOPERATIONMETADATA.fields_by_name[
    "end_time"
].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_INDEXOPERATIONMETADATA.fields_by_name["state"].enum_type = _OPERATIONSTATE
_INDEXOPERATIONMETADATA.fields_by_name["progress_documents"].message_type = _PROGRESS
_INDEXOPERATIONMETADATA.fields_by_name["progress_bytes"].message_type = _PROGRESS
_FIELDOPERATIONMETADATA_INDEXCONFIGDELTA.fields_by_name[
    "change_type"
].enum_type = _FIELDOPERATIONMETADATA_INDEXCONFIGDELTA_CHANGETYPE
_FIELDOPERATIONMETADATA_INDEXCONFIGDELTA.fields_by_name[
    "index"
].message_type = (
    google_dot_cloud_dot_firestore_dot_admin__v1_dot_proto_dot_index__pb2._INDEX
)
_FIELDOPERATIONMETADATA_INDEXCONFIGDELTA.containing_type = _FIELDOPERATIONMETADATA
_FIELDOPERATIONMETADATA_INDEXCONFIGDELTA_CHANGETYPE.containing_type = (
    _FIELDOPERATIONMETADATA_INDEXCONFIGDELTA
)
_FIELDOPERATIONMETADATA.fields_by_name[
    "start_time"
].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_FIELDOPERATIONMETADATA.fields_by_name[
    "end_time"
].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_FIELDOPERATIONMETADATA.fields_by_name[
    "index_config_deltas"
].message_type = _FIELDOPERATIONMETADATA_INDEXCONFIGDELTA
_FIELDOPERATIONMETADATA.fields_by_name["state"].enum_type = _OPERATIONSTATE
_FIELDOPERATIONMETADATA.fields_by_name["progress_documents"].message_type = _PROGRESS
_FIELDOPERATIONMETADATA.fields_by_name["progress_bytes"].message_type = _PROGRESS
_EXPORTDOCUMENTSMETADATA.fields_by_name[
    "start_time"
].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_EXPORTDOCUMENTSMETADATA.fields_by_name[
    "end_time"
].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_EXPORTDOCUMENTSMETADATA.fields_by_name["operation_state"].enum_type = _OPERATIONSTATE
_EXPORTDOCUMENTSMETADATA.fields_by_name["progress_documents"].message_type = _PROGRESS
_EXPORTDOCUMENTSMETADATA.fields_by_name["progress_bytes"].message_type = _PROGRESS
_IMPORTDOCUMENTSMETADATA.fields_by_name[
    "start_time"
].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_IMPORTDOCUMENTSMETADATA.fields_by_name[
    "end_time"
].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_IMPORTDOCUMENTSMETADATA.fields_by_name["operation_state"].enum_type = _OPERATIONSTATE
_IMPORTDOCUMENTSMETADATA.fields_by_name["progress_documents"].message_type = _PROGRESS
_IMPORTDOCUMENTSMETADATA.fields_by_name["progress_bytes"].message_type = _PROGRESS
DESCRIPTOR.message_types_by_name["IndexOperationMetadata"] = _INDEXOPERATIONMETADATA
DESCRIPTOR.message_types_by_name["FieldOperationMetadata"] = _FIELDOPERATIONMETADATA
DESCRIPTOR.message_types_by_name["ExportDocumentsMetadata"] = _EXPORTDOCUMENTSMETADATA
DESCRIPTOR.message_types_by_name["ImportDocumentsMetadata"] = _IMPORTDOCUMENTSMETADATA
DESCRIPTOR.message_types_by_name["ExportDocumentsResponse"] = _EXPORTDOCUMENTSRESPONSE
DESCRIPTOR.message_types_by_name["Progress"] = _PROGRESS
DESCRIPTOR.enum_types_by_name["OperationState"] = _OPERATIONSTATE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

IndexOperationMetadata = _reflection.GeneratedProtocolMessageType(
    "IndexOperationMetadata",
    (_message.Message,),
    dict(
        DESCRIPTOR=_INDEXOPERATIONMETADATA,
        __module__="google.cloud.firestore.admin_v1.proto.operation_pb2",
        __doc__="""Metadata for
  [google.longrunning.Operation][google.longrunning.Operation] results
  from [FirestoreAdmin.CreateIndex][google.firestore.admin.v1.FirestoreA
  dmin.CreateIndex].
  Attributes:
      start_time:
          The time this operation started.
      end_time:
          The time this operation completed. Will be unset if operation
          still in progress.
      index:
          The index resource that this operation is acting on. For
          example: ``projects/{project_id}/databases/{database_id}/colle
          ctionGroups/{collection_id}/indexes/{index_id}``
      state:
          The state of the operation.
      progress_documents:
          The progress, in documents, of this operation.
      progress_bytes:
          The progress, in bytes, of this operation.
  """,
        # @@protoc_insertion_point(class_scope:google.firestore.admin.v1.IndexOperationMetadata)
    ),
)
_sym_db.RegisterMessage(IndexOperationMetadata)

FieldOperationMetadata = _reflection.GeneratedProtocolMessageType(
    "FieldOperationMetadata",
    (_message.Message,),
    dict(
        IndexConfigDelta=_reflection.GeneratedProtocolMessageType(
            "IndexConfigDelta",
            (_message.Message,),
            dict(
                DESCRIPTOR=_FIELDOPERATIONMETADATA_INDEXCONFIGDELTA,
                __module__="google.cloud.firestore.admin_v1.proto.operation_pb2",
                __doc__="""Information about an index configuration change.
    Attributes:
        change_type:
            Specifies how the index is changing.
        index:
            The index being changed.
    """,
                # @@protoc_insertion_point(class_scope:google.firestore.admin.v1.FieldOperationMetadata.IndexConfigDelta)
            ),
        ),
        DESCRIPTOR=_FIELDOPERATIONMETADATA,
        __module__="google.cloud.firestore.admin_v1.proto.operation_pb2",
        __doc__="""Metadata for
  [google.longrunning.Operation][google.longrunning.Operation] results
  from [FirestoreAdmin.UpdateField][google.firestore.admin.v1.FirestoreA
  dmin.UpdateField].
  Attributes:
      start_time:
          The time this operation started.
      end_time:
          The time this operation completed. Will be unset if operation
          still in progress.
      field:
          The field resource that this operation is acting on. For
          example: ``projects/{project_id}/databases/{database_id}/colle
          ctionGroups/{collection_id}/fields/{field_path}``
      index_config_deltas:
          A list of [IndexConfigDelta][google.firestore.admin.v1.FieldOp
          erationMetadata.IndexConfigDelta], which describe the intent
          of this operation.
      state:
          The state of the operation.
      progress_documents:
          The progress, in documents, of this operation.
      progress_bytes:
          The progress, in bytes, of this operation.
  """,
        # @@protoc_insertion_point(class_scope:google.firestore.admin.v1.FieldOperationMetadata)
    ),
)
_sym_db.RegisterMessage(FieldOperationMetadata)
_sym_db.RegisterMessage(FieldOperationMetadata.IndexConfigDelta)

ExportDocumentsMetadata = _reflection.GeneratedProtocolMessageType(
    "ExportDocumentsMetadata",
    (_message.Message,),
    dict(
        DESCRIPTOR=_EXPORTDOCUMENTSMETADATA,
        __module__="google.cloud.firestore.admin_v1.proto.operation_pb2",
        __doc__="""Metadata for
  [google.longrunning.Operation][google.longrunning.Operation] results
  from [FirestoreAdmin.ExportDocuments][google.firestore.admin.v1.Firest
  oreAdmin.ExportDocuments].
  Attributes:
      start_time:
          The time this operation started.
      end_time:
          The time this operation completed. Will be unset if operation
          still in progress.
      operation_state:
          The state of the export operation.
      progress_documents:
          The progress, in documents, of this operation.
      progress_bytes:
          The progress, in bytes, of this operation.
      collection_ids:
          Which collection ids are being exported.
      output_uri_prefix:
          Where the entities are being exported to.
  """,
        # @@protoc_insertion_point(class_scope:google.firestore.admin.v1.ExportDocumentsMetadata)
    ),
)
_sym_db.RegisterMessage(ExportDocumentsMetadata)

ImportDocumentsMetadata = _reflection.GeneratedProtocolMessageType(
    "ImportDocumentsMetadata",
    (_message.Message,),
    dict(
        DESCRIPTOR=_IMPORTDOCUMENTSMETADATA,
        __module__="google.cloud.firestore.admin_v1.proto.operation_pb2",
        __doc__="""Metadata for
  [google.longrunning.Operation][google.longrunning.Operation] results
  from [FirestoreAdmin.ImportDocuments][google.firestore.admin.v1.Firest
  oreAdmin.ImportDocuments].
  Attributes:
      start_time:
          The time this operation started.
      end_time:
          The time this operation completed. Will be unset if operation
          still in progress.
      operation_state:
          The state of the import operation.
      progress_documents:
          The progress, in documents, of this operation.
      progress_bytes:
          The progress, in bytes, of this operation.
      collection_ids:
          Which collection ids are being imported.
      input_uri_prefix:
          The location of the documents being imported.
  """,
        # @@protoc_insertion_point(class_scope:google.firestore.admin.v1.ImportDocumentsMetadata)
    ),
)
_sym_db.RegisterMessage(ImportDocumentsMetadata)

ExportDocumentsResponse = _reflection.GeneratedProtocolMessageType(
    "ExportDocumentsResponse",
    (_message.Message,),
    dict(
        DESCRIPTOR=_EXPORTDOCUMENTSRESPONSE,
        __module__="google.cloud.firestore.admin_v1.proto.operation_pb2",
        __doc__="""Returned in the
  [google.longrunning.Operation][google.longrunning.Operation] response
  field.
  Attributes:
      output_uri_prefix:
          Location of the output files. This can be used to begin an
          import into Cloud Firestore (this project or another project)
          after the operation completes successfully.
  """,
        # @@protoc_insertion_point(class_scope:google.firestore.admin.v1.ExportDocumentsResponse)
    ),
)
_sym_db.RegisterMessage(ExportDocumentsResponse)

Progress = _reflection.GeneratedProtocolMessageType(
    "Progress",
    (_message.Message,),
    dict(
        DESCRIPTOR=_PROGRESS,
        __module__="google.cloud.firestore.admin_v1.proto.operation_pb2",
        __doc__="""Describes the progress of the operation. Unit of work is generic and
  must be interpreted based on where
  [Progress][google.firestore.admin.v1.Progress] is used.
  Attributes:
      estimated_work:
          The amount of work estimated.
      completed_work:
          The amount of work completed.
  """,
        # @@protoc_insertion_point(class_scope:google.firestore.admin.v1.Progress)
    ),
)
_sym_db.RegisterMessage(Progress)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
