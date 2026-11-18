from typing import (
    Callable as _Callable,
    Any as _Any,
    Optional as _Optional
)

from ..base import *
from .. import profile as _profile
from . import base as _base
from .label import Label as _Text
from .box import Box as _Box
from .image import Image as _Image
from .. import animator as _animator

import pathlib as _pathlib
import pygame as _pg
from functools import wraps as _wraps

class Button(_base.Element):
    def __init__(self, u: float, v: float, width: float, height: float,
                 text: str, textAttributes: TextAttributes = _profile.default_textAttributes, color: gdk_color = (0,0,0), border = _profile.default_border,
                 padding = _profile.default_padding, callback_clicked: _Optional[_Callable] = None, animator: _Optional[_animator.GAnimator] = None) -> None:
        super().__init__(u, v, width, height, padding, border, animator, FeedbackOption(True, True))
        self._hover_feedback_color = Color(0, 0, 0, 51)
        self._click_feedback_color = Color(0, 0, 0, 102)
        self._hover_feedback_surface.fill(self._hover_feedback_color)
        self._click_feedback_surface.fill(self._click_feedback_color)

        self._text = text
        self._textAttributes = textAttributes
        self._color = color
        self._border = border
        self._padding = padding

        self.callback_clicked = callback_clicked

        self.box_obj = _Box(u, v, *self.size.tuple, color, padding, border)
        self.set_child(self.box_obj)
        self.box_obj.uv = Vec2(0, 0)

        self.text_obj = _Text(u, v, text, textAttributes, padding=padding)
        self.set_child(self.text_obj)
        self.text_obj.uv = Vec2(0, 0)

    def update(self):
        if not self.should_update(): return
        super().update()

        if self._dirty:
            self.text_obj.set_text(self._text)
            self.text_obj.set_textAttributes(self._textAttributes)
            self.text_obj.set_padding(self._padding)
            self.text_obj.uv = Vec2(0, 0)
            self.text_obj.update()

            self.box_obj.set_border(self._border)
            self.box_obj.set_padding(self._padding)
            self.box_obj.set_color(self._color)
            self.box_obj.size = self.size
            self.box_obj.update()

    def _get_baseline_offset(self) -> float:
        return (
            (self.size.height - self.text_obj.size.height) / 2
            + self.text_obj._get_baseline_offset()
        )

    def draw(self):
        if not self.should_draw(): return
        super().draw()
        self.text_obj.draw()
        self.box_obj.draw()
        self.reset_dirty()

class ImageButton(Button):
    from .. import profile
    def __init__(self, u: float, v: float, width: float,
                 text: str, textAttributes: TextAttributes = profile.default_textAttributes, image: _Optional[_Image] = None, border = profile.default_border,
                 padding = profile.default_padding, callback_clicked: _Optional[_Callable] = None, animator: _Optional[_animator.GAnimator] = None, no_register = False) -> None:
        if image is None: raise Exception("image is None.")
        self.image_obj = image
        super().__init__(u, v, width, self.image_obj.size.height, text, textAttributes, (0,0,0,0), border, padding, callback_clicked, animator)
        super().set_child(self.image_obj)
        self.image_obj.uv = Vec2(0, 0)

    def update(self):
        super().update()
        if self.should_update() == False: return
        self.image_obj.update()

    def draw(self):
        if self.should_draw() == False: return
        super().draw()
        self.image_obj.resize()
        self.image_obj.draw()
        self.reset_dirty()