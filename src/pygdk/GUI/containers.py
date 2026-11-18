from __future__ import annotations

import pygame as _pg
from typing import Optional as _Optional
from collections.abc import Sequence as _Sequence
import copy

from ..base import *
from .. import event as _event
from . import base as _base
from .. import profile as _profile
from .. import colors as _colors
from .scrollbar import (
    VerticalScrollBar as _VerticalScrollBar,
    HorizontalScrollBar as _HorizontalScrollBar
    )
from .label import (
    Label as _Label
)
from ..time import BenchMark as _BenchMark
from .. import animator as _animator

# TODO container bug: Item size is weird. When the cursor is on the item, can't scroll the container.

class ContainerBase(_base.Element):
    def __init__(self, u: float, v: float, width: float, height: float, background: _Optional[_base.Background] = None,
                 padding = _profile.default_padding, items: _Optional[_Sequence[_base.Element]] = None, bar_style: _base.ScrollBarStyle = _profile.default_scrollbar_style,
                 lock_vertical_scroll = False, lock_horizontal_scroll = False,
                 space: float = 0, border: _Optional[Border] = Border(0, _colors.WHITE), animator: _Optional[_animator.GAnimator] = None) -> None:
        super().__init__(u, v, width, height, padding, border, animator)

        self.background = background
        if items is not None:
            self.items: list[_base.Element] = list(items)
            for item in self.items:
                self.set_child(item)
        else:
            self.items: list[_base.Element] = []

        self.space = space
        self.bar_style = bar_style

        self.lock_vertical_scroll = lock_vertical_scroll
        self.lock_horizontal_scroll = lock_horizontal_scroll

        self.item_size = Vec2(0, 0)

        self.scroll_h = 0
        self.scroll_v = 0

        self.title_text_obj: _Optional[_Label] = None
        self.v_scrollBar_obj: _Optional[_VerticalScrollBar] = None
        self.h_scrollBar_obj: _Optional[_HorizontalScrollBar] = None

        self.callback_mousewheelscrolled = self.on_mousewheelscroll
        # if not no_register:
        #     _event.EventManager.register_mousewheeldown(type(self).on_mousewheeldown)
        #     _event.EventManager.register_mousewheelup(type(self).on_mousewheelup)
        #     _event.EventManager.link_instance(self)

    def adjust_size(self):
        width = abs(self.item_size.width - self.size.width)
        height = abs(self.item_size.height - self.size.height)
        if self.scroll_h > 0 or self.h_scrollBar_obj is None:
            self.scroll_h = 0
        elif self.scroll_h < -width:
            self.scroll_h = -width

        if self.scroll_v > 0 or self.v_scrollBar_obj is None:
            self.scroll_v = 0
        elif self.scroll_v < -height:
            self.scroll_v = -height

    def on_mousewheelscroll(self, e):
        delta: int = e.y * _profile.lines_per_scroll
        if _event.getMod().isShift():
            self.scroll_h += delta
        else:
            self.scroll_v += delta
        self.adjust_size()
        self._calc_positions()
        self.set_dirty()

    def update(self):
        if not self.should_update(): return
        with _BenchMark(f"{self}.update:item.update()"):
            for item in self.items:
                item.update()
        with _BenchMark(f"{self}.update:super().update()"):
            super().update()

        with _BenchMark(f"{self} others"):
            _vertical_scroll = False
            _horizontal_scroll = False
            if self.item_size.height > self.size.height:
                _vertical_scroll = True
            if self.item_size.width > self.size.width:
                _horizontal_scroll = True
            if self.lock_vertical_scroll:
                _vertical_scroll = False
            if self.lock_horizontal_scroll:
                _horizontal_scroll = False

            if self.lock_vertical_scroll:
                self.scroll_v = 0
            if self.lock_horizontal_scroll:
                self.scroll_h = 0

            # make scroll bar
            # u, v = _base._pos2uv(self.pos, self.size.width, self.size.height)
            if (_vertical_scroll
                    and self.v_scrollBar_obj is None):
                self.v_scrollBar_obj = _VerticalScrollBar(
                    0, 0, self.item_size, self.size, self.bar_style, self._padding)
                self.v_scrollBar_obj.pos = Vec2(0, 0)
                self.set_child(self.v_scrollBar_obj)

            elif not _vertical_scroll:
                if self.v_scrollBar_obj:
                    self.rm_child(self.v_scrollBar_obj)
                self.v_scrollBar_obj = None
                
            if (_horizontal_scroll
                    and self.h_scrollBar_obj is None):
                self.h_scrollBar_obj = _HorizontalScrollBar(
                    0, 0, self.item_size, self.size, self.bar_style, self._padding)
                self.h_scrollBar_obj.pos = Vec2(0, 0)
                self.set_child(self.h_scrollBar_obj)   
            elif not _horizontal_scroll:
                if self.h_scrollBar_obj:
                    self.rm_child(self.h_scrollBar_obj)
                self.h_scrollBar_obj = None

            # background image position
            if self.background and self.background.isImage():
                self.background.image.pos = Vec2(0,0)       # pyright: ignore
                if self.background.image.size.width != self.size.width:     # pyright: ignore
                    self.background.image.size.width = self.size.width      # pyright: ignore
                if self.background.image.size.height != self.size.height:   # pyright: ignore
                    self.background.image.size.height = self.size.height    # pyright: ignore
                with _BenchMark(f"{self}.update:background.image.resize_strict()"):
                    self.background.image.resize_strict()   # pyright: ignore
                with _BenchMark(f"{self}.update:background.image.update()"):
                    self.background.image.update()          # pyright: ignore

            # update scrollbar member values and udpate them
            if self.v_scrollBar_obj:
                self.v_scrollBar_obj.scroll_v = self.scroll_v # pyright: ignore
                self.v_scrollBar_obj.update()
            if self.h_scrollBar_obj:
                self.h_scrollBar_obj.scroll_h = self.scroll_h # pyright: ignore
                self.h_scrollBar_obj.update()
        
    def draw(self):
        if not self.should_draw(): return
        super().draw()
        if self.background and self.background.isColor():
            _pg.draw.rect(
                self.surface, self.background.color,# pyright: ignore
                _pg.Rect(0,0, *self.size))
        elif self.background and self.background.isImage():
            self.background.image.draw() # pyright: ignore
        self.reset_dirty()

    def push_item(self, item: _base.Element):
        self.items.append(item)
        self.set_child(item)
        self._calc_positions()
        self._calc_size()

    def set_items(self, items: _Sequence[_base.Element]):
        for item in self.items:
            self.rm_child(item)

        self.items = list(items)
        for item in self.items:
            if item not in self.children:
                self.set_child(item)
        self._calc_positions()
        self._calc_size()
        self.set_dirty()

    def _get_border_width(self) -> float:
        return self._border.width if self._border is not None else 0

    def rm_item(self, item: _base.Element):
        self.items.remove(item)
        self.rm_child(item)
        self._calc_positions()
        self._calc_size()

    def _calc_size(self): pass
    def _calc_positions(self): pass

