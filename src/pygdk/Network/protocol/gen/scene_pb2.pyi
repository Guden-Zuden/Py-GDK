import pygdk.Network.protocol.gen.common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EntityState(_message.Message):
    __slots__ = ("type", "id", "position", "velocity", "current_anim", "anim_index")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    VELOCITY_FIELD_NUMBER: _ClassVar[int]
    CURRENT_ANIM_FIELD_NUMBER: _ClassVar[int]
    ANIM_INDEX_FIELD_NUMBER: _ClassVar[int]
    type: str
    id: int
    position: _common_pb2.Vec2f
    velocity: _common_pb2.Vec2f
    current_anim: str
    anim_index: int
    def __init__(self, type: _Optional[str] = ..., id: _Optional[int] = ..., position: _Optional[_Union[_common_pb2.Vec2f, _Mapping]] = ..., velocity: _Optional[_Union[_common_pb2.Vec2f, _Mapping]] = ..., current_anim: _Optional[str] = ..., anim_index: _Optional[int] = ...) -> None: ...

class SceneState(_message.Message):
    __slots__ = ("entitystates",)
    ENTITYSTATES_FIELD_NUMBER: _ClassVar[int]
    entitystates: _containers.RepeatedCompositeFieldContainer[EntityState]
    def __init__(self, entitystates: _Optional[_Iterable[_Union[EntityState, _Mapping]]] = ...) -> None: ...
