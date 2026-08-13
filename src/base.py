from __future__ import annotations

from dataclasses import dataclass, field
from enum import Flag, auto
from typing import Optional, Any, Callable, Self, overload
from inspect import isfunction, signature
from functools import cache

import pygame as _pg

from . import colors

# TODO: temporary

type gdk_color = _pg.Color | tuple[int, int, int, int] | tuple[int, int, int]

class NullSurface(_pg.Surface): ...

# definition position type
class Vec2:
    def __init__(self, x: int | float, y: int | float) -> None:
        self.x, self.y = x, y
    
    @property
    def pos(self):
        return (self.x, self.y)
    
    def __add__(self, other: Vec2) -> Vec2:
        if type(other) == float or type(other) == int:
            return Vec2(self.x + other, self.y + other)
        elif type(other) == Vec2:
            return Vec2(self.x + other.x, self.y + other.y)
        else:
            raise TypeError("Only Vec2, float, or integer arguments are supported.")
    
    def __sub__(self, other: Vec2) -> Vec2:
        if type(other) == float or type(other) == int:
            return Vec2(self.x - other, self.y - other)
        elif type(other) == Vec2:
            return Vec2(self.x - other.x, self.y - other.y)
        else:
            raise TypeError("Only Vec2, float, or integer arguments are supported.")
    
    def __mul__(self, other: Vec2 | float | int) -> Vec2:
        if type(other) == float or type(other) == int:
            return Vec2(self.x * other, self.y * other)
        elif type(other) == Vec2:
            return Vec2(self.x * other.x, self.y * other.y)
        else:
            raise TypeError("Only Vec2, float, or integer arguments are supported.")
    
    def __truediv__(self, other: Vec2 | float | int) -> Vec2:
        if type(other) == float or type(other) == int:
            return Vec2(self.x / other, self.y / other)
        elif type(other) == Vec2:
            return Vec2(self.x / other.x, self.y / other.y)
        else:
            raise TypeError("Only Vec2, float, or integer arguments are supported.")
    
    def __str__(self) -> str:
        return f"x: {self.x} y: {self.y}"
    
    def __iter__(self):
        yield self.x
        yield self.y
    
    def normalized(self):
        distance = (self.x ** 2 + self.y ** 2) ** 1/2
        self /= distance

    def distance(self) -> float:
        v = (self.x ** 2 + self.y ** 2) ** 1/2
        return v

class Padding:
    @overload
    def __init__(self, /) -> None: ...
    @overload
    def __init__(self, padding: float, /) -> None: ...

    @overload
    def __init__(self, vertical: float, horizontal: float, /) -> None: ...

    @overload
    def __init__(self, left: float, top: float, right: float, bottom: float, /) -> None: ...

    def __init__(self, *args):
        if len(args) == 0:
            self.top = self.bottom = self.left = self.right = 0
        elif len(args) == 1:
            self.top = self.bottom = self.left = self.right = args[0]
        elif len(args) == 2:
            self.left = self.right = args[0]
            self.top = self.bottom = args[1]
        elif len(args) == 4:
            self.left = args[0]
            self.top = args[1]
            self.right = args[2]
            self.bottom = args[3]
        else:
            raise TypeError("Padding() takes 0, 1, 2, or 4 arguments.")

class Color(_pg.Color): ...

class Border:
    def __init__(self, width: float, color: gdk_color) -> None:
        self.width = width
        self.color = color if type(color) is Color else Color(*color)

@dataclass
class TextAttributes:
    Font: str
    FontSize: float
    TextColor: gdk_color
    BackGroundColor: Optional[gdk_color] = None

    OutlineWidth: float = 0
    """This is float, but """
    OutlineColor: Optional[gdk_color] = None

    Bold: bool = False
    Italic: bool = False

    def getFontStyle(self):
        from . import profile
        return (
            # self.Font, self.FontSize, self.Bold, self.Italic
            self.Font, self.FontSize*profile.surface_scale, self.Bold, self.Italic
        )
    def getTextColors(self):
        return (
            self.TextColor, self.BackGroundColor
        )

@dataclass
class ScrollBarStyle:
    width: int = 10
    color: gdk_color = colors.WHITE
    rounded: bool = False