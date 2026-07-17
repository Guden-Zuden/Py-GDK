import pygame as _pg
# TODO: temporary

type gdk_color = _pg.Color | tuple[int, int, int, int] | tuple[int, int, int]

# definition position type
class Pos:
    def __init__(self, x: int | float, y: int | float) -> None:
        self.x, self.y = x, y
    
    @property
    def pos(self):
        return (self.x, self.y)
    
    def __add__(self, other: Pos) -> Pos:
        return Pos(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: Pos) -> Pos:
        return Pos(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other: Pos) -> Pos:
        return Pos(self.x * other.x, self.y * other.y)
    
    def __truediv__(self, other: Pos) -> Pos:
        return Pos(self.x / other.x, self.y / other.y)
    
    def __str__(self) -> str:
        return f"x: {self.x} y: {self.y}"
    
    def __iter__(self):
        yield self.x
        yield self.y