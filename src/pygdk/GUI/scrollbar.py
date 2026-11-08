import pygame as _pg
from typing import Optional as _Optional
import copy as _copy

from ..base import *
from .. import event as _event
from . import base as _base
from .. import profile as _profile
from .. import colors as _colors
from .. import animator as _animator

class ScrollBarBase(_base.Element):
    def __init__(self,
                 u: float, v: float, item_size: Vec2, field_size: Vec2,
                 bar_style: _base.ScrollBarStyle = _profile.default_scrollbar_style,
                 padding = _profile.default_padding, animator: _Optional[_animator.GAnimator] = None) -> None:
        super().__init__(u, v, *field_size.tuple, padding, animator=animator)
        self.size = field_size
        self.item_size = item_size
        self.field_size = field_size
        self.bar_style = bar_style

        self.scroll_v = 0
        self.scroll_h = 0

    def update(self):
        super().update()

class VerticalScrollBar(ScrollBarBase):
    def __init__(self,
                 u: float, v: float, item_size: Vec2, field_size: Vec2,
                 bar_style: _base.ScrollBarStyle = _profile.default_scrollbar_style,
                 padding = _profile.default_padding, animator: _Optional[_animator.GAnimator] = None) -> None:
        super().__init__(u, v, item_size, field_size, bar_style, padding, animator)
        self.start_pos = Vec2(self.size.width, 0)
        self.start_pos.x -= self.bar_style.width/2 # 太さの補正
        self.start_pos.y -= self.field_size.height / self.item_size.height * self.scroll_v

        self.end_pos = _copy.copy(self.start_pos)
        self.end_pos.y += self.field_size.height / self.item_size.height * self.field_size.height

    def update(self) -> None:
        super().update()
        self.start_pos = Vec2(self.size.width, 0)
        self.start_pos.x -= self.bar_style.width/2 # 太さの補正
        self.start_pos.y -= self.field_size.height / self.item_size.height * self.scroll_v

        self.end_pos = _copy.copy(self.start_pos)
        self.end_pos.y += self.field_size.height / self.item_size.height * self.field_size.height

    def draw(self):
        super().draw()

        if not self.bar_style.rounded:
            _pg.draw.line(self.surface, self.bar_style.color, 
                            (self.start_pos).tuple, (self.end_pos).tuple, self.bar_style.width)
        else:
            # 補正
            self.start_pos.y += self.bar_style.width/2
            self.end_pos.y -= self.bar_style.width/2
            _pg.draw.line(self.surface, self.bar_style.color,
                          (self.start_pos).tuple, (self.end_pos).tuple, self.bar_style.width)
            _pg.draw.circle(self.surface, self.bar_style.color, # start edge
                            (self.start_pos).tuple, self.bar_style.width/2)
            _pg.draw.circle(self.surface, self.bar_style.color, # end edge
                            (self.end_pos).tuple, self.bar_style.width/2)

class HorizontalScrollBar(ScrollBarBase):
    def __init__(self,
                 u: float, v: float, item_size: Vec2, field_size: Vec2,
                 bar_style: _base.ScrollBarStyle = _profile.default_scrollbar_style,
                 padding = _profile.default_padding, animator: _Optional[_animator.GAnimator] = None) -> None:
        super().__init__(u, v, item_size, field_size, bar_style, padding, animator)
        self.start_pos = Vec2(0, self.size.height)
        self.start_pos.y -= self.bar_style.width/2 # 太さの補正
        self.start_pos.x -= self.field_size.width / self.item_size.width * self.scroll_h

        self.end_pos = _copy.copy(self.start_pos)
        self.end_pos.x += self.field_size.width / self.item_size.width * self.field_size.width

    def update(self) -> None:
        if not self.should_update(): return
        super().update()
        self.start_pos = Vec2(0, self.size.height)
        self.start_pos.y -= self.bar_style.width/2 # 太さの補正
        self.start_pos.x -= self.field_size.width / self.item_size.width * self.scroll_h
        
        self.end_pos = _copy.copy(self.start_pos)
        self.end_pos.x += self.field_size.width / self.item_size.width * self.field_size.width

    def draw(self):
        if not self.should_draw(): return
        super().draw()

        if not self.bar_style.rounded:
            _pg.draw.line(self.surface, self.bar_style.color, 
                            (self.start_pos).tuple, (self.end_pos).tuple, self.bar_style.width)
        else:
            # 補正
            self.start_pos.y += self.bar_style.width/2
            self.end_pos.y -= self.bar_style.width/2
            _pg.draw.line(self.surface, self.bar_style.color,
                          (self.start_pos).tuple, (self.end_pos).tuple, self.bar_style.width)
            _pg.draw.circle(self.surface, self.bar_style.color, # start edge
                            (self.start_pos).tuple, self.bar_style.width/2)
            _pg.draw.circle(self.surface, self.bar_style.color, # end edge
                            (self.end_pos).tuple, self.bar_style.width/2)
            