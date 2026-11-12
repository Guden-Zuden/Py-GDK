from typing import TYPE_CHECKING

from ..base import *
from .. import profile as _profile
from ..time import Timer as _Timer
from . import attachments as _attachments

if TYPE_CHECKING:
    from . import collider as _collider

import pygame as _pg
from typing import (
    Optional as _Optional,
    Callable as _Callable
)

class EntityBase():
    def __init__(
            self, 
            x: float, 
            y: float, 
            width: float, 
            height: float, 
            movement_model: _Optional[_attachments.MovementModelBase] = None,
            collider: _Optional[_collider.Collider] = None,
            callback_col_enter: _Optional[_Callable] = None,
            callback_col_stay: _Optional[_Callable] = None,
            callback_col_leave: _Optional[_Callable] = None,
            ) -> None:
        self._timer = _Timer()
        self.pos = Vec2(x, y)
        self.velocity = Vec2(0, 0)

        self.size = Vec2(width, height)
        self.movement_model = movement_model
        self.colliders: list[_collider.Collider] = collider

        self.callback_col_enter: _Optional[_Callable] = callback_col_enter
        self.callback_col_stay: _Optional[_Callable] = callback_col_stay
        self.callback_col_leave: _Optional[_Callable] = callback_col_leave

    def update(self):
        self._timer.update()

        if self.movement_model:
            self.movement_model.velocity = self.velocity
            self.movement_model.update()
            vel = self.movement_model.velocity
            vel = self.movement_model.velocity.normalized * min(vel.distance(), self.movement_model.max_speed)
            # self.pos += vel * self._timer.delta_time
            # print(vel.distance())
        # self.pos += self.velocity * abs(self.velocity.normalized) * self._timer.delta_time
        
        self._timer.reset()


    def draw(self, view_position: Vec2):
        pass

    def get_rect(self) -> _pg.Rect:
        if self.colliders is None:
            raise Exception("No collider")

        return _pg.Rect(
            self.pos.x - self.colliders.width/2, 
            self.pos.y - self.colliders.height/2, 
            self.colliders.width, 
            self.colliders.height
            )

    def make_collision(self, type: _collider.ColliderType) -> _collider.Collider:
        from . import collider as _collider
        self.colliders = _collider.Collider(self, type)
        return self.colliders

__all__ = [
    "EntityBase",
]