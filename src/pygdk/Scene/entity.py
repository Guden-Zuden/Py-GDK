from typing import (
    Optional as _Optional,
    Callable as _Callable,
    Sequence as _Sequence
)
import pygame as _pg

from ..base import *
from .. import profile as _profile
from . import base as _base
from .. import sprite as _sprite
from .. import animator as _animator
from .. import time as _time
from .. import event as _event
from . import attachments as _attachments
from . import collider as _collider

class Entity(_base.EntityBase):
    def __init__(
            self,
            x: float, 
            y: float,
            width: float, 
            height: float, 
            movement_model: _attachments.MovementModelBase,
            sprite: _sprite.Sprite, 
            animator: _Optional[_animator.EAnimator] = None, 
            collider: _Sequence[_collider.Collider] = (),
            callback_col_enter: _Optional[_Callable] = None,
            callback_col_stay: _Optional[_Callable] = None,
            callback_col_leave: _Optional[_Callable] = None,) -> None:
        super().__init__(x, y, width, height, movement_model, collider, callback_col_enter, callback_col_stay, callback_col_leave)
        self.sprite = sprite
        self.animator = animator

    def update(self):
        super().update()
        if self.animator:
            self.animator.update()

    def draw(self, view_position: Vec2):
        super().draw(view_position)
        if self.animator:
            self.sprite.draw(self.animator.get_index(), *(self.pos - view_position), anchor=Anchor.BOTTOM)
        else:
            self.sprite.draw(0, *(self.pos - view_position), anchor=Anchor.BOTTOM)
        if self.colliders:
            _pg.draw.rect(_profile.window.surface, (255,255,255), self.colliders.rect, 1)