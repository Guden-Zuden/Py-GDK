from .base import *
from . import Scene
from . import GUI
from . import profile
from . import event
from . import layer
from .time import *
from . import colors

import pygame as _pg
import sys as _sys

def init():
    _pg.init()
    _pg.mixer.init()
    _pg.display.set_caption(profile.title)
    profile.clock = _pg.time.Clock()
    profile.default_font = _pg.font.Font(None, profile.default_fontsize)

    flags = _pg.RESIZABLE if profile.resizable else 0
    profile.screen = _pg.display.set_mode((profile.window_width, profile.window_height), flags=flags)

    profile.surface = _pg.Surface((profile.width*profile.surface_scale, profile.height*profile.surface_scale), flags=_pg.SRCALPHA).convert_alpha()


def recreate_surface(width: int, height: int):
    profile.width = width
    profile.height = height
    profile.surface = _pg.Surface([profile.width*profile.surface_scale, profile.height*profile.surface_scale], flags=_pg.SRCALPHA)

def run():
    assert profile.screen is not None
    assert profile.clock is not None

    profile._gdk_executed = True
    for _layer in layer._LayerManager.layer_stack:
        for _component in _layer._GUIComponent_stack:
            _component._regist_events()

    frameCounter = None
    if profile.isCalcPerformance:
        frameCounter = FrameCounter()

    while True:
        if frameCounter:
            frameCounter.accumulateFrameCount()
            if now() - frameCounter._start_time > 1:
                printTime(1/frameCounter.frame_count)
                frameCounter.reset()

        profile.surface.fill(colors.BLACK)

        event._updateKeyEvents()
        event._updateMouseEvents()
        event._updateMousePos()
        event.Input.update()

        event.EventManager.update(_pg.event.get())

        event.EventManager.dispatch()

        # Scene.SceneManager.update() # TODO
        # Scene.SceneManager.draw()

        GUI.base._updateMouseStatus()
        GUI.base.GUIBase._reset_g_flag()

        layer._LayerManager.update()
        layer._LayerManager.draw()
        for pos in GUI.base.GUIBase._debug_position_stack:
            _pg.draw.circle(profile.surface, (0, 255, 0), (pos*profile.surface_scale).pos, 10)

        profile.screen.fill((0, 0, 0))
        if profile.surface_scale != 1:
            _surf = _pg.transform.smoothscale(profile.surface, (profile.width, profile.height))
        else:
            _surf = profile.surface

        profile.screen.blit(_surf, (profile.window_width/2-profile.width/2, profile.window_height/2 - profile.height/2))
        _pg.draw.rect(profile.screen, (255, 255, 255), _pg.Rect(profile.window_width/2-profile.width/2-1, profile.window_height/2-profile.height/2-1, profile.width+2, profile.height+2), 1)

        _pg.display.update()
        profile.clock.tick(profile.fps)

def quit():
    _pg.quit()
    _sys.exit()