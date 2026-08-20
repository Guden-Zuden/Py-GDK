from typing import (
    Callable as _Callable,
    Any as _Any,
    Optional as _Optional
)

from ..base import *
from .. import profile as _profile
from . import base as _base
from .text import Text as _Text
from .box import Box as _Box
from .. import colors as _colors
from .image import Image as _Image

import pathlib as _pathlib
import pygame as _pg

class Button(_base.GUIBase):
    def __init__(self, u: float, v: float, width: float, height: float,
                 text: str, textAttributes: TextAttributes = _profile.default_textAttributes, color: gdk_color = (0,0,0), border = _profile.default_border,
                 padding = _profile.default_padding, event_func: _Optional[_Callable] = None, no_register = False) -> None:
        super().__init__(u, v, width, height, padding, border, no_register)

        self.text = text
        self.textAttributes = textAttributes
        self.color = color
        self.border = border
        self.padding = padding
        self.event_func = event_func

        self.text_obj = _Text(u, v, text, textAttributes, padding, no_register=True)
        self.box_obj = _Box(u, v, self.width, self.height, color, padding, border, child=self.text_obj, no_register=True)
        self.hovering_box_obj = _Box(u, v, self.width, self.height, _colors.BLACK, padding, border, no_register=True)
        self.hovering_box_obj.color.a = int(self.hovering_box_obj.color.a * 0.2)

        self.clicking_box_obj = _Box(u, v, self.width, self.height, _colors.BLACK, padding, border, no_register=True)
        self.clicking_box_obj.color.a = int(self.clicking_box_obj.color.a * 0.4)

        self.event_func = event_func

    def update(self):
        super().update()
        self.text_obj.pos = self.pos
        self.text_obj.text = self.text
        self.text_obj.textAttributes = self.textAttributes
        self.text_obj.padding = self.padding

        self.box_obj.pos = self.pos
        self.box_obj.border = self.border
        self.box_obj.padding = self.padding

        self.hovering_box_obj.pos = self.pos
        self.hovering_box_obj.border = self.border
        self.hovering_box_obj.padding = self.padding
        
        self.clicking_box_obj.pos = self.pos
        self.clicking_box_obj.border = self.border
        self.clicking_box_obj.padding = self.padding

    def draw(self, surface: _Optional[_pg.Surface] = None):
        super().draw(surface)
        self.box_obj.draw(surface)
        if self.clicked:
            self.clicking_box_obj.draw(surface)
        elif self.hovered:
            self.hovering_box_obj.draw(surface)

        if surface: self._flush(surface)
        else: self._flush()

class ImageButton(Button):
    from .. import profile
    def __init__(self, u: float, v: float, width: float,
                 text: str, textAttributes: TextAttributes = profile.default_textAttributes, image: _Optional[_Image] = None, border = profile.default_border,
                 padding = profile.default_padding, event_func: _Optional[_Callable] = None, no_register = False) -> None:
        if image is None: raise Exception("image is None.")
        self.image_obj = image
        super().__init__(u, v, width, self.image_obj.height, text, textAttributes, (0,0,0,0), border, padding, event_func, no_register)

    def update(self):
        super().update()
        self.image_obj.pos = self.pos
        self.image_obj.border = self.border
        self.image_obj.padding = self.padding

        self.image_obj.update()

    def draw(self, surface: _Optional[_pg.Surface] = None):
        self.image_obj.draw(surface)
        super().draw(surface)