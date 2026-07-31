import pygame as _pg
from typing import Optional

from ..base import *
from . import base
from .. import profile
from .. import colors

class VerticalAlignContainer(base.GUIBase):
    def __init__(self, u: float, v: float, width: float, height: float, 
                 padding = profile.default_padding, items: list[base.GUIBase] = [],
                 space: float = 0, border: Border = Border(0, colors.WHITE),  no_register = False) -> None:
        super().__init__(u, v, width, height, padding, border, no_register)
        self.items = items
        self.surface = _pg.Surface([self.width * profile.surface_scale, self.height * profile.surface_scale])
        self.space = 0
        self.border = border

        self._scrollable = False
    
    def update(self):
        super().update()
        for item in self.items:
            item._reset_flag()
            item.update()

    def draw(self, surface: Optional[_pg.Surface] = None):
        super().draw(surface)
        x = self.padding.left + self.border.width
        y = self.padding.top + self.border.width

        for item in self.items:
            item.pos = Vec2(x, y)
            item.draw(self.surface)
            y += item.height + item.padding.top + item.padding.bottom + self.space

        if y > self.height:
            self._scrollable = True
        else:
            self._scrollable = False

        self._flush()

    def pushItem(self, item: base.GUIBase):
        self.items.append(item)

class HorizontalAlignContainer(base.GUIBase):
    def __init__(self, u: float, v: float, width: float, height: float,
                 padding = profile.default_padding, items: list[base.GUIBase] = [],
                 space: float = 0, border: Border = Border(0, colors.WHITE), no_register = False) -> None:
        super().__init__(u, v, width, height, padding, border, no_register)
        self.items = items
        self.surface = _pg.Surface([self.width * profile.surface_scale, self.height * profile.surface_scale])
        self.space = space
        self.border = border

        self._scrollable = False

    def update(self):
        super().update()
        for item in self.items:
            item._reset_flag()
            item.update()

    def draw(self, surface: Optional[_pg.Surface] = None):
        super().draw(surface)
        x = self.padding.left + self.border.width
        y = self.padding.top + self.border.width

        for item in self.items:
            item.pos = Vec2(x, y)
            item.draw(self.surface)
            x += item.width + item.padding.left + item.padding.right + self.space

        if x > self.width:
            self._scrollable = True
        else:
            self._scrollable = False

        self._flush()

class GridContainer(base.GUIBase):
    def __init__(self, u: float, v: float, width: float, height: float,
                 padding = profile.default_padding, border: Border = Border(0, colors.WHITE), no_register = False) -> None:
        super().__init__(u, v, width, height, padding, border, no_register)
        self.border = border
        # TODO