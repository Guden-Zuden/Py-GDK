import pygame as _pg
from typing import Optional as _Optional
from dataclasses import dataclass as _dataclass
import copy as _copy

from ..base import *
from . import base as _base
from .. import profile as _profile
from .. import colors as _colors

class Text(_base.GUIBase):
    def __init__(self, u: float, v: float, text: str, textAttributes = _profile.default_textAttributes,
                 padding = _profile.default_padding, wrap_width: int = 0, border: Border = Border(0, _colors.WHITE), no_register = False) -> None:
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
        
        super().__init__(u, v, self.text_surface.width/_profile.surface_scale, self.text_surface.height/_profile.surface_scale, padding, border, no_register)
        self.surface = _pg.Surface(
            (self.textAttributes.OutlineWidth*_profile.surface_scale + self.width*_profile.surface_scale, 
             self.textAttributes.OutlineWidth*_profile.surface_scale + self.height*_profile.surface_scale), flags=_pg.SRCALPHA)
    
    def update(self):
        super().update()
        if (self.text != self.__private_text
            or self.wrap_width != self.__private_wrap_width
            or self.textAttributes != self.__private_textAttributes):
            self.__private_text = self.text
            self.__private_wrap_width = self.__private_wrap_width
            self.__private_textAttributes = self.textAttributes
            self.text_surface = _pg.sysfont.SysFont(*self.textAttributes.getFontStyle()).render(
                self.text, True, *self.textAttributes.getTextColors(), wraplength=self.wrap_width*_profile.surface_scale)
            self.width = self.text_surface.get_width()/_profile.surface_scale
            self.height = self.text_surface.get_height()/_profile.surface_scale
            self.surface = _pg.Surface(self.text_surface.get_size(), _pg.SRCALPHA)
            self.pos = _base._uvTopos((self.u, self.v), self.width, self.height)

    def draw(self, surface: _Optional[_pg.Surface] = None):
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