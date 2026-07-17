import pygame as _pg
from typing import Optional

from ..base import *
from . import base
from .. import profile

class VerticalAlignContainer(base.GUIBase):
    def __init__(self, u: float, v: float, width: float, height: float, 
                 padding = profile.default_padding, items: list[base.GUIBase] = [],
                 space: float = 0) -> None:
        super().__init__(u, v, width, height, padding)
        self.items = items
        self.surface = _pg.Surface([self.width, self.height]) # TODO: 範囲外は描画しないようにする
        self.space = 0
    
    def update(self):
        for item in self.items:
            item._reset_flag()
            item.update()

    def draw(self, surface: Optional[_pg.Surface] = None):
        y = self.pos.y
        for item in self.items:
            item.pos.x, item.pos.y = self.pos.x, y
            item.draw(surface)
            y += item.height + item.padding.top + item.padding.bottom + self.space

    def pushItem(self, item: base.GUIBase):
        self.items.append(item)

class HorizontalAlignContainer(base.GUIBase):
    def __init__(self, u: float, v: float, width: float, height: float,
                 padding = profile.default_padding, items: list[base.GUIBase] = [],
                 space: float = 0) -> None:
        super().__init__(u, v, width, height, padding)
        self.items = items
        
        self.space = space

    def update(self):
        for item in self.items:
            item._reset_flag()
            item.update()

    def draw(self, surface: Optional[_pg.Surface] = None):
        x = self.pos.x
        for item in self.items:
            item.pos.x, item.pos.y = x, self.pos.y
            item.draw(surface)
            x += item.width + item.padding.left + item.padding.right + self.space

class GridContainer(base.GUIBase):
    def __init__(self, u: float, v: float, width: float, height: float,
                 padding = profile.default_padding) -> None:
        super().__init__(u, v, width, height, padding)
        # TODO