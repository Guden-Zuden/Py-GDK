"""
Contains Values to be used globally.
"""

import pygame as _pg
from typing import Optional, Any

screen: Optional[_pg.Surface] = None
surface: Optional[_pg.Surface] = None
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
default_padding: float = 4

sprite_size: int = 32

isCalcPerformance: bool = False