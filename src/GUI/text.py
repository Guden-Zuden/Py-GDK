import pygame as _pg

from . import base
from .. import profile

class Text(base.GUIBase):
    def __init__(self, u: float, v: float, text: str) -> None:
        self.surface = _pg.sysfont.SysFont("msgothic", 20).render(text, True, (255,255,255))
        super().__init__(u, v, self.surface.width, self.surface.height)
    
    def draw(self):
        assert profile.surface
        profile.surface.blit(self.surface, [self.x, self.y])