# containers
class VerticalAlignContainer(ContainerBase):
    def __init__(self, u: float, v: float, width: float, height: float, background: _Optional[Background] = None,
                 padding = _profile.default_padding, items: _Optional[_Sequence[_base.Element]] = None, bar_style: _base.ScrollBarStyle = _profile.default_scrollbar_style,
                 lock_vertical_scroll = False, lock_horizontal_scroll = False,
                 space: float = 0, alignment: Alignment = Alignment.LEFT, border: _Optional[Border] = Border(0, _colors.WHITE),
                 animator: _Optional[_animator.GAnimator] = None) -> None:
        super().__init__(u, v, width, height, background, padding, items, bar_style, lock_vertical_scroll, lock_horizontal_scroll, space, border, animator)
        self.alignment = alignment
        self._calc_size()
        self._calc_positions()

    def update(self):
        if not self.should_update(): return
        super().update()

    def draw(self):
        if not self.should_draw(): return
        super().draw()

        for item in self.items:
            if item.pos.y + item.size.height > 0 and item.pos.y < self.size.height:
                item.draw()

        if self.v_scrollBar_obj: self.v_scrollBar_obj.draw()
        if self.h_scrollBar_obj: self.h_scrollBar_obj.draw()
        self.reset_dirty()

    def _calc_size(self):
        self.item_size.width = 0
        if len(self.items) != 0:
            self.item_size.width = max([item.size.width for item in self.items])

        self.item_size.height = 0
        for item in self.items:
            self.item_size.height += item.size.height
        self.item_size.height += (len(self.items) - 1) * self.space
        self.item_size.height += self._padding.top + self._padding.bottom

    def _calc_positions(self):
        border_width = self._get_border_width()
        x = self._padding.left + border_width
        y = self._padding.top + border_width

        for item in self.items:
            item.pos = Vec2(x + self.scroll_h, y + self.scroll_v)
            if self.alignment == Alignment.CENTER:
                item.pos.x = self.size.width/2 - item.size.width/2
            elif self.alignment == Alignment.RIGHT:
                item.pos.x = self.size.width - item.size.width - self._padding.right
            y += item.size.height + self.space

