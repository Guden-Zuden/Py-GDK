import pygame as _pg
from typing import Optional
from dataclasses import dataclass

from ..base import *
from . import base
from .. import profile

class Text(base.GUIBase):
    def __init__(self, u: float, v: float, text: str, textAttributes = profile.default_textAttributes,
                 padding = profile.default_padding, wrap_width: int = 0, border: Border = Border(0, colors.WHITE), no_register = False) -> None:
        self.text = text
        self.wrap_width = wrap_width
        self.textAttributes = textAttributes
        
        self.__private_text = text
        self.__private_wrap_width = wrap_width
        self.__private_textAttributes = textAttributes

        self.text_surface = _pg.sysfont.SysFont(*self.textAttributes.getFontStyle()).render(
            text, True, *self.textAttributes.getTextColors(), wraplength=wrap_width)
        
        super().__init__(u, v, self.text_surface.width/profile.surface_scale, self.text_surface.height/profile.surface_scale, padding, border, no_register)
    
    def update(self):
        super().update()
        if (self.text != self.__private_text or self.wrap_width != self.__private_wrap_width
            or self.textAttributes != self.__private_textAttributes):
            self.text_surface = _pg.sysfont.SysFont(*self.textAttributes.getFontStyle()).render(
                self.text, True, *self.textAttributes.getTextColors(), wraplength=self.wrap_width*profile.surface_scale)

    def draw(self, surface: Optional[_pg.Surface] = None):
        # if surface is None: surface = self.surface
        super().draw(surface)
        self.surface.blit(self.text_surface, (0,0))
        if surface: self._flush(surface)
        else: self._flush()