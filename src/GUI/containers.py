import pygame as _pg
from typing import Optional

from . import base
from .. import profile

class VerticalAlignContainer(base.GUIBase):
    def __init__(self, u: float, v: float, width: float, height: float, 
                 padding: Optional[float] = None, items: list[base.GUIBase] = []) -> None:
        super().__init__(u, v, width, height, padding)
        self.items = items
        self.surface = _pg.Surface([self.width, self.height]) # TODO: 範囲外は描画しないようにする
    
    def update(self):
        for item in self.items:
            item._reset_flag()
            item.update()

    def draw(self):
        y = self.y
        for item in self.items:
            item.x, item.y = self.x, y
            item.draw()
            y += item.height + item.padding*2

    def pushItem(self, item: base.GUIBase):
        self.items.append(item)

class HorizontalAlignContainer(base.GUIBase):
    def __init__(self, u: float, v: float, width: float, height: float,
                 padding: Optional[float] = None, items: list[base.GUIBase] = [],
                 space: float = 0) -> None:
        super().__init__(u, v, width, height, padding)
        self.items = items
        
        self.space = space

    def update(self):
        for item in self.items:
            item._reset_flag()
            item.update()

    def draw(self):
        x = self.x
        for item in self.items:
            item.x, item.y = x, self.y
            item.draw()
            x += item.width + self.space + item.padding

class GridContainer(base.GUIBase):
    def __init__(self, u: float, v: float, width: float, height: float,
                 padding: float | None = None,) -> None:
        super().__init__(u, v, width, height, padding)
        # TODO