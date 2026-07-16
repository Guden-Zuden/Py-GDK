import pygame as _pg
from typing import Optional
from dataclasses import dataclass

from . import base
from .. import profile


@dataclass
class TextAttributes:
    Font: str
    FontSize: float
    TextColor: base.gdk_color
    BackGroundColor: Optional[base.gdk_color] = None

    Bold: bool = False
    Italic: bool = False

    def getFontStyle(self):
        return (
            self.Font, self.FontSize, self.Bold, self.Italic
        )
    def getTextColors(self):
        return (
            self.TextColor, self.BackGroundColor
        )

default_textAttributes = TextAttributes("msgothic", 20, (255, 255, 255))

class Text(base.GUIBase):
    def __init__(self, u: float, v: float, text: str, textAttributes: TextAttributes = default_textAttributes, padding: Optional[float] = None, wrap_width: int = 0) -> None:
        self.text = text
        self.wrap_width = wrap_width
        self.textAttributes = textAttributes
        
        self.__private_text = text
        self.__private_wrap_width = wrap_width
        self.__private_textAttributes = textAttributes

        self.surface = _pg.sysfont.SysFont(*self.textAttributes.getFontStyle()).render(
            text, True, *self.textAttributes.getTextColors(), wraplength=wrap_width)
        super().__init__(u, v, self.surface.width, self.surface.height, padding)
    
    def update(self):
        if (self.text != self.__private_text or self.wrap_width != self.__private_wrap_width
            or self.textAttributes != self.__private_textAttributes):
            self.surface = _pg.sysfont.SysFont(*self.textAttributes.getFontStyle()).render(
                self.text, True, *self.textAttributes.getTextColors(), wraplength=self.wrap_width)

    def draw(self):
        assert profile.surface
        profile.surface.blit(self.surface, [self.x, self.y])
        if self.focused:
            _pg.draw.rect(profile.surface, (255,255,255,70), self.get_rect(), 1) # TODO: temporary