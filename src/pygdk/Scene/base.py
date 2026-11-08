from typing import TYPE_CHECKING

from ..base import *
from .. import profile as _profile
from ..time import Timer as _Timer
from . import attachments as _attachments

if TYPE_CHECKING:
    from . import collider as _collider

import pygame as _pg
from typing import (
    Optional as _Optional
)

class EntityBase:
    def __init__(
            self, 
            x: float, 
            y: float, 
            width: float, 
            height: float, 
            movement_model: _Optional[_attachments.MovementModelBase] = None,
            collider: _Optional[_collider.Collider] = None) -> None:
        self._timer = _Timer()
        self.pos = Vec2(x, y)
        self.velocity = Vec2(0, 0)

        self.size = Vec2(width, height)
        self.movement_model = movement_model
        self.collider = collider

    def update(self):
        self._timer.update()

        if self.movement_model:
            self.movement_model.velocity = self.velocity
            self.movement_model.update()
            vel = self.movement_model.velocity
            vel = self.movement_model.velocity.normalized * min(vel.distance(), self.movement_model.max_speed)
            self.pos += vel * self._timer.delta_time
            print(vel.distance())
        # self.pos += self.velocity * abs(self.velocity.normalized) * self._timer.delta_time
        
        self._timer.reset()


    def draw(self, view_position: Vec2):
        pass

    def get_collider_rect(self) -> _pg.typing.RectLike:
        if self.collider is None:
            raise Exception("No collider")

        return (
            self.pos.x - self.collider.width/2, 
            self.pos.y - self.collider.height/2, 
            self.collider.width, 
            self.collider.height
            )

__all__ = [
    "EntityBase",
]