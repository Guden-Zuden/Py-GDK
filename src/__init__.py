from . import core
from . import profile
from . import event, key, mouse
from . import layer

from . import GUI
from . import Scene

from .utils import *

import pygame
from typing import Optional, Any
from os import PathLike

def init(title: str = "GameDeveloperKits", fps: int = 60, width: int = 600, height: int = 400, mapSprite_size: int = 32, window_width: Optional[int] = None, window_height: Optional[int] = None):
    print("This Game Developer Kits is using pygame.")
    profile.title = title
    profile.fps = fps
    profile.width = width
    profile.height = height
    profile.sprite_size = mapSprite_size

    if window_width and window_height:
        profile.window_width, profile.window_height = window_width, window_height
    else:
        profile.window_width, profile.window_height = profile.width, profile.height

    core.init()

def get_availableFonts():
    for font in pygame.font.get_fonts():
        print(font)

def run():
    core.run()