class HorizontalAlignContainer(ContainerBase):
    def __init__(self, u: float, v: float, width: float, height: float, background: _Optional[Background] = None,
                 padding = _profile.default_padding, items: _Optional[_Sequence[_base.Element]] = None, bar_style: _base.ScrollBarStyle = _profile.default_scrollbar_style,
                 lock_vertical_scroll = False, lock_horizontal_scroll = False,
                 space: float = 0, border: _Optional[Border] = Border(0, _colors.WHITE), animator: _Optional[_animator.GAnimator] = None) -> None:
        super().__init__(u, v, width, height, background, padding, items, bar_style, lock_vertical_scroll, lock_horizontal_scroll, space, border, animator)
        self._calc_size()
        self._calc_positions()

    def update(self):
        if not self.should_update(): return
        super().update()

    def draw(self):
        if not self.should_draw(): return
        super().draw()

        for item in self.items:
            if item.pos.x + item.size.width > 0 and item.pos.x < self.size.width:
                item.draw()

        if self.v_scrollBar_obj: self.v_scrollBar_obj.draw()
        if self.h_scrollBar_obj: self.h_scrollBar_obj.draw()

    def _calc_size(self):
        self.item_size.width = 0
        for item in self.items:
            self.item_size.width += item.size.width
        self.item_size.width += (len(self.items) - 1) * self.space
        self.item_size.width += self._padding.left + self._padding.right

        self.item_size.height = 0
        if len(self.items) != 0:
            self.item_size.height = max([item.size.height for item in self.items])
            baseline_offsets = [
                (item, item._get_baseline_offset())
                for item in self.items
            ]
            baseline_offsets = [
                (item, offset)
                for item, offset in baseline_offsets
                if offset is not None
            ]
            if baseline_offsets:
                baseline = max(offset for _, offset in baseline_offsets)
                descent = max(
                    item.size.height - offset
                    for item, offset in baseline_offsets
                )
                self.item_size.height = max(
                    self.item_size.height,
                    baseline + descent,
                )

    def _calc_positions(self):
        border_width = self._get_border_width()
        x = self._padding.left + border_width
        top = self._padding.top + border_width
        baseline_offsets = [
            item._get_baseline_offset()
            for item in self.items
        ]
        baseline = max(
            (offset for offset in baseline_offsets if offset is not None),
            default=None,
        )

        for item, offset in zip(self.items, baseline_offsets):
            y = top
            if baseline is not None and offset is not None:
                y += baseline - offset
            item.pos = Vec2(x + self.scroll_h, y + self.scroll_v)
            x += item.size.width + self.space


class GridContainer(ContainerBase):
    def __init__(self, u: float, v: float, width: float, height: float, background: _Optional[Background] = None,
                 grid_col: int = -1, grid_row: int = -1,
                 padding = _profile.default_padding, items: _Optional[_Sequence[_base.Element]] = None, bar_style: _event.ScrollBarStyle = _profile.default_scrollbar_style,
                 lock_vertical_scroll = False, lock_horizontal_scroll = False, 
                 space: float = 0, border: _Optional[Border] = Border(0, _colors.WHITE), animator: _Optional[_animator.GAnimator] = None) -> None:
        if grid_col < 1 or grid_row < 1:
            raise Exception("Invalid number. It must be more than 1.")
        super().__init__(u, v, width, height, background, padding, items, bar_style, lock_vertical_scroll, lock_horizontal_scroll, space, border, animator)
        self.grid_col, self.grid_row = grid_col, grid_row

        self._calc_size()
        self._calc_positions()

    def update(self):
        if not self.should_update(): return
        super().update()

    def draw(self):
        if not self.should_draw(): return
        super().draw()

        _index = 0
        for item in self.items:
            if item.pos.x + item.size.width > 0 and item.pos.x < self.size.width:
                item.draw()
            _index += 1

        if self.v_scrollBar_obj: self.v_scrollBar_obj.draw()
        if self.h_scrollBar_obj: self.h_scrollBar_obj.draw()

    def _calc_size(self):
        def separate_items(_list: list, _n: int):
            return [_list[i : i + _n] for i in range(0, len(_list), _n)]

        if len(self.items) == 0: return
        x_size = max(
            [
                sum([obj.size.width for obj in h_objs]) + (len(h_objs) - 1) * self.space + self._padding.left + self._padding.right
                for h_objs in separate_items(self.items, self.grid_row)
            ]
        )
        y_size = sum(
            [
                max([obj.size.height for obj in h_objs])
                for h_objs in separate_items(self.items, self.grid_row)
            ]
        ) + (self.grid_col - 1) * self.space + self._padding.top + self._padding.bottom

        self.item_size.width = x_size
        self.item_size.height = y_size

    def _calc_positions(self):
        with _BenchMark(f"{self}._calc_positions()"):
            border_width = self._get_border_width()
            x = self._padding.left + border_width
            y = self._padding.top + border_width

            _index = 0
            for item in self.items:
                item.pos = Vec2(x + self.scroll_h, y + self.scroll_v)
                # if item.pos.x + item.size.width > 0 and item.pos.x < self.size.width:
                #     item.draw(self.surface)
                if (_index + 1) % self.grid_row == 0:
                    x = self._padding.left + border_width # reset
                    y += item.size.height + self.space
                else:
                    x += item.size.width + self.space

                _index += 1

