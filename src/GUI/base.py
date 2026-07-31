# import sys
# import pathlib
# sys.path.append(pathlib.Path().absolute().__str__())
from __future__ import annotations

import pygame as _pg
from typing import Self, Optional

from ..base import *
from .. import profile
from .. import event, mouse

def _updateMouseStatus():
    from . import Button
    if type(GUIBase.g_hoveredObj) == Button:
        _pg.mouse.set_cursor(_pg.SYSTEM_CURSOR_HAND)
    else:
        _pg.mouse.set_cursor(_pg.SYSTEM_CURSOR_ARROW)

class GUIBase(event.EventObject):
    g_hovered = False
    g_hoveredObj: Optional[GUIBase] = None
    g_focusedObj: Optional[GUIBase] = None

    _debug_position_stack: list[Vec2] = []

    def __init__(self, u: float, v: float, width: float, height: float,
                 padding = profile.default_padding, border: Border = Border(0, colors.WHITE), no_register = False) -> None:
        self.surface = _pg.Surface((width*profile.surface_scale, height*profile.surface_scale), _pg.SRCALPHA)
        self.width, self.height = Vec2(width, height)
        self.pos = Vec2(
            profile.width/2 + profile.width/2 * u - self.width/2,
            profile.height/2 + profile.height/2 * v - self.height/2)

        self.padding = padding
        self.border = border

        self.hovered = False
        self.clicked = False
        self.focused = False

        self.attachTo: Optional[object] = None
        self.event_func: Optional[Callable] = None

        if not no_register:
            event.EventManager.register_update(type(self).on_hovered)
            event.EventManager.register_mousebuttonup(mouse.left, type(self).on_executed)
            event.EventManager.link_instance(self)

        if profile.isShowPos:
            GUIBase._debug_position_stack.append(self.pos)

    def update(self) -> None:
        if self.attachTo is None: return

    def draw(self, surface: Optional[_pg.Surface] = None) -> None:
        if surface is None: surface = self.surface
        rect = self.get_rect()
        rect.x *= profile.surface_scale
        rect.y *= profile.surface_scale
        rect.width *= profile.surface_scale
        rect.height *= profile.surface_scale

        if self.border.width > 0:
            border_rect = surface.get_rect()

            width = self.border.width*profile.surface_scale

            _pg.draw.rect(surface, self.border.color, border_rect, int(width))


    def _flush(self, surface: Optional[_pg.Surface] = None):
        """If surface is not specified, profile.surface will be used."""
        if surface is None:
            surface = profile.surface
            surface.blit(self.surface, (self.pos*profile.surface_scale).pos)
        else:
            surface.blit(self.surface, (self.pos*profile.surface_scale).pos)

    def get_rect(self):
        return _pg.Rect(
            self.pos.x*profile.surface_scale - self.padding.left*profile.surface_scale,
            self.pos.y*profile.surface_scale - self.padding.top*profile.surface_scale,
            self.width*profile.surface_scale + self.padding.left*profile.surface_scale + self.padding.right*profile.surface_scale,
            self.height*profile.surface_scale + self.padding.top*profile.surface_scale + self.padding.bottom*profile.surface_scale)

    # commons
    # def __init_subclass__(cls: type[Self]) -> None:


    @staticmethod
    def _reset_g_flag():
        GUIBase.g_hovered = False
        GUIBase.g_hoveredObj = None

    def _reset_flag(self):
        # self.hovered = False
        # self.clicked = False
        pass
    
    def _centering(self):
        self.pos.x -= self.width/2
        self.pos.y -= self.height/2

    def on_hovered(self):
        if self.attachTo is None: return

        mouse_pos = event.getMousePos()
        rect = self.get_rect()
        rect.x /= profile.surface_scale
        rect.y /= profile.surface_scale
        rect.width /= profile.surface_scale
        rect.height /= profile.surface_scale
        isCollide = _pg.Rect.collidepoint(rect, *mouse_pos)

        # print(self, isCollide)
        
        # TODO: temporary

        if GUIBase.g_hovered == False:
            if isCollide:
                GUIBase.g_hovered = True
                GUIBase.g_hoveredObj = self
                self.hovered = True
            else:
                self.hovered = False
        if self.hovered:
            if mouse.get_pressed().left:
                self.clicked = True
            else:
                self.clicked = False
        else:
            self.clicked = False

    def on_executed(self, e):
        if self.attachTo is None: return
        if self.event_func and self.hovered:
            self.event_func()