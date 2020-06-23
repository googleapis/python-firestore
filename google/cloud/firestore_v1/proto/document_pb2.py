# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/cloud/firestore_v1/proto/document.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.type import latlng_pb2 as google_dot_type_dot_latlng__pb2
from google.api import annotations_pb2 as google_dot_api_dot_annotations__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
    name="google/cloud/firestore_v1/proto/document.proto",
    package="google.firestore.v1",
    syntax="proto3",
    serialized_options=b"\n\027com.google.firestore.v1B\rDocumentProtoP\001Z<google.golang.org/genproto/googleapis/firestore/v1;firestore\242\002\004GCFS\252\002\031Google.Cloud.Firestore.V1\312\002\031Google\\Cloud\\Firestore\\V1",
    create_key=_descriptor._internal_create_key,
    serialized_pb=b'\n.google/cloud/firestore_v1/proto/document.proto\x12\x13google.firestore.v1\x1a\x1cgoogle/protobuf/struct.proto\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x18google/type/latlng.proto\x1a\x1cgoogle/api/annotations.proto"\x80\x02\n\x08\x44ocument\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x39\n\x06\x66ields\x18\x02 \x03(\x0b\x32).google.firestore.v1.Document.FieldsEntry\x12/\n\x0b\x63reate_time\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12/\n\x0bupdate_time\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x1aI\n\x0b\x46ieldsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12)\n\x05value\x18\x02 \x01(\x0b\x32\x1a.google.firestore.v1.Value:\x02\x38\x01"\xae\x03\n\x05Value\x12\x30\n\nnull_value\x18\x0b \x01(\x0e\x32\x1a.google.protobuf.NullValueH\x00\x12\x17\n\rboolean_value\x18\x01 \x01(\x08H\x00\x12\x17\n\rinteger_value\x18\x02 \x01(\x03H\x00\x12\x16\n\x0c\x64ouble_value\x18\x03 \x01(\x01H\x00\x12\x35\n\x0ftimestamp_value\x18\n \x01(\x0b\x32\x1a.google.protobuf.TimestampH\x00\x12\x16\n\x0cstring_value\x18\x11 \x01(\tH\x00\x12\x15\n\x0b\x62ytes_value\x18\x12 \x01(\x0cH\x00\x12\x19\n\x0freference_value\x18\x05 \x01(\tH\x00\x12.\n\x0fgeo_point_value\x18\x08 \x01(\x0b\x32\x13.google.type.LatLngH\x00\x12\x36\n\x0b\x61rray_value\x18\t \x01(\x0b\x32\x1f.google.firestore.v1.ArrayValueH\x00\x12\x32\n\tmap_value\x18\x06 \x01(\x0b\x32\x1d.google.firestore.v1.MapValueH\x00\x42\x0c\n\nvalue_type"8\n\nArrayValue\x12*\n\x06values\x18\x01 \x03(\x0b\x32\x1a.google.firestore.v1.Value"\x90\x01\n\x08MapValue\x12\x39\n\x06\x66ields\x18\x01 \x03(\x0b\x32).google.firestore.v1.MapValue.FieldsEntry\x1aI\n\x0b\x46ieldsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12)\n\x05value\x18\x02 \x01(\x0b\x32\x1a.google.firestore.v1.Value:\x02\x38\x01\x42\xa7\x01\n\x17\x63om.google.firestore.v1B\rDocumentProtoP\x01Z<google.golang.org/genproto/googleapis/firestore/v1;firestore\xa2\x02\x04GCFS\xaa\x02\x19Google.Cloud.Firestore.V1\xca\x02\x19Google\\Cloud\\Firestore\\V1b\x06proto3',
    dependencies=[
        google_dot_protobuf_dot_struct__pb2.DESCRIPTOR,
        google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,
        google_dot_type_dot_latlng__pb2.DESCRIPTOR,
        google_dot_api_dot_annotations__pb2.DESCRIPTOR,
    ],
)


_DOCUMENT_FIELDSENTRY = _descriptor.Descriptor(
    name="FieldsEntry",
    full_name="google.firestore.v1.Document.FieldsEntry",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="key",
            full_name="google.firestore.v1.Document.FieldsEntry.key",
            index=0,
            number=1,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="value",
            full_name="google.firestore.v1.Document.FieldsEntry.value",
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
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=b"8\001",
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=374,
    serialized_end=447,
)

