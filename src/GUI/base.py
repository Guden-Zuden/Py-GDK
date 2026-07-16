# import sys
# import pathlib
# sys.path.append(pathlib.Path().absolute().__str__())
import pygame as _pg
from typing import Self, Optional

from ..base import *
from .. import profile
from .. import event, mouse

print(profile.clock)

class GUIBase(event.EventObject):
    g_hovered = False
    g_focused: Optional[GUIBase] = None

    def __init__(self, u: float, v: float, width: float, height: float, padding: Optional[float] = None) -> None:
        self.u, self.v = u, v
        self.x = profile.width/2 + profile.width/2 * u - width/2
        self.y = profile.height/2 + profile.height/2 * v - height/2
        self.width, self.height = width, height
        self.padding = profile.default_padding if padding is None else padding

        self.hovered = False
        self.clicked = False
        self.focused = False

    def update(self): pass
    def draw(self): pass

    def get_rect(self):
        return _pg.Rect(self.x - self.padding, self.y - self.padding, self.width + self.padding*2, self.height + self.padding*2)

    # commons
    def __init_subclass__(cls: type[Self]) -> None:
        print(f"called __init_subclass__ cls: {cls}")
        event.EventManager.register_update(cls.on_hovered)
        event.EventManager.register_mousebuttondown(mouse.left, cls.on_click)
        # event.EventManager.link_instance(cls)

    @staticmethod
    def _reset_g_flag():
        GUIBase.g_hovered = False

    def _reset_flag(self):
        self.hovered = False
        self.clicked = False

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