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
        self.displayed_img_surface = _pg.transform.smoothscale(self.img_surface, (width*profile.surface_scale, height*profile.surface_scale))
        

        super().__init__(u, v, width, height, padding, border, no_register)

        self.child = child
        if self.child:
            self.child.pos = Vec2(
                self.size.width/2 - self.child.size.width/2,
                self.size.height/2 - self.child.size.height/2
            )

    def resize(self):
        """
        _resize() is called in update(), but this method must be called after resizing.\n
        This method resizes the image while preserving its aspect ratio.\n
        Please call this method after changing width only. The height will be ignored.
        """
        if not self.size.is_dirty():
            return
        self.size.height = self.img_surface.get_height() * self.size.width / self.img_surface.get_width()
        self.displayed_img_surface = _pg.transform.smoothscale(self.img_surface, (self.size*profile.surface_scale).tuple)

    def resize_strict(self):
        """
        _resize() is called in update(), but this method must be called after resizing.\n
        This method resizes the image without preserving its aspect ratio.
        """
        if not self.size.is_dirty():
            return
        self.displayed_img_surface = _pg.transform.smoothscale(self.img_surface, (self.size*profile.surface_scale).tuple)

    def update(self):
        from ..time import BenchMark
        with BenchMark("image.update()"):
            super().update()

    def draw(self, surface: _Optional[_pg.Surface] = None) -> None:
        super().draw(surface)

        self.surface.blit(self.displayed_img_surface)

        if self.child:
            self.child.pos = Vec2(
                self.size.width/2 - self.child.size.width/2,
                self.size.height/2 - self.child.size.height/2
            )

            self.child.draw(self.surface)

        if surface: self._flush(surface)
        else: self._flush()