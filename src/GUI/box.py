from ..base import *
from .. import profile as _profile
from .. import colors as _colors
from . import base as _base

import pygame as _pg
from typing import Optional as _Optional

class Box(_base.GUIBase):
    def __init__(self, u: float, v: float, width: float, height: float,
                 color: gdk_color, padding = _profile.default_padding, border = Border(0, _colors.WHITE),
                 child: _Optional[_base.GUIBase] = None, no_register = False) -> None:
        super().__init__(u, v, width, height, padding, border, no_register)
        self.color = color if type(color) is Color else Color(*color)
        self.border = border

        self.child = child
        if self.child:
            self.child.pos = Vec2(
                self.width/2 - self.child.width/2,
                self.height/2 - self.child.height/2
            )

    def update(self):
        super().update()

    def draw(self, surface: _Optional[_pg.Surface] = None) -> None:
        super().draw(surface)

        _pg.draw.rect(self.surface, self.color, self.surface.get_rect())

        if self.child:
            self.child.pos = Vec2(
                self.width/2 - self.child.width/2,
                self.height/2 - self.child.height/2
            )

            self.child.draw(self.surface)

        if surface: self._flush(surface)
        else: self._flush()