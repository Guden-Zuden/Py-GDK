from __future__ import annotations

import pygame as _pg
from typing import Optional as _Optional
import copy

from ..base import *
from .. import event as _event
from . import base as _base
from .. import profile as _profile
from .. import colors as _colors
from .scrollbar import(
    VerticalScrollBar as _VerticalScrollBar,
    HorizontalScrollBar as _HorizontalScrollBar
    )

class ContainerBase(_base.GUIBase):
    def __init__(self, u: float, v: float, width: float, height: float, background: _Optional[_base.Background] = None,
                 padding = _profile.default_padding, items: list[_base.GUIBase] = [], bar_style: _base.ScrollBarStyle = _profile.default_scrollbar_style,
                 lock_vertical_scroll = False, lock_horizontal_scroll = False,
                 space: float = 0, border: Border = Border(0, _colors.WHITE), no_register = False) -> None:
        super().__init__(u, v, width, height, padding, border, no_register)

        self.background = background
        self.items = items
        for item in self.items:
            self.attach(item)

        self.space = space
        self.bar_style = bar_style

        self.lock_vertical_scroll = lock_vertical_scroll
        self.lock_horizontal_scroll = lock_horizontal_scroll

        self.item_width = 0
        self.item_height = 0

        self.scroll_h = 0
        self.scroll_v = 0

        self.v_scrollBar_obj: _Optional[_VerticalScrollBar] = None
        self.h_scrollBar_obj: _Optional[_HorizontalScrollBar] = None

        if not no_register:
            _event.EventManager.register_mousewheeldown(type(self).on_mousewheeldown)
            _event.EventManager.register_mousewheelup(type(self).on_mousewheelup)
            _event.EventManager.link_instance(self)

    def adjust_size(self):
        width = abs(self.item_width - self.width)
        height = abs(self.item_height - self.height)
        if not self.lock_horizontal_scroll:
            if self.scroll_h > 0:
                self.scroll_h = 0
            elif self.scroll_h < -width:
                self.scroll_h = -width

        if not self.lock_vertical_scroll:
            if self.scroll_v > 0:
                self.scroll_v = 0
            elif self.scroll_v < -height:
                self.scroll_v = -height
        
    def on_mousewheeldown(self, e):
        if not self.hovered: return
        delta: int = e.y * 32
        if _event.getMod().isShift():
            self.scroll_h += delta
        else:
            self.scroll_v += delta
        self.adjust_size()

    def on_mousewheelup(self, e):
        if not self.hovered: return
        delta: int = e.y * 32
        if _event.getMod().isShift():
            self.scroll_h += delta
        else:
            self.scroll_v += delta
        self.adjust_size()

    def update(self):
        for item in self.items:
            item.update()
        super().update()

        if self.item_height < self.height:
            self.lock_vertical_scroll = True
        if self.item_width < self.width:
            self.lock_horizontal_scroll = True

        if self.lock_vertical_scroll:
            self.scroll_v = 0
        if self.lock_horizontal_scroll:
            self.scroll_h = 0

        # make scroll bar
        u, v = _base._posTouv(self.pos, self.width, self.height)
        if (not self.lock_vertical_scroll
                and self.v_scrollBar_obj is None
                and not self.lock_vertical_scroll):
            self.v_scrollBar_obj = _VerticalScrollBar(
                u, v, self.item_width, self.item_height, self.width, self.height, self.bar_style, self.padding, self.no_register)
        elif self.lock_vertical_scroll:
            self.v_scrollBar_obj = None
            
        if (not self.lock_horizontal_scroll
                and self.h_scrollBar_obj is None
                and not self.lock_horizontal_scroll):
            self.h_scrollBar_obj = _HorizontalScrollBar(
                u, v, self.item_width, self.item_height, self.width, self.height, self.bar_style, self.padding, self.no_register)            
        elif self.lock_horizontal_scroll:
            self.h_scrollBar_obj = None

        # background image position
        if self.background and self.background.isImage():
            self.background.image.pos = Vec2(0,0)        # pyright: ignore
            self.background.image.width = self.width    # pyright: ignore
            self.background.image.height = self.height  # pyright: ignore
            self.background.image.resize_strict()       # pyright: ignore

        # update scrollbar member values and udpate them
        if self.v_scrollBar_obj:
            self.v_scrollBar_obj.item_width = self.item_width
            self.v_scrollBar_obj.item_height = self.item_height
            self.v_scrollBar_obj.scroll_v = self.scroll_v # pyright: ignore
            self.v_scrollBar_obj.update()
        if self.h_scrollBar_obj:
            self.h_scrollBar_obj.item_width = self.item_width
            self.h_scrollBar_obj.item_height = self.item_height
            self.h_scrollBar_obj.scroll_h = self.scroll_h # pyright: ignore
            self.h_scrollBar_obj.update()
        
    def draw(self, surface: _Optional[_pg.Surface] = None):
        super().draw(surface)
        if self.background and self.background.isColor():
            _pg.draw.rect(
                self.surface, self.background.color,# pyright: ignore
                _pg.Rect(0,0, self.width*_profile.surface_scale, self.height*_profile.surface_scale))
        elif self.background and self.background.isImage():
            self.background.image.draw(self.surface) # pyright: ignore

    def pushItem(self, item: _base.GUIBase): ...

