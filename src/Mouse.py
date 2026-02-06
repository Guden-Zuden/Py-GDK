from pygame import constants as _cst
from dataclasses import dataclass

@dataclass
class MouseButtonType:
    name: str
    buttonType: int

@dataclass
class MouseButtonData:
    left: bool
    middle: bool
    right: bool
    x1: bool
    x2: bool

right = MouseButtonType("right_button", _cst.BUTTON_RIGHT)
left = MouseButtonType("left_button", _cst.BUTTON_LEFT)
middle = MouseButtonType("middle_button", _cst.BUTTON_MIDDLE)
x1 = MouseButtonType("x1", _cst.BUTTON_X1)
x2 = MouseButtonType("x1", _cst.BUTTON_X2)