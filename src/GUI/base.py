# import sys
# import pathlib
# sys.path.append(pathlib.Path().absolute().__str__())
import pygame as _pg
from typing import Self, Optional

from ..base import *
from .. import profile
from .. import event, mouse

class GUIBase(event.EventObject):
    g_hovered = False
    g_focused: Optional[GUIBase] = None

    def __init__(self, u: float, v: float, width: float, height: float, padding = profile.default_padding) -> None:
        self.pos = Vec2(
            profile.width/2 + profile.width/2 * u - width/2,
            profile.height/2 + profile.height/2 * v - height/2)
        self.width, self.height = Vec2(width, height)
        self.padding = padding

        self.hovered = False
        self.clicked = False
        self.focused = False

    def update(self) -> None: pass
    def draw(self, surface: Optional[_pg.Surface] = None) -> None: pass

    def get_rect(self):
        return _pg.Rect(
            self.pos.x - self.padding.left,
            self.pos.y - self.padding.top,
            self.width + self.padding.left + self.padding.right,
            self.height + self.padding.top + self.padding.bottom)

    # commons
    def __init_subclass__(cls: type[Self]) -> None:
        event.EventManager.register_update(cls.on_hovered)
        event.EventManager.register_mousebuttondown(mouse.left, cls.on_click)

    @staticmethod
    def _reset_g_flag():
        GUIBase.g_hovered = False

    def _reset_flag(self):
        self.hovered = False
        self.clicked = False
    
    def _centering(self):
        self.pos.x -= self.width/2
        self.pos.y -= self.height/2

    def on_hovered(self):
        mouse_pos = event.getMousePos()
        isCollide = _pg.Rect.collidepoint(self.get_rect(), *mouse_pos)

        if GUIBase.g_hovered == False:
            if isCollide:
                GUIBase.g_hovered = True
                self.hovered = True

    def on_click(self, e):
        if self.hovered:
            self.clicked = True

            if GUIBase.g_focused is not None and GUIBase.g_focused is not self:
                GUIBase.g_focused.focused = False
            
            GUIBase.g_focused = self
            self.focused = True

        if not GUIBase.g_hovered:
            self.focused = False
            GUIBase.g_focused = None