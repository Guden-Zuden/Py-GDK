from . import Core, Profile, Time, Event
from . import Entity
from . import Scene
from . import Sprite
from . import Tilemap
from .Log import *
from .Animator import *
from . import Layer
from . import GUI
from .Utils import Anchor
from . import Key
from . import Sound

import pygame
from typing import Optional, Any
from os import PathLike

def init(title: str = "GameDeveloperKits", fps: int = 60, width: int = 600, height: int = 400, mapSprite_size: int = 32, window_width: Optional[int] = None, window_height: Optional[int] = None):
    print("This Game Developer Kits is using pygame.")
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

def get_availableFonts():
    for font in pygame.font.get_fonts():
        print(font)

def set_user_instance(instance: Any):
    Profile.user_instance = instance

def run():
    Core.run()

# ====== Create Functions ======

def createScene() -> Scene.Scene:
    scene = Scene.Scene()
    Scene.SceneManager.pushScene(scene)
    return scene

def createLayer() -> Layer.Layer:
    layer = Layer.Layer()
    Layer.LayerManager.pushLayer(layer)
    return layer

def createSprite(img_filepath: str | PathLike, sprite_size: int, sprite_padding: int, offset_x: int = 0, offset_y: int = 0, isAntialias: bool = False):
    sprite = Sprite.Sprite()
    sprite.load_tile(img_filepath, sprite_size, sprite_padding, offset_x, offset_y, isAntialias)
    return sprite

def createTilemap(sprite: Sprite.Sprite, start_pos: tuple[int, int] = (0, 0)):
    return Tilemap.Tilemap(sprite, start_pos)

def createEntity(x: float, y: float, sprite: Sprite.Sprite, movement_model: Entity.MovementModelBase, sprite_index: int = 0):
    return Entity.Entity(x, y, sprite, movement_model, sprite_index)

def createBox(u: float,
              v: float,
              width: float,
              height: float,
              color: pygame.Color | tuple[int, int, int, int] | tuple[int, int, int],
              border_width: int = 0,
              border_color: pygame.Color | tuple[int, int, int, int] | tuple[int, int, int] = (0, 0, 0),
              padding: int = 0,
              anchor: Utils.Anchor = Utils.Anchor.center):
    return GUI.Box(u, v, width, height, color, border_width, border_color, padding, anchor)

def createSpriteBox(u: float,
                    v: float,
                    sprite: Sprite.Sprite,
                    width: Optional[float] = None,
                    height: Optional[float] = None,
                    animator: Optional[Animator] = None,
                    padding: int = 0,
                    anchor: Utils.Anchor = Utils.Anchor.center,
                    sprite_index: int = 0):
    return GUI.SpriteBox(u, v, sprite, width, height, animator, padding, anchor, sprite_index)