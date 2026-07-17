import pygame as _pg
from typing import Optional
from dataclasses import dataclass

from ..base import *
from . import base
from .. import profile

class Text(base.GUIBase):
    def __init__(self, u: float, v: float, text: str, textAttributes = profile.default_textAttributes,
                 padding = profile.default_padding, wrap_width: int = 0) -> None:
        self.text = text
        self.wrap_width = wrap_width
        self.textAttributes = textAttributes
        
        self.__private_text = text
        self.__private_wrap_width = wrap_width
        self.__private_textAttributes = textAttributes

        self.text_surface = _pg.sysfont.SysFont(*self.textAttributes.getFontStyle()).render(
            text, True, *self.textAttributes.getTextColors(), wraplength=wrap_width)
        super().__init__(u, v, self.text_surface.width, self.text_surface.height, padding)
    
    def update(self):
        if (self.text != self.__private_text or self.wrap_width != self.__private_wrap_width
            or self.textAttributes != self.__private_textAttributes):
            self.text_surface = _pg.sysfont.SysFont(*self.textAttributes.getFontStyle()).render(
                self.text, True, *self.textAttributes.getTextColors(), wraplength=self.wrap_width)

    def draw(self, surface: Optional[_pg.Surface] = None):
        if surface is None: surface = profile.surface
        surface.blit(self.text_surface, [*self.pos])
        if self.focused:
            _pg.draw.rect(surface, (255,255,255,70), self.get_rect(), 1) # TODO: temporary