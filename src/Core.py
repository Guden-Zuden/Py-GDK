from . import Profile
from . import Event
from . import Key
from . import Scene, Entity
from . import Sprite
from .Timer import ScopedTimer
from . import Layer
from .Log import *

import pygame as _pygame
import sys as _sys

def init():
    _pygame.init()
    _pygame.display.set_caption(Profile.title)
    Profile.clock = _pygame.time.Clock()
    Profile.default_font = _pygame.font.Font(None, Profile.default_fontsize)
    Profile.surface = _pygame.Surface((Profile.width, Profile.height), flags=_pygame.SRCALPHA)
    Profile.screen = _pygame.display.set_mode((Profile.window_width, Profile.window_height), flags=_pygame.RESIZABLE)

    @Event.OnWindowResized()
    def reflectWindowSize(e):
        Log.debug(e)
        Profile.window_width, Profile.window_height = e.x, e.y

def recreate_surface():
    Profile.surface = _pygame.Surface([Profile.window_width, Profile.window_height], flags=_pygame.SRCALPHA)

def run():
    assert Profile.surface is not None
    assert Profile.screen is not None
    assert Profile.clock is not None
    while True:
        fps_clock = None
        if Profile.isCalcPerformance:
            fps_clock = ScopedTimer()

        Event._updateKeyEvents()
        Event._updateMouseEvents()
        Event._updateMousePos()
        Event.Input.update()

        Event.EventManager.update(_pygame.event.get())
        Event.EventManager.dispatch()
        Event.EventManager.dispatch_onUpdate()
            
        Profile.surface.fill((0, 0, 0))

        Scene.SceneManager.update()
        Scene.SceneManager.draw()

        Layer.LayerManager.update()
        Layer.LayerManager.draw()

        Profile.screen.fill((0, 0, 0))
        Profile.screen.blit(Profile.surface, (0, 0), _pygame.Rect(-Profile.window_width/2+Profile.width/2, -Profile.window_height/2+Profile.height/2, Profile.window_width, Profile.window_height))
        _pygame.draw.rect(Profile.screen, (255, 255, 255), _pygame.Rect(Profile.window_width/2-Profile.width/2-1, Profile.window_height/2-Profile.height/2-1, Profile.width+2, Profile.height+2), 1)


        _pygame.display.update()
        Profile.clock.tick(Profile.fps)