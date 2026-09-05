from .base import *
from .GUI.base import *
from .utils import *

from . import profile
from . import layer
from . import GUI
from . import Scene
from . import event, key, mouse
from . import colors
from . import sound
from . import time

# experimental
from . import Debugger

import pygame
from typing import Optional as _Optional

def init(title: str = "GameDeveloperKits", fps: int = 60, width: int = 600, height: int = 400, mapSprite_size: int = 32, window_width: _Optional[int] = None, window_height: _Optional[int] = None):
    from . import core
    print("This Game Developer Kits is using pygame-ce.")
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
    import pygame as pg
    for font in pg.font.get_fonts():
        print(font)

def run():
    from . import core
    core.run()

@event.OnWindowResized()
def on_windowResized(e):
    from . import core
    profile.window_width = e.x
    profile.window_height = e.y

    new_width = 0
    new_height = 0

    if profile.surface_fill_screen:
        new_width = profile.window_width
        new_height = profile.window_height
    else:
        old_width = profile.width
        old_height = profile.height
        max_width = profile.window_width
        max_height = profile.window_height

        scaleX = max_width / old_width
        scaleY = max_height / old_height
        scale = min(scaleX, scaleY)

        new_width = old_width * scale
        new_height = old_height * scale

    core.recreate_surface(new_width, new_height)

    for _layer in layer.LayerManager.layer_stack:
        for gui_component in _layer._GUIComponent_stack:
            gui_component.pos = Vec2(
                profile.width/2 + profile.width/2 * gui_component.u - gui_component.width/2,
                profile.height/2 + profile.height/2 * gui_component.v - gui_component.height/2)