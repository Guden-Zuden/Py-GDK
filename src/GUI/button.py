from src.colors import WHITE

from ..base import *
from . import base
from .text import *
from .box import *

import pygame as _pg
import copy

class Button(Box):
    def __init__(self, u: float, v: float, width: float, height: float,
                 color: gdk_color, border = profile.default_border,
                 padding = profile.default_padding, child: base.GUIBase | None = None) -> None:
        super().__init__(u, v, width, height, color, border, padding, child)

    def update(self):
        if self.hovered:
            box = copy.deepcopy(self)
            box.color.a -= 70
            box.draw()