from . import Profile
from . import Event
from . import Key
from . import Scene, Entity, Text
from . import Sprite
from .Timer import ScopedTimer

import pygame as _pygame
import sys as _sys

def init():
    _pygame.init()
    _pygame.display.set_caption(Profile.title)
    Profile.clock = _pygame.time.Clock()
    Profile.default_font = _pygame.font.Font(None, Profile.default_fontsize)
    Profile.screen = _pygame.display.set_mode((Profile.width, Profile.height))

def run():
    assert Profile.screen is not None
    while True:
        a = ScopedTimer()

        Event._updateKeyEvents()
        Event.Input.update()

        Event.EventManager.update(_pygame.event.get())
        Event.EventManager.dispatch()
            
        Profile.screen.fill((0, 0, 0))

        Scene.SceneManager.update()
        Scene.SceneManager.draw()

        _pygame.display.update()
        Profile.clock.tick(Profile.fps)