# containers
class VerticalAlignContainer(ContainerBase):
    def __init__(self, u: float, v: float, width: float, height: float, background: _Optional[Background] = None,
                 padding = _profile.default_padding, items: list[_base.GUIBase] = [], bar_style: _base.ScrollBarStyle = _profile.default_scrollbar_style,
                 lock_vertical_scroll = False, lock_horizontal_scroll = False,
                 space: float = 0, border: Border = Border(0, _colors.WHITE), no_register = False) -> None:
        super().__init__(u, v, width, height, background, padding, items, bar_style, lock_vertical_scroll, lock_horizontal_scroll, space, border, no_register)

        if len(self.items) == 0:
            self.item_width = self.width/2
        elif len(self.items) == 1:
            self.item_width = self.items[0].width + self.width/2
        else:
            self.item_width = max(*[item.width for item in self.items]) + self.width/2

        for item in self.items[:-1]:
            self.item_height += item.height + item.padding.top + item.padding.bottom + self.space
        self.item_height += self.height

    def update(self):
        super().update()

    def draw(self, surface: _Optional[_pg.Surface] = None):
        super().draw(surface)
        x = self.padding.left + self.border.width
        y = self.padding.top + self.border.width

        for item in self.items:
            item.pos = Vec2(x + self.scroll_h, y + self.scroll_v)
            if item.pos.y + item.height > 0 and item.pos.y < self.height:
                item.draw(self.surface)
            y += item.height + item.padding.top + item.padding.bottom + self.space

        if self.v_scrollBar_obj: self.v_scrollBar_obj.draw(self.surface)
        if self.h_scrollBar_obj: self.h_scrollBar_obj.draw(self.surface)

        if surface: self._flush(surface)
        else: self._flush()

    def pushItem(self, item: _base.GUIBase):
        self.items.append(item)

        item = self.items[-2]
        self.item_width = max(*[item.width for item in self.items])
        self.item_height += item.height + item.padding.top + item.padding.bottom + self.space*2

class HorizontalAlignContainer(ContainerBase):
    def __init__(self, u: float, v: float, width: float, height: float, background: _Optional[Background] = None,
                 padding = _profile.default_padding, items: list[_base.GUIBase] = [], bar_style: _base.ScrollBarStyle = _profile.default_scrollbar_style,
                 lock_vertical_scroll = False, lock_horizontal_scroll = False,
                 space: float = 0, border: Border = Border(0, _colors.WHITE), no_register = False) -> None:
        super().__init__(u, v, width, height, background, padding, items, bar_style, lock_vertical_scroll, lock_horizontal_scroll, space, border, no_register)

        for item in self.items[:-1]:
            self.item_width += item.width + item.padding.left + item.padding.right + self.space
        self.item_width += self.width

        if len(self.items) == 0:
            self.item_height = self.height/2
        elif len(self.items) == 1:
            self.item_height = self.items[0].height + self.height/2
        else:
            self.item_height = (max(*[item.height for item in self.items]) + self.height/2)

    def update(self):
        super().update()

    def draw(self, surface: _Optional[_pg.Surface] = None):
        super().draw(surface)
        x = self.padding.left + self.border.width
        y = self.padding.top + self.border.width

        for item in self.items:
            item.pos = Vec2(x + self.scroll_h, y + self.scroll_v)
            if item.pos.x + item.width > 0 and item.pos.x < self.width:
                item.draw(self.surface)
            x += item.width + item.padding.left + item.padding.right + self.space

        if self.v_scrollBar_obj: self.v_scrollBar_obj.draw(self.surface)
        if self.h_scrollBar_obj: self.h_scrollBar_obj.draw(self.surface)

        if surface: self._flush(surface)
        else: self._flush()

    def pushItem(self, item: _base.GUIBase):
        self.items.append(item)

        item = self.items[-2]
        self.item_width += item.width + item.padding.left + item.padding.right + self.space*2
        self.item_height = max(*[item.height for item in self.items])

