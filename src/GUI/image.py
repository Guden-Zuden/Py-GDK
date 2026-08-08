from ..base import *
from .. import profile
from .. import colors
from . import base

import pygame as _pg
import pathlib

class Image(base.GUIBase):
    def __init__(self, u: float, v: float, img_filepath: str | pathlib.Path, width: float,
                 padding=profile.default_padding, border: base.Border = Border(0, colors.WHITE),
                 child: Optional[base.GUIBase] = None, no_register = False) -> None:
        try:
            self.img_surface = _pg.image.load(img_filepath).convert_alpha()
        except FileNotFoundError as e:
            print(f"[Image.__init__] {e}")
            self.img_surface = _pg.image.load("src/assets/img/NoImage.png").convert_alpha()

        height = self.img_surface.get_height() * width / self.img_surface.get_width()
        self.img_surface = _pg.transform.smoothscale(self.img_surface, (width*2, height*2))

        super().__init__(u, v, width, height, padding, border, no_register)

        self.child = child
        if self.child:
            self.child.pos = Vec2(
                self.width/2 - self.child.width/2,
                self.height/2 - self.child.height/2
            )

    def update(self):
        super().update()

    def draw(self, surface: Optional[_pg.Surface] = None) -> None:
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