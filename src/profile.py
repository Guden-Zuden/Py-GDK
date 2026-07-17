"""
Contains Values to be used globally.
"""

import pygame as _pg

from .base import *

screen: Optional[_pg.Surface] = None
surface: _pg.Surface = NullSurface([0,0])
clock: Optional[_pg.time.Clock] = None

title: str = "GameDeveloperKits"
fps: int = 60
width: int = 400
height: int = 300
window_width: int = 400
window_height: int = 300

# user_instance: Optional[Any] = None

default_fontsize: int = 20
default_font: Optional[_pg.font.Font] = None
default_padding = Padding(4)
default_textAttributes = TextAttributes("msgothic", 20, (255, 255, 255))
default_border = Border(0, colors.WHITE)

sprite_size: int = 32

isCalcPerformance: bool = False