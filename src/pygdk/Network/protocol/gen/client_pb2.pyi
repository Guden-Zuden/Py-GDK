import pygdk.Network.protocol.gen.common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ClientState(_message.Message):
    __slots__ = ("curr_scene_name", "view_position", "view_size")
    CURR_SCENE_NAME_FIELD_NUMBER: _ClassVar[int]
    VIEW_POSITION_FIELD_NUMBER: _ClassVar[int]
    VIEW_SIZE_FIELD_NUMBER: _ClassVar[int]
    curr_scene_name: str
    view_position: _common_pb2.Vec2f
    view_size: _common_pb2.Vec2i
    def __init__(self, curr_scene_name: _Optional[str] = ..., view_position: _Optional[_Union[_common_pb2.Vec2f, _Mapping]] = ..., view_size: _Optional[_Union[_common_pb2.Vec2i, _Mapping]] = ...) -> None: ...