_DOCUMENT = _descriptor.Descriptor(
    name="Document",
    full_name="google.firestore.v1.Document",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="name",
            full_name="google.firestore.v1.Document.name",
            index=0,
            number=1,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="fields",
            full_name="google.firestore.v1.Document.fields",
            index=1,
            number=2,
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
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="create_time",
            full_name="google.firestore.v1.Document.create_time",
            index=2,
            number=3,
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
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="update_time",
            full_name="google.firestore.v1.Document.update_time",
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
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[_DOCUMENT_FIELDSENTRY],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=191,
    serialized_end=447,
)


_VALUE = _descriptor.Descriptor(
    name="Value",
    full_name="google.firestore.v1.Value",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="null_value",
            full_name="google.firestore.v1.Value.null_value",
            index=0,
            number=11,
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
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="boolean_value",
            full_name="google.firestore.v1.Value.boolean_value",
            index=1,
            number=1,
            type=8,
            cpp_type=7,
            label=1,
            has_default_value=False,
            default_value=False,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="integer_value",
            full_name="google.firestore.v1.Value.integer_value",
            index=2,
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
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="double_value",
            full_name="google.firestore.v1.Value.double_value",
            index=3,
            number=3,
            type=1,
            cpp_type=5,
            label=1,
            has_default_value=False,
            default_value=float(0),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="timestamp_value",
            full_name="google.firestore.v1.Value.timestamp_value",
            index=4,
            number=10,
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
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="string_value",
            full_name="google.firestore.v1.Value.string_value",
            index=5,
            number=17,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="bytes_value",
            full_name="google.firestore.v1.Value.bytes_value",
            index=6,
            number=18,
            type=12,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"",
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="reference_value",
            full_name="google.firestore.v1.Value.reference_value",
            index=7,
            number=5,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="geo_point_value",
            full_name="google.firestore.v1.Value.geo_point_value",
            index=8,
            number=8,
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
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="array_value",
            full_name="google.firestore.v1.Value.array_value",
            index=9,
            number=9,
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
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="map_value",
            full_name="google.firestore.v1.Value.map_value",
            index=10,
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
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[
        _descriptor.OneofDescriptor(
            name="value_type",
            full_name="google.firestore.v1.Value.value_type",
            index=0,
            containing_type=None,
            create_key=_descriptor._internal_create_key,
            fields=[],
        )
    ],
    serialized_start=450,
    serialized_end=880,
)


_ARRAYVALUE = _descriptor.Descriptor(
    name="ArrayValue",
    full_name="google.firestore.v1.ArrayValue",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="values",
            full_name="google.firestore.v1.ArrayValue.values",
            index=0,
            number=1,
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
            create_key=_descriptor._internal_create_key,
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
    serialized_start=882,
    serialized_end=938,
)


_MAPVALUE_FIELDSENTRY = _descriptor.Descriptor(
    name="FieldsEntry",
    full_name="google.firestore.v1.MapValue.FieldsEntry",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="key",
            full_name="google.firestore.v1.MapValue.FieldsEntry.key",
            index=0,
            number=1,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="value",
            full_name="google.firestore.v1.MapValue.FieldsEntry.value",
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
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=b"8\001",
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=374,
    serialized_end=447,
)

_MAPVALUE = _descriptor.Descriptor(
    name="MapValue",
    full_name="google.firestore.v1.MapValue",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="fields",
            full_name="google.firestore.v1.MapValue.fields",
            index=0,
            number=1,
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
            create_key=_descriptor._internal_create_key,
        )
    ],
    extensions=[],
    nested_types=[_MAPVALUE_FIELDSENTRY],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=941,
    serialized_end=1085,
)

