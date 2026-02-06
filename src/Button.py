from . import Text
from . import Components
from . import Box
from . import Constants
from . import Profile
from . import Event
from . import Collision
from .Log import *

import pygame as _pygame
from typing import Callable

class Button(Components.LayerComponentBase):
    __NEUTRAL_COLOR: int =  0
    __HOVERED_COLOR: int = 16
    __CLICKED_COLOR: int = 32
    _mouseX: float = 0
    _mouseY: float = 0

    _clickevent: bool = False

    def __init__(
            self,
            name: str,
            u: float,
            v: float,
            children: tuple[Components.LayerComponentBase],
            width: float,
            height: float,
            background_color: _pygame.Color | tuple[int, int, int, int] | tuple[int, int, int],
            clickFunc: Callable,
            flags: int = 0,
            border_width: int = 0,
            border_color: _pygame.Color | tuple[int, int, int, int] | tuple[int, int, int] = (0, 0, 0)) -> None:
        super().__init__(u, v)
        self.name = name
        self.children = children
        self.width = width
        self.height = height
        self.background_color = background_color
        self.clickFunc = clickFunc
        self.border_width = border_width
        self.border_color = border_color

        self.box_obj = Box.Box(u, v, width, height, background_color, border_width, border_color)
        self.children_obj = children

        self.isHovered = False
        self.isPressed = False

        self.flags = flags

        self.overlay = _pygame.Surface([self.width, self.height], _pygame.SRCALPHA)



    def update(self):
        Button._Hovering_Flag = False

        self.isHovered = self.box_obj.rect.collidepoint(Button._mouseX, Button._mouseY)

        if Event.pressedMousebuttons.left and self.isHovered:
            self.isPressed = True

        if Button._clickevent and self.isPressed:
            
            self.isHovered = self.box_obj.rect.collidepoint(Button._mouseX, Button._mouseY)

            if self.isHovered:
                self.clickFunc()
            self.isPressed = False
            Button._clickevent = False            

    def draw(self):
        assert Profile.surface is not None

        color = (0, 0, 0, 0)

        if self.isPressed:
            plus = self.__CLICKED_COLOR
        elif self.isHovered:
            plus = self.__HOVERED_COLOR
        else:
            plus = self.__NEUTRAL_COLOR

        is_darken = False

        if (self.background_color[0] + self.background_color[1] + self.background_color[2])/3 >= 128:
            is_darken = True

        if is_darken:
            color = (0, 0, 0, plus)
        else:
            color = (255, 255, 255, plus)

        self.box_obj.draw()

        self.overlay.fill((0, 0, 0, 0))

        if (    
                self.isHovered
                and not self.flags & Constants.DIS_HOVERFEED
                and not self.isPressed
            ) or (
                self.isPressed
                and not self.flags & Constants.DIS_CLICKFEED
            ):
                    self.overlay.fill(color)

        _pygame.Surface.blit(Profile.surface, self.overlay, self.box_obj.rect)

        for child in self.children:
            child._draw(self.x, self.y)

@Event.OnMousemove()
def updateMousePos(e):
    Button._mouseX, Button._mouseY = e.pos[0], e.pos[1]

@Event.OnMousebuttonUp(Event.Mouse.left)
def updateMousebuttonUp(e):
    Button._clickevent = True