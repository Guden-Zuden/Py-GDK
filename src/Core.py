from . import profile
from . import event
from . import Scene

import pygame as _pg
import sys as _sys

def init():
    _pg.init()
    _pg.mixer.init()
    _pg.display.set_caption(profile.title)
    profile.clock = _pg.time.Clock()
    profile.default_font = _pg.font.Font(None, profile.default_fontsize)
    profile.surface = _pg.Surface((profile.width, profile.height), flags=_pg.SRCALPHA)
    profile.screen = _pg.display.set_mode((profile.window_width, profile.window_height), flags=_pg.RESIZABLE)

def recreate_surface():
    profile.surface = _pg.Surface([profile.window_width, profile.window_height], flags=_pg.SRCALPHA)

def run():
    assert profile.surface is not None
    assert profile.screen is not None
    assert profile.clock is not None
    while True:
        fps_clock = None
        # if profile.isCalcPerformance:
            # fps_clock = ScopedTimer()

        event._updateKeyEvents()
        event._updateMouseEvents()
        event._updateMousePos()
        event.Input.update()

        event.EventManager.update(_pg.event.get())
        event.EventManager.dispatch()
            
        profile.surface.fill((0, 0, 0))

        # Scene.SceneManager.update()
        # Scene.SceneManager.draw()

        # Layer.LayerManager.update()
        # Layer.LayerManager.draw()

        profile.screen.fill((0, 0, 0))
        profile.screen.blit(profile.surface, (0, 0), _pg.Rect(-profile.window_width/2+profile.width/2, -profile.window_height/2+profile.height/2, profile.window_width, profile.window_height))
        _pg.draw.rect(profile.screen, (255, 255, 255), _pg.Rect(profile.window_width/2-profile.width/2-1, profile.window_height/2-profile.height/2-1, profile.width+2, profile.height+2), 1)


        _pg.display.update()
        profile.clock.tick(profile.fps)

def quit():
    _pg.quit()
    _sys.exit()