_DOCUMENT_FIELDSENTRY.fields_by_name["value"].message_type = _VALUE
_DOCUMENT_FIELDSENTRY.containing_type = _DOCUMENT
_DOCUMENT.fields_by_name["fields"].message_type = _DOCUMENT_FIELDSENTRY
_DOCUMENT.fields_by_name[
    "create_time"
].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_DOCUMENT.fields_by_name[
    "update_time"
].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_VALUE.fields_by_name[
    "null_value"
].enum_type = google_dot_protobuf_dot_struct__pb2._NULLVALUE
_VALUE.fields_by_name[
    "timestamp_value"
].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_VALUE.fields_by_name[
    "geo_point_value"
].message_type = google_dot_type_dot_latlng__pb2._LATLNG
_VALUE.fields_by_name["array_value"].message_type = _ARRAYVALUE
_VALUE.fields_by_name["map_value"].message_type = _MAPVALUE
_VALUE.oneofs_by_name["value_type"].fields.append(_VALUE.fields_by_name["null_value"])
_VALUE.fields_by_name["null_value"].containing_oneof = _VALUE.oneofs_by_name[
    "value_type"
]
_VALUE.oneofs_by_name["value_type"].fields.append(
    _VALUE.fields_by_name["boolean_value"]
)
_VALUE.fields_by_name["boolean_value"].containing_oneof = _VALUE.oneofs_by_name[
    "value_type"
]
_VALUE.oneofs_by_name["value_type"].fields.append(
    _VALUE.fields_by_name["integer_value"]
)
_VALUE.fields_by_name["integer_value"].containing_oneof = _VALUE.oneofs_by_name[
    "value_type"
]
_VALUE.oneofs_by_name["value_type"].fields.append(_VALUE.fields_by_name["double_value"])
_VALUE.fields_by_name["double_value"].containing_oneof = _VALUE.oneofs_by_name[
    "value_type"
]
_VALUE.oneofs_by_name["value_type"].fields.append(
    _VALUE.fields_by_name["timestamp_value"]
)
_VALUE.fields_by_name["timestamp_value"].containing_oneof = _VALUE.oneofs_by_name[
    "value_type"
]
_VALUE.oneofs_by_name["value_type"].fields.append(_VALUE.fields_by_name["string_value"])
_VALUE.fields_by_name["string_value"].containing_oneof = _VALUE.oneofs_by_name[
    "value_type"
]
_VALUE.oneofs_by_name["value_type"].fields.append(_VALUE.fields_by_name["bytes_value"])
_VALUE.fields_by_name["bytes_value"].containing_oneof = _VALUE.oneofs_by_name[
    "value_type"
]
_VALUE.oneofs_by_name["value_type"].fields.append(
    _VALUE.fields_by_name["reference_value"]
)
_VALUE.fields_by_name["reference_value"].containing_oneof = _VALUE.oneofs_by_name[
    "value_type"
]
_VALUE.oneofs_by_name["value_type"].fields.append(
    _VALUE.fields_by_name["geo_point_value"]
)
_VALUE.fields_by_name["geo_point_value"].containing_oneof = _VALUE.oneofs_by_name[
    "value_type"
]
_VALUE.oneofs_by_name["value_type"].fields.append(_VALUE.fields_by_name["array_value"])
_VALUE.fields_by_name["array_value"].containing_oneof = _VALUE.oneofs_by_name[
    "value_type"
]
_VALUE.oneofs_by_name["value_type"].fields.append(_VALUE.fields_by_name["map_value"])
_VALUE.fields_by_name["map_value"].containing_oneof = _VALUE.oneofs_by_name[
    "value_type"
]
_ARRAYVALUE.fields_by_name["values"].message_type = _VALUE
_MAPVALUE_FIELDSENTRY.fields_by_name["value"].message_type = _VALUE
_MAPVALUE_FIELDSENTRY.containing_type = _MAPVALUE
_MAPVALUE.fields_by_name["fields"].message_type = _MAPVALUE_FIELDSENTRY
DESCRIPTOR.message_types_by_name["Document"] = _DOCUMENT
DESCRIPTOR.message_types_by_name["Value"] = _VALUE
DESCRIPTOR.message_types_by_name["ArrayValue"] = _ARRAYVALUE
DESCRIPTOR.message_types_by_name["MapValue"] = _MAPVALUE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Document = _reflection.GeneratedProtocolMessageType(
    "Document",
    (_message.Message,),
    {
        "FieldsEntry": _reflection.GeneratedProtocolMessageType(
            "FieldsEntry",
            (_message.Message,),
            {
                "DESCRIPTOR": _DOCUMENT_FIELDSENTRY,
                "__module__": "google.cloud.firestore_v1.proto.document_pb2"
                # @@protoc_insertion_point(class_scope:google.firestore.v1.Document.FieldsEntry)
            },
        ),
        "DESCRIPTOR": _DOCUMENT,
        "__module__": "google.cloud.firestore_v1.proto.document_pb2",
        "__doc__": """A Firestore document.  Must not exceed 1 MiB - 4 bytes.
  Attributes:
      name:
          The resource name of the document, for example ``projects/{pro
          ject_id}/databases/{database_id}/documents/{document_path}``.
      fields:
          The document’s fields.  The map keys represent field names.  A
          simple field name contains only characters ``a`` to ``z``,
          ``A`` to ``Z``, ``0`` to ``9``, or ``_``, and must not start
          with ``0`` to ``9``. For example, ``foo_bar_17``.  Field names
          matching the regular expression ``__.*__`` are reserved.
          Reserved field names are forbidden except in certain
          documented contexts. The map keys, represented as UTF-8, must
          not exceed 1,500 bytes and cannot be empty.  Field paths may
          be used in other contexts to refer to structured fields
          defined here. For ``map_value``, the field path is represented
          by the simple or quoted field names of the containing fields,
          delimited by ``.``. For example, the structured field ``"foo"
          : { map_value: { "x&y" : { string_value: "hello" }}}`` would
          be represented by the field path ``foo.x&y``.  Within a field
          path, a quoted field name starts and ends with :literal:`\``
          and may contain any character. Some characters, including
          :literal:`\``, must be escaped using a ``\``. For example,
          :literal:`\`x&y\`` represents ``x&y`` and
          :literal:`\`bak\`tik\`` represents :literal:`bak`tik`.
      create_time:
          Output only. The time at which the document was created.  This
          value increases monotonically when a document is deleted then
          recreated. It can also be compared to values from other
          documents and the ``read_time`` of a query.
      update_time:
          Output only. The time at which the document was last changed.
          This value is initially set to the ``create_time`` then
          increases monotonically with each change to the document. It
          can also be compared to values from other documents and the
          ``read_time`` of a query.
  """,
        # @@protoc_insertion_point(class_scope:google.firestore.v1.Document)
    },
)
_sym_db.RegisterMessage(Document)
_sym_db.RegisterMessage(Document.FieldsEntry)

