import pygame as _pg
from typing import Optional
import copy

from src.colors import WHITE

from ..base import *
from .. import event
from . import base
from .. import profile
from .. import colors
from .scrollbar import VerticalScrollBar, HorizontalScrollBar

class ContainerBase(base.GUIBase):
    def __init__(self, u: float, v: float, width: float, height: float, background_color: Optional[gdk_color] = None,
                 padding = profile.default_padding, items: list[base.GUIBase] = [], bar_style: base.ScrollBarStyle = profile.default_scrollbar_style,
                 space: float = 0, border: Border = Border(0, colors.WHITE), no_register = False) -> None:
        super().__init__(u, v, width, height, padding, border, no_register)
        self.background_color = background_color
        self.items = items
        self.space = space
        self.bar_style = bar_style

        self.item_width = 0
        self.item_height = 0

        self._scrollable = False
        self.scrollable_h = False
        self.scrollable_v = False
        self.scroll_h = 0
        self.scroll_v = 0

        if not no_register:
            event.EventManager.register_mousewheeldown(type(self).on_mousewheeldown)
            event.EventManager.register_mousewheelup(type(self).on_mousewheelup)
            event.EventManager.link_instance(self)

    def adjust_size(self):
        width = self.item_width - self.width
        height = self.item_height - self.height

        if self.scroll_h > 0:
            self.scroll_h = 0
        elif self.scroll_h < -width:
            self.scroll_h = -width

        if self.scroll_v > 0:
            self.scroll_v = 0
        elif self.scroll_v < -height:
            self.scroll_v = -height

    def on_mousewheeldown(self, e):
        if not self.hovered: return
        delta: int = e.y * 32
        if event.getMod().isShift():
            self.scroll_h += delta
        else:
            self.scroll_v += delta
        self.adjust_size()

    def on_mousewheelup(self, e):
        if not self.hovered: return
        delta: int = e.y * 32
        if event.getMod().isShift():
            self.scroll_h += delta
        else:
            self.scroll_v += delta
        self.adjust_size()

    def update(self):
        super().update()
        for item in self.items:
            item._reset_flag()
            item.update()

        if self.item_height > self.height:
            self.scrollable_v = True
        else:
            self.scrollable_v = False
        if self.item_width > self.width:
            self.scrollable_h = True
        else:
            self.scrollable_h = False

        if self.scrollable_v:
            scroll_bar_length = self.height / self.item_height * (self.height + (self.items[-1].width + self.padding.left + self.padding.right + self.space))

            start_pos = Vec2(self.width, 0)

            end_pos = copy.copy(start_pos)
            end_pos.y += scroll_bar_length

            _pg.draw.line(self.surface, (255,255,255), (start_pos*2).pos, (end_pos*2).pos, 10)

        if self.scrollable_h:
            scroll_bar_length = self.width / self.item_width * self.width

            start_pos = copy.copy(self.pos)
            start_pos.y += self.height

            end_pos = copy.copy(start_pos)
            end_pos.x += scroll_bar_length

            _pg.draw.line(self.surface, (255,255,255), (start_pos*2).pos, (end_pos*2).pos, 10)

    def draw(self, surface: Optional[_pg.Surface] = None):
        super().draw(surface)
        if self.background_color:
            _pg.draw.rect(profile.surface, self.background_color, _pg.Rect(*(self.pos*2).pos, self.width*2, self.height*2))

# containers
class VerticalAlignContainer(ContainerBase):
    def __init__(self, u: float, v: float, width: float, height: float, background_color: Optional[gdk_color] = None,
                 padding = profile.default_padding, items: list[base.GUIBase] = [], bar_style: base.ScrollBarStyle = profile.default_scrollbar_style,
                 space: float = 0, border: Border = Border(0, colors.WHITE), no_register = False) -> None:
        super().__init__(u, v, width, height, background_color, padding, items, bar_style, space, border, no_register)

        self.item_width = max(*[item.width for item in self.items])
        for item in self.items[:-1]:
            self.item_height += item.height + item.padding.top + item.padding.bottom + self.space
        self.item_height += self.height

        self.v_scrollBar_obj = VerticalScrollBar(
            u, v, self.item_width, self.item_height, self.width, self.height, bar_style)

    def update(self):
        super().update()
        self.v_scrollBar_obj.scroll_v = self.scroll_v # pyright: ignore
        self.v_scrollBar_obj.update()

    def draw(self, surface: Optional[_pg.Surface] = None):
        super().draw(surface)
        x = self.padding.left + self.border.width
        y = self.padding.top + self.border.width

        for item in self.items:
            item.pos = Vec2(x, y + self.scroll_v)
            item.draw(self.surface)
            y += item.height + item.padding.top + item.padding.bottom + self.space

        self.v_scrollBar_obj.draw(self.surface)

        self._flush()

class HorizontalAlignContainer(ContainerBase):
    def __init__(self, u: float, v: float, width: float, height: float, background_color: Optional[gdk_color] = None,
                 padding = profile.default_padding, items: list[base.GUIBase] = [], bar_style: base.ScrollBarStyle = profile.default_scrollbar_style,
                 space: float = 0, border: Border = Border(0, colors.WHITE), no_register = False) -> None:
        super().__init__(u, v, width, height, background_color, padding, items, bar_style, space, border, no_register)

        for item in self.items[:-1]:
            self.item_width += item.width + item.padding.left + item.padding.right + self.space
        self.item_width += self.width
        self.item_height = max(*[item.height for item in self.items])

        self.h_scrollBar_obj = HorizontalScrollBar(
            u, v, self.item_width, self.item_height, self.width, self.height, bar_style
        )

    def update(self):
        super().update()
        self.h_scrollBar_obj.scroll_h = self.scroll_h # pyright: ignore
        self.h_scrollBar_obj.update()

    def draw(self, surface: Optional[_pg.Surface] = None):
        super().draw(surface)
        x = self.padding.left + self.border.width
        y = self.padding.top + self.border.width

        for item in self.items:
            item.pos = Vec2(x + self.scroll_h, y)
            item.draw(self.surface)
            x += item.width + item.padding.left + item.padding.right + self.space

        self.h_scrollBar_obj.draw(self.surface)

        self._flush()

class GridContainer(base.GUIBase):
    def __init__(self, u: float, v: float, width: float, height: float,
                 padding = profile.default_padding, border: Border = Border(0, colors.WHITE), no_register = False) -> None:
        super().__init__(u, v, width, height, padding, border, no_register)
        self.border = border
        # TODO