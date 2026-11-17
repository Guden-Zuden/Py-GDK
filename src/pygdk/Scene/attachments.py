from .. import time as _time
from ..base import *
from .. import event as _event

from abc import (
    abstractmethod as _abstractmethod
)

class MovementModelBase:
    def __init__(self, accelaration: float, max_speed: float, brake: float) -> None:
        self.accelaration = accelaration
        self.max_speed = max_speed
        self.brake = brake
        self.velocity = Vec2(0, 0)

    @_abstractmethod
    def update(self) -> None:
        raise NotImplementedError("Subclasses must implement this method.")

class MovementModelPhysic(MovementModelBase):
    def update(self) -> None:
        self.velocity.x += _event.Input.horizontal * self.accelaration * _time.dt
        self.velocity.y += _event.Input.vertical * self.accelaration * _time.dt
        if _event.Input.horizontal == 0:
            if self.velocity.x > 0:
                self.velocity.x = max(0, self.velocity.x - self.brake * _time.dt)
            if self.velocity.x < 0:
                self.velocity.x = min(0, self.velocity.x + self.brake * _time.dt)
        if _event.Input.vertical == 0:
            if self.velocity.y > 0:
                self.velocity.y = max(0, self.velocity.y - self.brake * _time.dt)
            if self.velocity.y < 0:
                self.velocity.y = min(0, self.velocity.y + self.brake * _time.dt)

        self.velocity.x = max(-self.max_speed, min(self.max_speed, self.velocity.x))
        self.velocity.y = max(-self.max_speed, min(self.max_speed, self.velocity.y))

class MovementModelMob(MovementModelBase):
    """
    #### Parameters
        accelaration - This value don't be used this class.
        max_speed - This movement speed.

    """
    def update(self):
        # if self.velocity.x > 0:
        #     self.velocity.x = max(0, self.velocity.x - self.brake * _time.dt)
        # if self.velocity.x < 0:
        #     self.velocity.x = min(0, self.velocity.x + self.brake * _time.dt)
        # if self.velocity.y > 0:
        #     self.velocity.y = max(0, self.velocity.y - self.brake * _time.dt)
        # if self.velocity.y < 0:
        #     self.velocity.y = min(0, self.velocity.y + self.brake * _time.dt)
        pass

    def set_force(self, dx, dy):
        self.velocity.x = dx * self.max_speed
        self.velocity.y = dy * self.max_speed

    def add_force(self, dx, dy):
        self.velocity.x += dx * self.max_speed
        self.velocity.y += dy * self.max_speed