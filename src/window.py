from .base import *
import pygame as _pg
from typing import (
    Optional as _Optional
)

from . import event as _event

class Window(_event.EventObject):
    def __init__(
        self,
        title: str,
        window_width: int,
        window_height: int,
        surface_width: int,
        surface_height: int,
        allow_high_dpi: bool = False,
        utility: bool = False,
    ) -> None:
        self.window = _pg.Window(
            title,
            (window_width, window_height),
            allow_high_dpi=allow_high_dpi,
            utility=utility)
        self.surface = _pg.Surface(
            (surface_width, surface_height), _pg.SRCALPHA
        )
        self.window_width = window_width
        self.window_height = window_height
        self.surface_width = surface_width
        self.surface_height = surface_height

    def _get_actual_size(self):
        old_width = self.surface.width
        old_height = self.surface.height
        max_width = self.window_width
        max_height = self.window_height

        scaleX = max_width / old_width
        scaleY = max_height / old_height
        scale = min(scaleX, scaleY)

        actual_width = old_width * scale
        actual_height = old_height * scale
        print(actual_width, actual_height)
        return Vec2(actual_width, actual_height)

    def get_mousePos(self):
        mx, my = _pg.mouse.get_pos()
        actual_size = self._get_actual_size()
        surface_x = self.window_width/2 - actual_size.x/2
        surface_y = self.window_height/2 - actual_size.y/2

        return Vec2(
            (mx - surface_x) * (self.surface.width / actual_size.x), 
            (my - surface_y) * (self.surface.height / actual_size.y))

    def recreate_surface(self, width: int, height: int):
        self.surface = _pg.Surface((width, height), _pg.SRCALPHA)
        
    def update(self):
        pass

    def draw(self):
        actual_size = self._get_actual_size()
        surface_x = self.window_width/2 - actual_size.x/2
        surface_y = self.window_height/2 - actual_size.y/2
        _surface = _pg.transform.smoothscale(self.surface, actual_size.tuple)
        self.window.get_surface().blit(
            _surface, (surface_x, surface_y)
        )
        self.window.flip()

    @_event.OnWindowResized()
    def on_resized(self, e):
        self.window_width = e.x
        self.window_height = e.y