Value = _reflection.GeneratedProtocolMessageType(
    "Value",
    (_message.Message,),
    {
        "DESCRIPTOR": _VALUE,
        "__module__": "google.cloud.firestore_v1.proto.document_pb2",
        "__doc__": """A message that can hold any of the supported value types.
  Attributes:
      value_type:
          Must have a value set.
      null_value:
          A null value.
      boolean_value:
          A boolean value.
      integer_value:
          An integer value.
      double_value:
          A double value.
      timestamp_value:
          A timestamp value.  Precise only to microseconds. When stored,
          any additional precision is rounded down.
      string_value:
          A string value.  The string, represented as UTF-8, must not
          exceed 1 MiB - 89 bytes. Only the first 1,500 bytes of the
          UTF-8 representation are considered by queries.
      bytes_value:
          A bytes value.  Must not exceed 1 MiB - 89 bytes. Only the
          first 1,500 bytes are considered by queries.
      reference_value:
          A reference to a document. For example: ``projects/{project_id
          }/databases/{database_id}/documents/{document_path}``.
      geo_point_value:
          A geo point value representing a point on the surface of
          Earth.
      array_value:
          An array value.  Cannot directly contain another array value,
          though can contain an map which contains another array.
      map_value:
          A map value.
  """,
        # @@protoc_insertion_point(class_scope:google.firestore.v1.Value)
    },
)
_sym_db.RegisterMessage(Value)

ArrayValue = _reflection.GeneratedProtocolMessageType(
    "ArrayValue",
    (_message.Message,),
    {
        "DESCRIPTOR": _ARRAYVALUE,
        "__module__": "google.cloud.firestore_v1.proto.document_pb2",
        "__doc__": """An array value.
  Attributes:
      values:
          Values in the array.
  """,
        # @@protoc_insertion_point(class_scope:google.firestore.v1.ArrayValue)
    },
)
_sym_db.RegisterMessage(ArrayValue)

MapValue = _reflection.GeneratedProtocolMessageType(
    "MapValue",
    (_message.Message,),
    {
        "FieldsEntry": _reflection.GeneratedProtocolMessageType(
            "FieldsEntry",
            (_message.Message,),
            {
                "DESCRIPTOR": _MAPVALUE_FIELDSENTRY,
                "__module__": "google.cloud.firestore_v1.proto.document_pb2"
                # @@protoc_insertion_point(class_scope:google.firestore.v1.MapValue.FieldsEntry)
            },
        ),
        "DESCRIPTOR": _MAPVALUE,
        "__module__": "google.cloud.firestore_v1.proto.document_pb2",
        "__doc__": """A map value.
  Attributes:
      fields:
          The map’s fields.  The map keys represent field names. Field
          names matching the regular expression ``__.*__`` are reserved.
          Reserved field names are forbidden except in certain
          documented contexts. The map keys, represented as UTF-8, must
          not exceed 1,500 bytes and cannot be empty.
  """,
        # @@protoc_insertion_point(class_scope:google.firestore.v1.MapValue)
    },
)
_sym_db.RegisterMessage(MapValue)
_sym_db.RegisterMessage(MapValue.FieldsEntry)


DESCRIPTOR._options = None
_DOCUMENT_FIELDSENTRY._options = None
_MAPVALUE_FIELDSENTRY._options = None
# @@protoc_insertion_point(module_scope)
