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

default_fontsize: int = 20
default_font: Optional[_pg.font.Font] = None
default_padding = Padding(4)
default_textAttributes = TextAttributes("msgothic", 20, (255, 255, 255))
default_border = Border(0, colors.WHITE)
default_scrollbar_style = ScrollBarStyle()

sprite_size: int = 32

surface_size_locked = False
"""If true, surface size cannot be changed."""
surface_fill_screen = False
"""If false, surface size will be changed depending on the aspect ratio."""
surface_scale: int = 2
"""surface_scale must be set before calling init()"""

# === For debug ===
isCalcPerformance: bool = False
isShowPos: bool = False

import pathlib
_directory = pathlib.Path(__file__).parent
print(_directory)