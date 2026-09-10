"""Normally, we import this file with wild card."""
from __future__ import annotations

import pygame as _pg
from typing import (
    Self as _Self,
    Optional as _Optional,
    Callable as _Callable,
    overload as _overload
    )
from enum import (
    Flag as _Flag,
    auto as _auto
)
import copy as _copy

from ..base import *
from .. import profile
from .. import event, mouse
from .. import colors

def _posTouv(pos: Vec2, width: float, height: float) -> tuple[float, float]:
    u = 2 / profile.width * (pos.x + width - profile.width/2)
    v = 2 / profile.height * (pos.y + height - profile.height/2)
    return (u, v)

@_overload
def _uvTopos(uv: tuple[float, float], width: float, height: float) -> Vec2: ...

@_overload
def _uvTopos(uv: tuple[float, float], width: float, height: float, anchor: Anchor) -> Vec2: ...

def _uvTopos(uv: tuple[float, float], width: float, height: float, anchor: _Optional[Anchor] = None) -> Vec2:
    pos = Vec2(
        profile.width/2 + profile.width/2 * uv[0] - width/2,
        profile.height/2 + profile.height/2 * uv[1] - height/2
    )
    if anchor is None:
        pass # do nothing
    else:
        if anchor & Anchor.LEFT:
            pos.x += width/2
        if anchor & Anchor.RIGHT:
            pos.x -= width/2
        if anchor & Anchor.TOP:
            pos.y += height/2
        if anchor & Anchor.BOTTOM:
            pos.y -= height/2

    return pos

def _updateMouseStatus():
    from . import Button, ImageButton
    if isinstance(GUIBase.g_hoveredObj, (Button, ImageButton)):
        _pg.mouse.set_cursor(_pg.SYSTEM_CURSOR_HAND)
    else:
        _pg.mouse.set_cursor(_pg.SYSTEM_CURSOR_ARROW)

######################################
#############  GUI Base  #############
######################################
class GUIBase(event.EventObject):
    # for debug =====
    update_count = 0
    draw_count   = 0
    # ===============

    g_hoveredObj: _Optional[GUIBase] = None
    g_focusedObj: _Optional[GUIBase] = None

    _debug_position_stack: list[Vec2] = []
    
    def __init__(self, u: float, v: float, width: float, height: float,
                 padding = profile.default_padding, border: Border = Border(0, colors.WHITE), no_register = False) -> None:
        self.u, self.v = u, v
        self.size = Vec2(width, height)
        self.pos = Vec2(
            profile.width/2 + profile.width/2 * u - self.size.width/2,
            profile.height/2 + profile.height/2 * v - self.size.height/2)

        self.padding = padding
        self.border = border

        self.hovered = False
        self.clicked = False
        self.focused = False

        self.parent: _Optional[object] = None
        self.children: list[GUIBase] = []

        self.event_func: _Optional[_Callable] = None

        self.no_register = no_register

        if profile.is_show_gui_positions:
            GUIBase._debug_position_stack.append(self.pos)

        self.create_surface()

    def _regist_events(self):
        if not self.no_register:
            for component in self.children:
                component._regist_events()
            event.EventManager.register_update(type(self).on_hovered)
            event.EventManager.register_mousebuttonup(mouse.left, type(self).on_executed)
            event.EventManager.link_instance(self)

    def create_surface(self):
        self.surface = _pg.Surface((self.size*profile.surface_scale).tuple, _pg.SRCALPHA)
        self.border_surface = _pg.Surface((self.size*profile.surface_scale).tuple, _pg.SRCALPHA)
        
    def _centering(self):
        self.pos.x -= self.size.width/2
        self.pos.y -= self.size.height/2

    def update(self) -> None:
        GUIBase.update_count += 1

        self.on_update()

        if self.size.is_dirty():
            self.create_surface()
            self.size.reset()
        
        if self.parent is None: return

    def draw(self, surface: _Optional[_pg.Surface] = None) -> None:
        GUIBase.draw_count += 1
        if surface is None: surface = self.surface
        self.on_draw(surface)
        self.surface.fill((0,0,0,0))

        if self.border.width > 0:
            border_rect = surface.get_rect()

            width = int(self.border.width*profile.surface_scale)

            if width > 0: _pg.draw.rect(self.border_surface, self.border.color, border_rect, width)

    def _flush(self, surface: _Optional[_pg.Surface] = None):
        """If surface is not specified, profile.surface will be used."""
        if surface is None:
            surface = profile.surface

        surface.blit(self.surface, (self.pos * profile.surface_scale).pos)
        surface.blit(self.border_surface, (self.pos * profile.surface_scale).pos)

    def stick(self, gui_obj: GUIBase, dir: Direction):
        self.pos.x = gui_obj.pos.x + gui_obj.size.width/2 - self.size.width/2
        self.pos.y = gui_obj.pos.y + gui_obj.size.height/2 - self.size.height/2

        if dir & Direction.TOP:
            self.pos.y = gui_obj.pos.y - self.size.height
        elif dir & Direction.BOTTOM:
            self.pos.y = gui_obj.pos.y + gui_obj.size.height

        if dir & Direction.LEFT:
            self.pos.x = gui_obj.pos.x - self.size.width
        elif dir & Direction.RIGHT:
            self.pos.x = gui_obj.pos.x + gui_obj.size.width
        return self

    def get_rect(self):
        return _pg.Rect(
            self.pos.x*profile.surface_scale - self.padding.left*profile.surface_scale,
            self.pos.y*profile.surface_scale - self.padding.top*profile.surface_scale,
            self.size.width*profile.surface_scale + self.padding.left*profile.surface_scale + self.padding.right*profile.surface_scale,
            self.size.height*profile.surface_scale + self.padding.top*profile.surface_scale + self.padding.bottom*profile.surface_scale)

    def get_size(self):
        return (self.size.width, self.size.height)

    @staticmethod
    def _reset_g_flag():
        GUIBase.g_hoveredObj = None

    def attach(self, gui: GUIBase):
        gui.parent = self
        self.children.append(gui)

    def get_top(self):
        gui = self

        while isinstance(gui.parent, GUIBase):
            gui = gui.parent

        return gui

    def get_parents(self):
        parents: list[GUIBase] = []
        gui = self

        while isinstance(gui.parent, GUIBase):
            gui = gui.parent
            parents.append(gui)

        return parents

    # events    
    def on_hovered(self):
        if self.parent is None: return

        mouse_pos = event.getMousePos()
        rect = self.get_rect()
        rect.x /= profile.surface_scale
        rect.y /= profile.surface_scale
        rect.width /= profile.surface_scale
        rect.height /= profile.surface_scale

        for parent in self.get_parents():
            rect.x += parent.pos.x
            rect.y += parent.pos.y

        isCollide = _pg.Rect.collidepoint(rect, *mouse_pos)

        if GUIBase.g_hoveredObj is None:
            if isCollide:
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
        if not isCollide:
            self.hovered = False

    def on_executed(self, e):
        if self.parent is None: return
        if self.event_func and self.hovered:
            self.event_func()

    def on_update(self):
        pass
    def on_draw(self, surface: _pg.Surface):
        pass

    # setters
    def set_pos(self, x: int | float, y: int | float):
        self.pos = Vec2(x, y)

    def set_uv(self, u: float, v: float):
        self.u, self.v = u, v
        self.pos = _uvTopos((u, v), self.size.width, self.size.height)

    def set_size(self, width: float, height: float):
        self.size.width, self.size.height = width, height

    def sync_size_to(self, component: GUIBase):
        self.size = component.size

    #

__all__ = [
    "Direction"
]