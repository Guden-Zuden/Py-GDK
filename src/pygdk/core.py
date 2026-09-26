from .base import *
from . import scene
from . import GUI
from . import profile
from . import event
from . import layer
from .time import *
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
    for _layer in layer.LayerManager.layer_stack:
        for _component in _layer._GUIComponent_stack:
            _component._regist_events()

    while True:
        with BenchMark("core"):

            profile.window.surface.fill(colors.BLACK)

            with BenchMark("event"):
                event._updateKeyEvents()
                event._updateMouseEvents()
                event._updateMousePos()
                event.Input.update()

                event.EventManager.update(_pg.event.get())

                event.EventManager.dispatch()

            scene.SceneManager.update()
            scene.SceneManager.draw()

            with BenchMark("layer"):
                GUI.base._updateMouseStatus()
                GUI.base.GUIBase._reset_g_flag()

                layer.LayerManager.update()
                layer.LayerManager.draw()

            with BenchMark("final draw"):
                for pos in GUI.base.GUIBase._debug_position_stack:
                    _pg.draw.circle(profile.window.surface, (0, 255, 0), pos.pos, 10)

                profile.window.draw()
                # profile.window.screen.fill((0, 0, 0))
                # if profile.surface_scale != 1:
                #     _surf = _pg.transform.smoothscale(profile.surface, (profile.width, profile.height))
                # else:
                #     _surf = profile.surface
                # if profile.width != profile.window_width and profile.height != profile.window_height:
                #     old_width = profile.width
                #     old_height = profile.height
                #     max_width = profile.window_width
                #     max_height = profile.window_height

                #     scaleX = max_width / old_width
                #     scaleY = max_height / old_height
                #     scale = min(scaleX, scaleY)

                #     new_width = old_width * scale
                #     new_height = old_height * scale

                #     _surf = _pg.transform.smoothscale(_surf, (new_width, new_height))

                # profile.screen.blit(_surf, (profile.window_width/2-_surf.get_width()/2, profile.window_height/2 - _surf.get_height()/2))
                # _pg.draw.rect(profile.screen, (255, 255, 255), _pg.Rect(profile.window_width/2-_surf.get_width()/2-1, profile.window_height/2-_surf.get_height()/2-1, _surf.get_width()+2, _surf.get_height()+2), 1)

                # _pg.display.update()

            profile.clock.tick(profile.fps)

def quit():
    _pg.quit()
    _sys.exit()