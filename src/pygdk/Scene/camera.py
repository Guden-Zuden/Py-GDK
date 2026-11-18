from ..base import *
from . import base as _base
from .. import profile as _profile
from .. import scene as _scene
from .. import time as _time
from . import entity as _entity

import pygame as _pg
from typing import (
    Optional as _Optional
)

class Camera(_base.EntityBase):
    def __init__(self, name: str, x: float, y: float, smoothing: float = 1.0) -> None:
        super().__init__(x, y, 0, 0)
        self.name = name
        self.surface = _pg.Surface(_profile.window.surface.get_size()) # pyright: ignore
        self.following_entity: _Optional[_entity.Entity] = None
        self.smoothing = smoothing # fraction of remaining distance per 1/60 second

    def update(self):
        if self.following_entity:
            alpha = 1 - (1 - self.smoothing) ** (_time.dt * 60)
            self.pos += (self.following_entity.pos - self.pos) * alpha

    def follow(self, entity: _entity.Entity):
        self.following_entity = entity