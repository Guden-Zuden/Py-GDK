from .Utils import *

import pygame as _pygame
from dataclasses import dataclass

@dataclass
class TextAttribute:
    font: str
    size: int
    text_color: gdk_color
    background_color: gdk_color | None = None
    antialias: bool = True
    bold: bool = False
    italic: bool = False

    def createFont(self) -> _pygame.font.Font:
        font = _pygame.font.SysFont(self.font, self.size, self.bold, self.italic)
        return font