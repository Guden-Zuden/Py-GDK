from . import Core
from . import Profile
from . import Timer
from . import Event
from . import Entity, Components, Scene, Text
from . import Sprite
from .Log import *
from .Animator import *
from . import Tilemap

import pygame
from typing import Optional

def init(title: str = "GameDeveloperKits", fps: int = 60, width: int = 600, height: int = 400, mapSprite_size: int = 32, window_width: Optional[int] = None, window_height: Optional[int] = None):
    Profile.title = title
    Profile.fps = fps
    Profile.width = width
    Profile.height = height
    Profile.sprite_size = mapSprite_size

    if window_width and window_height:
        Profile.window_width, Profile.window_height = window_width, window_height
    else:
        Profile.window_width, Profile.window_height = Profile.width, Profile.height

    Core.init()

def run():
    Core.run()