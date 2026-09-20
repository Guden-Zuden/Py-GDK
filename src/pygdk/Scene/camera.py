from ..base import *
from . import base as _base
from .. import profile as _profile
from .. import scene as _scene
from . import entity as _entity

import pygame as _pg
from typing import (
    Optional as _Optional
)

class Camera(_base.EntityBase):
    def __init__(self, name: str, x: float, y: float, smoothing: float = 1.0) -> None:
        super().__init__(x, y, 0, 0)
        self.name = name
        self.surface = _pg.Surface(_profile.window.surface.get_size())
        self.following_entity: _Optional[_entity.Entity] = None
        self.smoothing = smoothing # 0~1

    def update(self):
        if self.following_entity: self.pos += (self.following_entity.pos - self.pos) * self.smoothing

    def follow(self, entity: _entity.Entity):
        self.following_entity = entity