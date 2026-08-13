from typing import Any, Callable

from ..base import *
from . import base
from .text import *
from .box import *

import pathlib
import pygame as _pg

class Button(base.GUIBase):
    def __init__(self, u: float, v: float, width: float, height: float,
                 text: str, textAttributes: TextAttributes = profile.default_textAttributes, color: gdk_color = (0,0,0), border = profile.default_border,
                 padding = profile.default_padding, event_func: Optional[Callable] = None, no_register = False) -> None:
        super().__init__(u, v, width, height, padding, border, no_register)

        self.text = text
        self.textAttributes = textAttributes
        self.color = color
        self.border = border
        self.padding = padding
        self.event_func = event_func

        self.text_obj = Text(u, v, text, textAttributes, padding, no_register=True)
        self.box_obj = Box(u, v, self.width, self.height, color, padding, border, child=self.text_obj, no_register=True)
        self.hovering_box_obj = Box(u, v, self.width, self.height, colors.BLACK, padding, border, no_register=True)
        self.hovering_box_obj.color.a = int(self.hovering_box_obj.color.a * 0.2)

        self.clicking_box_obj = Box(u, v, self.width, self.height, colors.BLACK, padding, border, no_register=True)
        self.clicking_box_obj.color.a = int(self.clicking_box_obj.color.a * 0.4)

        self.event_func = event_func

    def update(self):
        super().update()
        self.text_obj.text = self.text
        self.text_obj.textAttributes = self.textAttributes
        self.text_obj.padding = self.padding

        self.box_obj.border = self.border
        self.box_obj.padding = self.padding
        
        self.hovering_box_obj.border = self.border
        self.hovering_box_obj.padding = self.padding
        
        self.clicking_box_obj.border = self.border
        self.clicking_box_obj.padding = self.padding

    def draw(self, surface: Optional[_pg.Surface] = None):
        super().draw(surface)
        self.box_obj.draw()
        if self.clicked:
            self.clicking_box_obj.draw(surface)
        elif self.hovered:
            self.hovering_box_obj.draw(surface)

        if surface: self._flush(surface)
        else: self._flush()

class ImageButton(Button):
    def __init__(self, u: float, v: float, width: float,
                 text: str, textAttributes: TextAttributes = profile.default_textAttributes, img_filepath: str | pathlib.Path = profile._directory._str+"/assets/img/NoImage.png", border = profile.default_border,
                 padding = profile.default_padding, event_func: Optional[Callable] = None, no_register = False) -> None:
        from . import Image
        self.image_obj = Image(u, v, img_filepath, width, padding, border, None, True)
        super().__init__(u, v, width, self.image_obj.height, text, textAttributes, (0,0,0,0), border, padding, event_func, no_register)

    def update(self):
        super().update()
        self.image_obj.border = self.border
        self.image_obj.padding = self.padding

        self.image_obj.update()

    def draw(self, surface: Optional[_pg.Surface] = None):
        self.image_obj.draw(surface)
        super().draw(surface)