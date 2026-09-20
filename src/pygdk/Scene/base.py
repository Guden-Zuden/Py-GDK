from ..base import *
from .. import profile as _profile
from ..time import Timer as _Timer
from . import attachments

from typing import (
    Optional as _Optional
)

class EntityBase:
    def __init__(self, x: float, y: float, width: float, height: float, movement_model: _Optional[attachments.MovementModelBase] = None) -> None:
        self._timer = _Timer()
        self.pos = Vec2(x, y)
        self.velocity = Vec2(0, 0)

        self.size = Vec2(width, height)
        self.movement_model = movement_model

    def update(self):
        self._timer.update()

        if self.movement_model:
            self.movement_model.velocity = self.velocity
            self.movement_model.update()
            self.pos += self.movement_model.velocity * abs(self.movement_model.velocity.normalized)
        # self.pos += self.velocity * abs(self.velocity.normalized) * self._timer.delta_time

        
        self._timer.reset()


    def draw(self, view_position: Vec2):
        pass

__all__ = [
    "EntityBase",
]