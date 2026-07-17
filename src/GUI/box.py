from ..base import *
from .. import profile
from .. import colors
from . import base

import pygame as _pg

class Box(base.GUIBase):
    def __init__(self, u: float, v: float, width: float, height: float,
                 color: gdk_color, border = Border(0, colors.WHITE), padding = profile.default_padding,
                 child: Optional[base.GUIBase] = None) -> None:
        super().__init__(u, v, width, height, padding)
        self.color = color if type(color) is Color else Color(*color)
        self.border = border

        self.child = child

    def draw(self, surface: Optional[_pg.Surface] = None) -> None:
        if surface is None: surface = profile.surface

        if self.border.width > 0:
            rect = self.get_rect()
            rect.x -= self.border.width
            rect.y -= self.border.width
            rect.width += self.border.width*2
            rect.height += self.border.width*2
            _pg.draw.rect(surface, self.border.color, rect, int(self.border.width))

        _pg.draw.rect(surface, self.color, self.get_rect())

        if self.child:
            self.child.pos = Vec2(self.pos.x + self.width/2, self.pos.y + self.height/2)
            self.child._centering()

            self.child.draw()