from ..base import *
from .. import profile as _profile
from .. import colors as _colors
from .. import animator as _animator
from . import base as _base

import pygame as _pg
from typing import Optional as _Optional

class Box(_base.Element):
    def __init__(self, u: float, v: float, width: float, height: float,
                 color: gdk_color, padding = _profile.default_padding, border = Border(0, _colors.WHITE),
                 animator: _Optional[_animator.GAnimator] = None) -> None:
        super().__init__(u, v, width, height, padding, border, animator)
        self.color = color if type(color) is Color else Color(*color)

    def update(self):
        if not self.should_update(): return
        super().update()

    def draw(self) -> None:
        if not self.should_draw(): return
        super().draw()

        _pg.draw.rect(self.surface, self.color, self.surface.get_rect())
        self.reset_dirty()

    def set_color(self, color: gdk_color):
        self.color = color