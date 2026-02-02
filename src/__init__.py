from . import Core
from . import Profile
from . import Timer
from . import Event
from . import Entity, Components, Scene, Text
from . import Sprite
from .Log import *
from .Animator import *
from . import Tilemap

import pygame as pg

def init(title: str, fps: int, width: int, height: int, mapSprite_size: int):
    Profile.title = title
    Profile.fps = fps
    Profile.width = width
    Profile.height = height
    Profile.sprite_size = mapSprite_size
    Core.init()

def run():
    Core.run()