import pygame as _pg
from typing import (
    Optional as _Optional
)

from ..base import *
from .. import profile as _profile
from .. import colors as _colors
from . import base as _base


class ToolBar(_base.GUIBase):
    def __init__(
            self, u: float, v: float, textAttributes: TextAttributes = _profile.default_textAttributes,
            toolbar_background: _Optional[Background] = None, dropdownMenu_background: _Optional[Background] = None, bar_style: ScrollBarStyle = _profile.default_scrollbar_style,
            space = 0,padding=_profile.default_padding, border: _base.Border = Border(0, _colors.WHITE), no_register=False
            ) -> None:
        from . import HorizontalAlignContainer, VerticalAlignContainer
        super().__init__(u, v, _profile.width, textAttributes.FontSize + padding.top + padding.bottom, padding, border, no_register)
        self.textAttributes = textAttributes
        self.HC_ToolBar = HorizontalAlignContainer(
            0,0,
            _profile.width, textAttributes.FontSize + padding.top + padding.bottom,
            background = toolbar_background,
            padding = padding,
            bar_style = bar_style,
            lock_vertical_scroll = True,
            lock_horizontal_scroll = False,
            space = space,
            border = border,
            no_register = no_register
            )
        self.add_inner(self.HC_ToolBar)
        self.add_child(self.HC_ToolBar)
        self.HC_ToolBar.sync_size_to(self)

        self.VC_DropDownMenu = VerticalAlignContainer(
            0,0,
            50,100,
            background = dropdownMenu_background,
            padding = padding,
            lock_vertical_scroll = True,
            lock_horizontal_scroll = True,
            space = space,
            border = border,
            no_register = no_register
            )
        self.VC_DropDownMenu.is_hide = True
        self.add_child(self.VC_DropDownMenu)

        self.toolbar_properties: list[ToolBarItemProperty] = []

    def push_item(self, toolbar_item_property: ToolBarItemProperty) -> None:
        from . import Button
        button = Button(
            0,0,
            100, self.size.height,
            text = toolbar_item_property.name,
            textAttributes = self.textAttributes,
            color = Color(0,0,0,0)
        )
        def on_click():
            property = next((property for property in self.toolbar_properties if property.name == button.text), None)
            if property:
                self.on_clicked_toolbar_item(property)
        button.event_func = on_click
        button.set_size(button.text_obj.size.width, self.textAttributes.FontSize)
        self.HC_ToolBar.push_item(button)
        self.toolbar_properties.append(toolbar_item_property)

    def on_clicked_toolbar_item(self, property: ToolBarItemProperty):
        from . import Button
        from .. import event

        for item in self.VC_DropDownMenu.items:
            item.is_hide = True # TODO: ISSUE: ボタンオブジェクトがイベントハンドラに残りメモリリーク的なことが起きている。

        self.VC_DropDownMenu.items.clear()
        for property_item in property.pulldown_menu_items:
            button = Button(
                0, 0,
                50, self.textAttributes.FontSize,
                text = property_item[0],
                textAttributes = self.textAttributes, 
                color = (0, 0, 0, 0),
                event_func=property_item[1]
            )
            button.size.width = button.text_obj.size.width
            self.VC_DropDownMenu.push_item(
                button
            )

        for item in self.VC_DropDownMenu.items:
            item.is_hide = False

        index = self.toolbar_properties.index(property)
        self.VC_DropDownMenu.set_pos(
            *self.HC_ToolBar.items[index].pos
        )
        self.VC_DropDownMenu.pos.y += self.HC_ToolBar.items[index].size.height
        self.VC_DropDownMenu.set_size(
            self.VC_DropDownMenu.item_size.width,
            self.VC_DropDownMenu.item_size.height
        )
        self.VC_DropDownMenu.is_hide = False

    def update(self) -> None:
        if self.is_hide: return
        super().update()
        self.HC_ToolBar.set_pos(*self.pos)
        self.HC_ToolBar.update()
        self.VC_DropDownMenu.update()

    def draw(self, surface: _Optional[_pg.Surface] = None) -> None:
        if self.is_hide: return
        super().draw(surface)
        self.HC_ToolBar.draw(self.surface)
        self.VC_DropDownMenu.draw(surface)

    
        if surface: self._flush(surface)
        else: self._flush()
        _pg.draw.circle(_profile.window.surface, (0,255,255), self.VC_DropDownMenu.pos.tuple, 5)
        _pg.draw.circle(_profile.window.surface, (0,255,255), self.HC_ToolBar.pos.tuple, 5)