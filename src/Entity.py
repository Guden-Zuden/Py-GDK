from . import Profile
from . import Components
from . import Sprite
from . import Utils
from . import Event
from . import Timer
from . import Animator

import pygame as _pygame
from typing import Optional

class MovementModelBase:
    def __init__(self, accelaration: float, max_speed: float, friction: float) -> None:
        self.accelaration = accelaration
        self.max_speed = max_speed
        self.friction = friction
        self.vx = 0
        self.vy = 0
        self.timer = Timer.Timer()

    def update(self) -> None:
        self.timer.update()

class PhysicMoventModel(MovementModelBase):
    def __init__(self, accelaration: float, max_speed: float, friction: float) -> None:
        super().__init__(accelaration, max_speed, friction)

    def update(self) -> None:
        super().update()
        self.vx += Event.Input.horizontal * self.accelaration * self.timer.deltaTime
        self.vy += Event.Input.vertical * self.accelaration * self.timer.deltaTime
        if Event.Input.horizontal == 0:
            if self.vx > 0:
                self.vx = max(0, self.vx - self.friction * self.timer.deltaTime)
            if self.vx < 0:
                self.vx = min(0, self.vx + self.friction * self.timer.deltaTime)
        if Event.Input.vertical == 0:
            if self.vy > 0:
                self.vy = max(0, self.vy - self.friction * self.timer.deltaTime)
            if self.vy < 0:
                self.vy = min(0, self.vy + self.friction * self.timer.deltaTime)

        self.vx = max(-self.max_speed, min(self.max_speed, self.vx))
        self.vy = max(-self.max_speed, min(self.max_speed, self.vy))

class InstantMovementModel(MovementModelBase):
    def __init__(self, accelaration: float, max_speed: float, friction: float) -> None:
        super().__init__(accelaration, max_speed, friction)

    def update(self) -> None:
        super().update()
        self.vx = Event.Input.horizontal * self.max_speed
        self.vy = Event.Input.vertical * self.max_speed

class MobMovementModel(MovementModelBase):
    def __init__(self, accelaration: float, max_speed: float, friction: float) -> None:
        super().__init__(accelaration, max_speed, friction)
        self.horizontal = 0
        self.vertical = 0

    def update(self) -> None:
        super().update()
        self.vx = self.horizontal * self.max_speed
        self.vy = self.vertical * self.max_speed

    def move(self, horizontal: int, vertical: int):
        self.horizontal = horizontal / abs(horizontal)
        self.vertical = vertical / abs(vertical)

class DisabledMovementModel(MovementModelBase):
    def __init__(self, accelaration: float, max_speed: float, friction: float) -> None:
        super().__init__(accelaration, max_speed, friction)

    def update(self) -> None:
        pass

class Entity(Components.ComponentBase):
    def __init__(self, x: float, y: float, sprite: Sprite.Sprite, movement_model: MovementModelBase, animator: Optional[Animator] = None) -> None:
        super().__init__(x, y)
        self.vx: float = 0
        self.vy: float = 0
        self.sprite: Sprite.Sprite = sprite
        self.movement_model = movement_model
        self.animator: Optional[Animator] = animator
    
    def update(self):
        self.movement_model.update()
        self.vx = self.movement_model.vx
        self.vy = self.movement_model.vy
        self.x += self.vx
        self.y += self.vy
        if self.animator:
            self.animator.update()

    def draw(self, offset_x: float, offset_y: float):
        assert Profile.screen is not None
        
        x, y = self.x - offset_x, self.y - offset_y

        # _pygame.draw.rect(Profile.screen, (255,255,255), _pygame.Rect(self.x, self.y, 20, 20))
        if self.animator:
            self.sprite.draw(self.animator.get_frame(), x, y, anchor=Utils.Anchor.bottom)
        else:
            self.sprite.draw(0, x, y, anchor=Utils.Anchor.bottom)