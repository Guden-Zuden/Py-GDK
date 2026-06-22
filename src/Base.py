from __future__ import annotations

from . import Profile
from .Log import *
from . import Time

from typing import Optional
from enum import Enum

# definition position type
class Pos:
    def __init__(self, x: int | float, y: int | float) -> None:
        self.x, self.y = x, y
    
    @property
    def pos(self):
        return (self.x, self.y)
    
    def __add__(self, other: Pos) -> Pos:
        return Pos(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: Pos) -> Pos:
        return Pos(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other: Pos) -> Pos:
        return Pos(self.x * other.x, self.y * other.y)
    
    def __truediv__(self, other: Pos) -> Pos:
        return Pos(self.x / other.x, self.y / other.y)
    
    def __str__(self) -> str:
        return f"x: {self.x} y: {self.y}"


# Component Base classes
class SceneComponentBase:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def update(self):
        pass

    def draw(self, offset_x: float, offset_y: float):
        pass

class LayerComponentBase:
    def __init__(self, u: float, v: float, width: float, height: float):
        self.u, self.v = u, v
        self.x = Profile.width/2 + Profile.width/2 * u - width/2
        self.y = Profile.height/2 + Profile.height/2 * v - height/2
        self.width, self.height = width, height

        self._attachments: list[AttachComponentBase] = []

    def attach(self, attachment: AttachComponentBase):
        self._attachments.append(attachment)
        attachment.component = self
        attachment.on_attach()
        return self

    def update(self):
        for attachment in self._attachments:
            attachment.update()
    
    def draw(self):
        """drawing centered position"""
        pass

class AttachComponentBase:
    def __init__(self) -> None:
        self.component: Optional[LayerComponentBase] = None
    
    def update(self) -> None: ...

    def on_attach(self) -> None: ...

class AnimBase:
    def __init__(self) -> None:
        self.start_x = 0.0
        self.start_y = 0.0
        self.dx = 0.0
        self.dy = 0.0
        self.isOutOfDate = False
        self.timer = Time.Timer()

    def reset(self) -> None:
        self.isOutOfDate = False
        self.timer.reset()

    def update(self) -> None: ...

class EasingBase:
    def __init__(self, dx: float, dy: float, dt: float) -> None:
        self.dx, self.dy = dx, dy
        self.dt = dt

    def update(self, timer: Time.Timer) -> tuple[float, float]: ...