class TabContainer(_base.Element):
    def __init__(self, u: float, v: float, width: float, height: float,
                 tab_background: Background,
                 selected_tab_background: Background,
                 tabitems_background: _Optional[Background] = None,
                 bar_style: ScrollBarStyle = _profile.default_scrollbar_style,
                 tab_textAttributes: TextAttributes = _profile.default_textAttributes,
                 tab_properties: list[TabProperty] = [],
                 padding=_profile.default_padding, border: _Optional[_event.Border] = Border(0, _colors.WHITE),
                 animator: _Optional[_animator.GAnimator] = None) -> None:
        from . import ImageButton, Button, Label
        super().__init__(u, v, width, height, padding, border, animator)

        self.tab_background = tab_background
        self.selected_tab_background = selected_tab_background
        self.tabitems_background = tabitems_background
        button_border = border if border is not None else Border(0, _colors.WHITE)

        tab_buttons: list[_base.Element] = []
        for tab_property in tab_properties:
            label = Label(0, 0, tab_property.name, tab_textAttributes, padding=padding)
            button_width = label.size.width + padding.left + padding.right
            button_height = label.size.height + padding.top + padding.bottom
            callback = lambda tab=tab_property: self.on_click_tab(tab_properties.index(tab))

            if tab_background.isColor():
                background_color = tab_background.color
                if background_color is None:
                    raise ValueError("A color tab background must have a color")
                tab_button = Button(
                    0, 0, button_width, button_height, tab_property.name,
                    tab_textAttributes, background_color, button_border, padding,
                    callback_clicked=callback,
                )
            else:
                background_image = tab_background.image
                if background_image is None:
                    raise ValueError("An image tab background must have an image")
                tab_button = ImageButton(
                    0, 0, button_width, tab_property.name,
                    tab_textAttributes, copy.copy(background_image), button_border, padding,
                    callback_clicked=callback,
                )
            tab_buttons.append(tab_button)

        tab_height = max(
            (button.size.height for button in tab_buttons),
            default=tab_textAttributes.FontSize,
        ) + padding.top + padding.bottom
        self.HC_Tab = HorizontalAlignContainer(
            0, 0, width, tab_height, tab_background, padding,
            items=tab_buttons,
            bar_style=ScrollBarStyle(0),
            lock_vertical_scroll=True)
        self.set_child(self.HC_Tab)
        self.HC_Tab.pos = Vec2(0,0)

        self.tab_properties = tab_properties

        self.current_tabIndex = 0
        self.VC_TabItems = VerticalAlignContainer(
            u, v, width, height - self.HC_Tab.size.height, tabitems_background, padding,
            self.tab_properties[self.current_tabIndex].items,
            bar_style=bar_style
        )
        self.set_child(self.VC_TabItems)
        self.VC_TabItems.pos = Vec2(0, self.HC_Tab.size.height)
        self._set_colors()

    def update(self) -> None:
        if not self.should_update(): return
        self.HC_Tab.update()
        self.VC_TabItems.update()
        super().update()
        
    def draw(self):
        if not self.should_draw(): return
        super().draw()
        self.HC_Tab.draw()
        self.VC_TabItems.draw()
        self.reset_dirty()

    def on_click_tab(self, index: int):
        self.current_tabIndex = index
        self.VC_TabItems.set_items(self.tab_properties[self.current_tabIndex].items)
        self._set_colors()
        self.set_dirty()

    def _set_colors(self):
        from . import Button, ImageButton
        background_color = self.tab_background.color
        background_image = self.tab_background.image
        selected_color = self.selected_tab_background.color
        selected_image = self.selected_tab_background.image

        for item in self.HC_Tab.items:
            if type(item) == Button and background_color is not None:
                item._color = background_color
                item.set_dirty()
            elif type(item) == ImageButton and background_image is not None:
                item.image_obj = background_image
                item.set_dirty()
            else:
                raise ValueError("Tab background does not match the tab button type")

        current_item = self.HC_Tab.items[self.current_tabIndex]
        if type(current_item) == Button and selected_color is not None:
            current_item._color = selected_color
            current_item.set_dirty()
        elif type(current_item) == ImageButton and selected_image is not None:
            current_item.image_obj = selected_image
            current_item.set_dirty()
        self.HC_Tab.set_dirty()