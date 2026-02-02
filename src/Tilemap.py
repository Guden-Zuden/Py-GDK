from . import Sprite
from . import Profile
from . import Components
from .Log import *

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
    if offset_x < 0:
        start_mx = 0
    else:
        start_mx = int(offset_x) // Profile.sprite_size

    if offset_y < 0:
        start_my = 0
    else:
        start_my = int(offset_y) // Profile.sprite_size

    if offset_x + surf_w > map_w * Profile.sprite_size:
        end_mx = map_w
    else:
        end_mx = int(offset_x + surf_w) // Profile.sprite_size + 1

    if offset_y + surf_h > map_h * Profile.sprite_size:
        end_my = map_h
    else:
        end_my = int(offset_y + surf_h) // Profile.sprite_size + 1

    return start_mx, end_mx, start_my, end_my

class Tilemap(Components.ComponentBase):
    def __init__(self, sprite: Sprite.Sprite = Sprite.Sprite(), start_pos: tuple[int, int] = (0, 0)) -> None:
        super().__init__(0, 0)
        self.map_data: MapData
        self.map_sprite = sprite
        self.start_pos = start_pos
        self.viewport = Viewport(0, 0, 0, 0)

    def load(self, filepath: str | os.PathLike):
        """Load the map data file."""
        with open(filepath, 'r') as f:
            try:
                data = json.load(f)

                bufData: list[MapLayer] = []
                for layer in data["layers"]:
                    bufData.append(MapLayer(layer["name"], layer["data"]))

                self.map_data = MapData(data["width"], data["height"], bufData)

            except KeyError as e:
                raise Exception(f"The format went wrong! Please look at the documents.")
            except Exception as e:
                raise Exception(f"Failed to load map Json file: {e}")
            
    def attach(self, sprite: Sprite.Sprite):
        if self.map_sprite: Log.warn("Tilemap attaching", "Some Sprite has already been attached, so it was overwritten.")
        self.map_sprite = sprite

    def updateViewport(self, offset_x: float, offset_y: float):
        assert Profile.screen is not None
        self.viewport.start_x   ,\
        self.viewport.end_x     ,\
        self.viewport.start_y   ,\
        self.viewport.end_y     = get_viewport(self.map_data.width, self.map_data.height, offset_x, offset_y, Profile.screen.get_width(), Profile.screen.get_height())

    def draw_collision(self, offset_x: float, offset_y: float):
        assert Profile.sprite_size is not None
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
        self.updateViewport(offset_x, offset_y)
        for x in range(self.viewport.get_width()):
            for y in range(self.viewport.get_height()):
                _x = x + self.viewport.start_x
                _y = y + self.viewport.start_y

                rect_x = _x*Profile.sprite_size - self.x - offset_x
                rect_y = _y*Profile.sprite_size - self.y - offset_y

                for layer in self.map_data.mapDatas:
                    if layer.name != "collision":
                        self.map_sprite.draw(layer.data[_y][_x], rect_x, rect_y)