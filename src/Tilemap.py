from . import Sprite
from . import Profile
from . import Components
from .Log import *
from . import Entity

import pygame as _pygame
import json
import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class MapLayer:
    name: str
    data: list[list[int]]

@dataclass
class MapData:
    width: int
    height: int
    mapDatas: list[MapLayer]
    
@dataclass
class Viewport:
    start_x: int
    end_x: int
    start_y: int
    end_y: int

    def get_width(self):
        return self.end_x - self.start_x
    def get_height(self):
        return self.end_y - self.start_y

def get_viewport(map_w: int, map_h: int, offset_x: float, offset_y: float, surf_w: int, surf_h: int):
    assert Profile.sprite_size is not None
    
    halfsize = Profile.sprite_size/2

    # start of map X
    if (halfsize < offset_x):
        start_mx = 0
    elif (offset_x <= halfsize and offset_x + map_w*Profile.sprite_size > 0):
        start_mx = int(abs(offset_x)) // Profile.sprite_size
    else:
        start_mx = map_w-1
    # right of maptile
    _offset_x = offset_x + (map_w - 1)*Profile.sprite_size
    # end of map X
    if (Profile.width - halfsize > _offset_x):
        end_mx = map_w-1
    elif (_offset_x >= Profile.width - halfsize and offset_x < Profile.width - halfsize):
        end_mx = (map_w-1) - int(abs(Profile.width - _offset_x)) // Profile.sprite_size
    else:
        end_mx = 0

    # start of map Y
    if (halfsize < offset_y):
        start_my = 0
    elif (offset_y <= halfsize and offset_y + map_h*Profile.sprite_size > 0):
        start_my = int(abs(offset_y)) // Profile.sprite_size
    else:
        start_my = map_h-1
    # left of maptile
    _offset_y = offset_y + (map_h-1)*Profile.sprite_size
    # end of map Y
    if (Profile.height - halfsize > _offset_y):
        end_my = map_h-1
    elif (_offset_y >= Profile.height - halfsize and offset_y < Profile.height - halfsize):
        end_my = (map_h-1) - int(abs(Profile.height - _offset_y)) // Profile.sprite_size
    else:
        end_my = 0

    return start_mx, end_mx, start_my, end_my

# ===== Tilemap =====
class Tilemap(Components.SceneComponentBase):
    def __init__(self, sprite: Sprite.Sprite = Sprite.Sprite(), start_pos: tuple[int, int] = (0, 0)) -> None:
        super().__init__(0, 0)
        self.map_data: MapData
        self.map_sprite = sprite
        self.start_pos = start_pos
        self.viewport = Viewport(0, 0, 0, 0)

        self.collision_data: list[list[int]] = []

        self.__loaded = False
        self.__warned = False

    def load(self, filepath: str | os.PathLike):
        """Load the map data file."""
        with open(filepath, 'r') as f:
            try:
                data = json.load(f)

                bufData: list[MapLayer] = []
                for layer in data["layers"]:
                    bufData.append(MapLayer(layer["name"], layer["data"]))

                self.map_data = MapData(data["width"], data["height"], bufData)
                for map_data in self.map_data.mapDatas:
                    if map_data.name == "collision":
                        self.collision_data = map_data.data

                self.__loaded = True

            except KeyError as e:
                raise Exception(f"The format went wrong! Please look at the documents.")
            except Exception as e:
                raise Exception(f"Failed to load map Json file: {e}")
            
    def attach(self, sprite: Sprite.Sprite):
        if self.map_sprite: Log.warn("Tilemap attaching", "Some Sprite has already been attached, so it was overwritten.")
        self.map_sprite = sprite

    def updateViewport(self, offset_x: float, offset_y: float):
        assert Profile.surface is not None
        self.viewport.start_x   ,\
        self.viewport.end_x     ,\
        self.viewport.start_y   ,\
        self.viewport.end_y     = get_viewport(self.map_data.width, self.map_data.height, offset_x, offset_y, Profile.surface.get_width(), Profile.surface.get_height())

    def draw_collision(self, offset_x: float, offset_y: float):
        assert Profile.sprite_size is not None
        if self.__loaded == False:
            return
        self.updateViewport(offset_x, offset_y)

        for x in range(self.viewport.get_width()):
            for y in range(self.viewport.get_height()):
                _x = x + self.viewport.start_x
                _y = y + self.viewport.start_y

                rect_x = _x*Profile.sprite_size - offset_x
                rect_y = _y*Profile.sprite_size - offset_y

                for layer in self.map_data.mapDatas:
                    if layer.name == "collition":
                        self.map_sprite.draw_border(layer.data[_y][_x], rect_x, rect_y)

    def update(self):pass
        # self.collide()

    def draw(self, offset_x, offset_y):
        assert Profile.sprite_size is not None
        if self.__loaded == False:
            if self.__warned == False:
                Log.warn("Tilemap", "There are not map data.")
            self.__warned = True
            return

        self.updateViewport(-offset_x, -offset_y)
        for x in range(self.viewport.get_width()):
            for y in range(self.viewport.get_height()):
                _x = x + self.viewport.start_x
                _y = y + self.viewport.start_y

                rect_x = _x*Profile.sprite_size - self.x - offset_x
                rect_y = _y*Profile.sprite_size - self.y - offset_y

                for layer in self.map_data.mapDatas:
                    if layer.name != "collision":
                        self.map_sprite.draw(layer.data[_y][_x], rect_x, rect_y)