"""
There are values to be used globally.
"""

import pygame as _pygame
from typing import Optional

screen: Optional[_pygame.Surface] = None
surface: Optional[_pygame.Surface] = None
clock: Optional[_pygame.time.Clock] = None

title: str = "GameDeveloperKits"
fps: int = 60
width: int = 400
height: int = 300
window_width: int = 400
window_height: int = 300

default_fontsize: int = 20
default_font: Optional[_pygame.font.Font] = None

sprite_size: int = 32

isCalcPerformance: bool = False