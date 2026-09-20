from .. import sprite as _sprite
from .. import profile as _profile
from ..base import *
from . import entity as _entity

import json
import os
from typing import (
    Optional as _Optional
)
from dataclasses import dataclass as _dataclass
import pathlib

class MapDataManager:
    def __init__(self, width: int, height: int, init_sprite_num: int):
        self.map_datas = {}
        self.sprites = []

        self.map_datas["width"] = width
        self.map_datas["height"] = height
        self.map_datas["layers"] = {
            "ground": [[init_sprite_num for x in range(width)] for j in range(height)]
        }

    def load_sprite(self): # Not yet.
        from tkinter import filedialog
        file_object = filedialog.askopenfile(filetypes=[("JSONファイル", "*.json")])
        if file_object:
            sprite = _sprite.Sprite()
            sprite.load_tile(file_object.name, sprite_size, sprite_padding, )

@_dataclass
class MapLayer:
    name: str
    data: list[list[int]]

@_dataclass
class MapData:
    width: int
    height: int
    map_datas: list[MapLayer]

@_dataclass
class _Viewport:
    start_x: int
    end_x: int
    start_y: int
    end_y: int

    def get_width(self):
        return self.end_x - self.start_x

    def get_height(self):
        return self.end_y - self.start_y

def _get_viewport(
        map_w: int, map_h: int,
        offset_x: float, offset_y: float):
    assert _profile.window is not None

    halfsize = _profile.sprite_size/2

    # begin of map_x
    if halfsize < offset_x:
        start_mx = 0
    elif offset_x <= halfsize and offset_x + map_w * _profile.sprite_size > 0:
        start_mx = int(abs(offset_x)) // _profile.sprite_size
    else:
        start_mx = map_w - 1
    # right of maptile
    _offset_x = offset_x + (map_w - 1) * _profile.sprite_size

    # end of map_x
    if _profile.width - halfsize > _offset_x:
        end_mx = map_w - 1
    elif _offset_x >= _profile.width - halfsize and offset_x < _profile.width - halfsize:
        end_mx = (map_w - 1) - int(abs(_profile.width - _offset_x)) // _profile.sprite_size
    else:
        end_mx = 0

    # begin of map_y
    if halfsize < offset_y:
        start_my = 0
    elif offset_y <= halfsize and offset_y + map_h * _profile.sprite_size > 0:
        start_my = int(abs(offset_y)) // _profile.sprite_size
    else:
        start_my = map_h - 1
    # left of maptile
    _offset_y = offset_y + (map_h - 1) * _profile.sprite_size

    # end of map_y
    _offset_y = offset_y + (map_h - 1) * _profile.sprite_size
    if _profile.height - halfsize > _offset_y:
        end_my = map_h - 1
    elif offset_y <= halfsize and offset_y < _profile.height - halfsize:
        end_my = (map_h - 1) - int(abs(_profile.height - _offset_y)) // _profile.sprite_size
    else:
        end_my = 0

    return (start_mx, end_mx, start_my, end_my)

class Tilemap:
    def __init__(self, sprite: _sprite.Sprite = _sprite.Sprite()) -> None:
        self.x, self.y = 0, 0
        self.map_sprite = sprite
        self.map_data: _Optional[MapData] = None
        self.collision_data: list[list[int]] = []
        self.viewport = _Viewport(0, 0, 0, 0)

        self.__loaded = False
        self.__warned = False

    def load(self, filepath: str | pathlib.Path):
        """Load the map data file."""
        with open(filepath, 'r') as f:
            try:
                data = json.load(f)

                buf_data: list[MapLayer] = []
                for layer in data["layers"]:
                    buf_data.append(MapLayer(layer["name"], layer["data"]))

                self.map_data = MapData(data["width"], data["height"], buf_data)
                for map_data in self.map_data.map_datas:
                    if map_data.name == "collision":
                        self.collision_data = map_data.data

                self.__loaded = True

            except KeyError as e:
                raise Exception(f"This map data is wrong format.")
            except Exception as e:
                raise Exception(f"Failed to load map json file: {e}")

    def update_viewport(self, offset_x: float, offset_y: float):
        assert _profile.window
        assert self.map_data
        self.viewport.start_x,\
        self.viewport.end_x,\
        self.viewport.start_y,\
        self.viewport.end_y = _get_viewport(self.map_data.width, self.map_data.height, offset_x, offset_y)

    def draw_collision(self, offset_x: float, offset_y: float):
        assert _profile.sprite_size
        assert self.map_data

        if self.__loaded == False: return
        self.update_viewport(offset_x, offset_y)

        for x in range(self.viewport.get_width()):
            for y in range(self.viewport.get_height()):
                _x = x + self.viewport.start_x
                _y = y + self.viewport.start_y

                rect_x = _x * _profile.sprite_size - offset_x
                rect_y = _y * _profile.sprite_size - offset_y

                for layer in self.map_data.map_datas:
                    if layer.name == "collision":
                        self.map_sprite.draw_border(layer.data[_y][_x], rect_x, rect_y)

    def update(self): pass

    def draw(self, offset_x: float, offset_y: float):
        assert _profile.sprite_size
        assert self.map_data

        if self.__loaded == False:
            if self.__warned == False:
                print("warning: There are not map data.")
                self.__warned = True
            return

        self.update_viewport(-offset_x, -offset_y)
        for x in range(self.viewport.get_width()):
            for y in range(self.viewport.get_height()):
                _x = x + self.viewport.start_x
                _y = y + self.viewport.start_y

                rect_x = _x * _profile.sprite_size - offset_x
                rect_y = _y * _profile.sprite_size - offset_y

                for layer in self.map_data.map_datas:
                    if layer.name != "collision":
                        self.map_sprite.draw(layer.data[_y][_x], rect_x, rect_y)
