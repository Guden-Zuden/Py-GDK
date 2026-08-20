from ..base import *
from .. import profile
from .. import colors
from . import base

import pygame as _pg
import pathlib
from typing import (
    Optional as _Optional
)

class Image(base.GUIBase):
    def __init__(self, u: float, v: float, img_filepath: str | pathlib.Path, width: float,
                 padding=profile.default_padding, border: base.Border = Border(0, colors.WHITE),
                 child: _Optional[base.GUIBase] = None, no_register = False) -> None:
        try:
            self.img_surface = _pg.image.load(img_filepath).convert_alpha()
        except FileNotFoundError as e:
            print(f"[Image.__init__] {e}")
            self.img_surface = _pg.image.load("src/assets/img/NoImage.png").convert_alpha()

        height = self.img_surface.get_height() * width / self.img_surface.get_width()
        self.img_surface = _pg.transform.smoothscale(self.img_surface, (width*profile.surface_scale, height*profile.surface_scale))

        super().__init__(u, v, width, height, padding, border, no_register)

        self.child = child
        if self.child:
            self.child.pos = Vec2(
                self.width/2 - self.child.width/2,
                self.height/2 - self.child.height/2
            )

    def resize(self):
        self.height = self.img_surface.get_height() * self.width / self.img_surface.get_width()
        self.img_surface = _pg.transform.smoothscale(self.img_surface, (self.width*profile.surface_scale, self.height*profile.surface_scale))
        self.surface = _pg.Surface((self.width*profile.surface_scale, self.height*profile.surface_scale), _pg.SRCALPHA)

    def resize_strict(self):
        self.img_surface = _pg.transform.smoothscale(self.img_surface, (self.width*profile.surface_scale, self.height*profile.surface_scale))
        self.surface = _pg.Surface((self.width*profile.surface_scale, self.height*profile.surface_scale), _pg.SRCALPHA)

    def update(self):
        super().update()

    def draw(self, surface: _Optional[_pg.Surface] = None) -> None:
        super().draw(surface)

        self.surface.blit(self.img_surface)

        if self.child:
            self.child.pos = Vec2(
                self.width/2 - self.child.width/2,
                self.height/2 - self.child.height/2
            )

            self.child.draw(self.surface)

        if surface: self._flush(surface)
        else: self._flush()