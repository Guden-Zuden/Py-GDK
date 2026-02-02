from . import Profile
from . import Components
from . import Utils

import pygame as _pygame
from dataclasses import dataclass
from enum import Enum

@dataclass
class TextAttribute:
    font: str
    size: int
    text_color: _pygame.Color | tuple[int, int, int, int] | tuple[int, int, int]
    background_color: _pygame.Color | tuple[int, int, int, int] | tuple[int, int, int] | None = None
    antialias: bool = True
    bold: bool = False
    italic: bool = False

    def createFont(self) -> _pygame.font.Font:
        font = _pygame.font.SysFont(self.font, self.size, self.bold, self.italic)
        return font

# ===== Text =====
class Text(Components.ComponentBase):
    def __init__(self, textAttribute: TextAttribute, text: str, x: float, y: float, anchor: Utils.Anchor=Utils.Anchor.default) -> None:
        super().__init__(x, y)
        self.textAttr = textAttribute
        self.font = self.textAttr.createFont()
        self.text = text
        self.anchor: Utils.Anchor = anchor

    def draw(self, offset_x: float, offset_y: float):
        assert Profile.screen is not None
        x, y = self.x - offset_x, self.y - offset_y
        surf = self.font.render(self.text, self.textAttr.antialias, self.textAttr.text_color, self.textAttr.background_color)
        Profile.screen.blit(surf, Utils.applyAnchor(x, y, surf.get_width(), surf.get_height(), self.anchor))