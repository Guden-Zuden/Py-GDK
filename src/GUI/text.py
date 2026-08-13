import pygame as _pg
from typing import Optional
from dataclasses import dataclass
import copy

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
        if self.textAttributes.OutlineColor:
            self.outline_surface = _pg.sysfont.SysFont(*self.textAttributes.getFontStyle()).render(
                text, True, self.textAttributes.OutlineColor, wraplength=wrap_width)
        else:
            self.outline_surface = None
        
        super().__init__(u, v, self.text_surface.width/profile.surface_scale, self.text_surface.height/profile.surface_scale, padding, border, no_register)
        self.surface = _pg.Surface(
            (self.textAttributes.OutlineWidth*2 + self.width*profile.surface_scale, 
             self.textAttributes.OutlineWidth*2 + self.height*profile.surface_scale), flags=_pg.SRCALPHA)
    
    def update(self):
        super().update()
        if (self.text != self.__private_text or self.wrap_width != self.__private_wrap_width
            or self.textAttributes != self.__private_textAttributes):
            self.text_surface = _pg.sysfont.SysFont(*self.textAttributes.getFontStyle()).render(
                self.text, True, *self.textAttributes.getTextColors(), wraplength=self.wrap_width*profile.surface_scale)

    def draw(self, surface: Optional[_pg.Surface] = None):
        # if surface is None: surface = self.surface
        super().draw(surface)
        pos = Vec2(self.surface.get_width()/2 - self.text_surface.get_width()/2,
                   self.surface.get_height()/2 - self.text_surface.get_height()/2)

        if self.outline_surface and surface:
            temp = int(self.textAttributes.OutlineWidth*2)
            for dx in range(-temp, temp + 1):
                for dy in range(-temp, temp + 1):
                    self.surface.blit(self.outline_surface, 
                                      (pos + Vec2(dx, dy)).pos) 

        self.surface.blit(self.text_surface, pos.pos)
        if surface: self._flush(surface)
        else: self._flush()