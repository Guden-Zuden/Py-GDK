from .base import *
from . import scene
from . import GUI
from . import profile
from . import event
from . import layer
from . import time
from . import colors
from . import Window

import pygame as _pg
import sys as _sys

def init():
    _pg.init()
    _pg.mixer.init()
    _pg.display.set_caption(profile.title)
    profile.clock = _pg.time.Clock()
    profile.default_font = _pg.font.Font(None, profile.default_fontsize)

    flags = _pg.RESIZABLE if profile.resizable else 0
    profile.window = Window(profile.title, profile.window_width, profile.window_height, profile.width, profile.height)
    profile.window.window.resizable = profile.resizable
    
def recreate_surface(width: int, height: int):
    assert profile.window
    profile.width = width
    profile.height = height
    profile.window.recreate_surface(width, height)
    print("recreated")

def run():
    assert profile.window is not None
    assert profile.clock is not None

    profile._gdk_executed = True
    for _layer in layer.LayerManager.layer_stack.values():
        for _component in _layer._GUIComponent_stack:
            # _component._regist_events()
            pass

    while True:
        with time.BenchMark("core"):
            time._update_global_dt()

            profile.window.surface.fill(colors.BLACK)

            with time.BenchMark("event"):
                event._updateKeyEvents()
                event._updateMouseEvents()
                event._updateMousePos()
                event.Input.update()

                event.EventManager.update(_pg.event.get())

                event.EventManager.dispatch()

            scene.SceneManager.update()
            scene.SceneManager.draw()

            with time.BenchMark("layer"):
                GUI.base._updateMouseStatus()
                GUI.base.Frame._reset_g_flag()

                layer.LayerManager.update()
                layer.LayerManager.draw()

            with time.BenchMark("final draw"):

                profile.window.draw()

            profile.clock.tick(profile.fps)

def exit():
    _pg.quit()
    _sys.exit()