class GridContainer(_base.GUIBase):
    def __init__(self, u: float, v: float, width: float, height: float,
                 padding = _profile.default_padding, border: Border = Border(0, _colors.WHITE), no_register = False) -> None:
        super().__init__(u, v, width, height, padding, border, no_register)
        self.border = border
        # TODO

class TabContainer(_base.GUIBase):
    def __init__(self, u: float, v: float, width: float, height: float,
                 tab_background: Background, tabitems_background: _Optional[Background] = None,
                 bar_style: ScrollBarStyle = _profile.default_scrollbar_style,
                 tab_textAttributes: TextAttributes = _profile.default_textAttributes,
                 tab_properties: list[TabProperty] = [],
                 padding=_profile.default_padding, border: _event.Border = Border(0, _colors.WHITE), no_register=False) -> None:
        from . import ImageButton, Button, Text
        super().__init__(u, v, width, height, padding, border, no_register)
        self.HC_Tab = HorizontalAlignContainer(
            0,0, width, tab_textAttributes.FontSize + padding.top + padding.bottom, tab_background, padding,
            items=[                                                                                    #pyright: ignore
                Button(0,0, *Text(0,0, tabProperty.name, tab_textAttributes, padding).get_size(),  
                       tabProperty.name, tab_textAttributes, tab_background.color, border, padding, # pyright: ignore
                       event_func=lambda tab=tabProperty: self.on_click_tab(tab_properties.index(tab)))
                if tab_background.isColor()
                else ImageButton(0,0, Text(0,0, tabProperty.name, tab_textAttributes, padding).width,
                            tabProperty.name, tab_textAttributes, tab_background.image, border, padding,
                            event_func=lambda tab=tabProperty: self.on_click_tab(tab_properties.index(tab)))
                for tabProperty in tab_properties
            ],
            bar_style=ScrollBarStyle(0),
            lock_vertical_scroll=True)
        self.HC_Tab.pos = Vec2(0,0)
        self.attach(self.HC_Tab)
        # print(self.HC_Tab.items[0].get_parents())

        self.tab_properties = tab_properties
        for tab_property in tab_properties:
            for item in tab_property.items:
                item.pos.y += self.HC_Tab.height

        self.current_tabIndex = 0
        self.VC_TabItems = VerticalAlignContainer(
            u, v, width, height - self.HC_Tab.height, tabitems_background, padding,
            self.tab_properties[self.current_tabIndex].items
        )
        self.VC_TabItems.pos = Vec2(0, self.HC_Tab.height)
        self.attach(self.VC_TabItems)

    def update(self) -> None:
        self.HC_Tab.update()
        self.VC_TabItems.update() # TODO: bug fix: おそらくVCのオブジェクトに邪魔されてタブがクリックできない
        super().update()
        
    def draw(self, surface: _Optional[_pg.Surface] = None):
        super().draw(surface)
        self.HC_Tab.draw(self.surface)
        self.VC_TabItems.draw(self.surface)

        if surface: self._flush(surface)
        else: self._flush()

    def on_click_tab(self, index):
        print(f"clicked. index: {index}")  #TODO
        self.current_tabIndex = index
        self.VC_TabItems.items = self.tab_properties[self.current_tabIndex].items