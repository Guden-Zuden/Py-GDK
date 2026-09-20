from .. import time as _time
from ..base import *
from .. import event as _event

class MovementModelBase:
    def __init__(self, accelaration: float, max_speed: float, brake: float) -> None:
        self.accelaration = accelaration
        self.max_speed = max_speed
        self.brake = brake
        self.velocity = Vec2(0, 0)
        self.timer = _time.Timer()

    def update(self) -> None:
        self.timer.update()

class MovementModelPhysic(MovementModelBase):
    def update(self) -> None:
        super().update()
        self.velocity.x += _event.Input.horizontal * self.accelaration * self.timer.delta_time
        self.velocity.y += _event.Input.vertical * self.accelaration * self.timer.delta_time
        if _event.Input.horizontal == 0:
            if self.velocity.x > 0:
                self.velocity.x = max(0, self.velocity.x - self.brake * self.timer.delta_time)
            if self.velocity.x < 0:
                self.velocity.x = min(0, self.velocity.x + self.brake * self.timer.delta_time)
        if _event.Input.vertical == 0:
            if self.velocity.y > 0:
                self.velocity.y = max(0, self.velocity.y - self.brake * self.timer.delta_time)
            if self.velocity.y < 0:
                self.velocity.y = min(0, self.velocity.y + self.brake * self.timer.delta_time)

        self.velocity.x = max(-self.max_speed, min(self.max_speed, self.velocity.x))
        self.velocity.y = max(-self.max_speed, min(self.max_speed, self.velocity.y))

# class MovementModelMob(MovementModelBase)