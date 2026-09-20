from ..base import *
from . import base as _base
from .. import sprite as _sprite
from .. import animator as _animator
from .. import time as _time
from .. import event as _event
from . import attachments as _attachments

class Entity(_base.EntityBase):
    def __init__(
            self,
            x: float, y: float,
            width: float, height: float, movement_model: _attachments.MovementModelBase,
            sprite: _sprite.Sprite, animator: _animator.EAnimator) -> None:
        super().__init__(x, y, width, height, movement_model)
        self.sprite = sprite
        self.animator = animator

    def update(self):
        super().update()
        self.animator.update()

    def draw(self, view_position: Vec2):
        super().draw(view_position)
        self.sprite.draw(self.animator.get_index(), *(self.pos - view_position), anchor=Anchor.BOTTOM)