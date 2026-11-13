import pygame as _pg
from typing import Optional as _Optional
from dataclasses import dataclass as _dataclass
import copy as _copy
from functools import (
    wraps as _wraps
)

import logging as _logging
logger = _logging.getLogger(__name__)

from ..base import *
from . import base as _base
from .. import profile as _profile
from .. import colors as _colors
from .. import animator as _animator
from .. import event as _event

class Label(_base.Element):
    def __init__(
            self, 
            u: float, 
            v: float, 
            text: str, 
            textAttributes = _profile.default_textAttributes, 
            padding = _profile.default_padding, 
            wrap_width: int = 0, 
            border: Border = Border(0, _colors.WHITE), 
            animator: _Optional[_animator.GAnimator] = None,
            anchor: Anchor = Anchor.CENTER,
            ) -> None:
        self._text = text
        self._wrap_width = wrap_width
        self._textAttributes = textAttributes

        self.font = _pg.sysfont.SysFont(*self._textAttributes.getFontStyle())
        self.text_surface = self.font.render(
            text, True, *self._textAttributes.getTextColors(), wraplength=wrap_width)
        if self._textAttributes.OutlineColor:
            self.outline_surface = self.font.render(
                text, True, self._textAttributes.OutlineColor, wraplength=wrap_width)
        else:
            self.outline_surface = None
            
        super().__init__(u, v, self.text_surface.width, self.text_surface.height, padding, border, animator, anchor=anchor)
        self._render_text()
        
        self.surface = _pg.Surface(
            (self._textAttributes.OutlineWidth + self.size.width, 
             self._textAttributes.OutlineWidth + self.size.height), flags=_pg.SRCALPHA)

    def _render_text(self):
        self.text_surface = _pg.sysfont.SysFont(*self._textAttributes.getFontStyle()).render(
                self._text, True, *self._textAttributes.getTextColors(), wraplength=self._wrap_width)
        self.size = Vec2(*self.text_surface.size)
        if self._textAttributes.OutlineColor:
            self.outline_surface = _pg.sysfont.SysFont(*self._textAttributes.getFontStyle()).render(
                self._text, True, self._textAttributes.OutlineColor, wraplength=self._wrap_width)
            self.size += self._textAttributes.OutlineWidth*2
        else:
            self.outline_surface = None

        if self.parent is None:
            self.pos = _base._uv2pos((self.u, self.v), self.size.width, self.size.height, self._anchor)

    def update(self):
        if not self.should_update(): return
        super().update()
        if self.should_update():
            if self.parent is None:
                self.pos = _base._uv2pos((self.u, self.v), self.size.width, self.size.height, self._anchor)

    def draw(self):
        if not self.should_draw(): return
        self._render_text()
        super().draw()
        pos = Vec2(self.surface.get_width()/2 - self.text_surface.get_width()/2,
                   self.surface.get_height()/2 - self.text_surface.get_height()/2)

        if self.outline_surface:
            temp = int(self._textAttributes.OutlineWidth*2)
            for dx in range(-temp, temp + 1):
                for dy in range(-temp, temp + 1):
                    self.surface.blit(self.outline_surface, 
                                      (pos + Vec2(dx, dy)).tuple) 

        self.surface.blit(self.text_surface, Vec2(0, 0).tuple)
        self.reset_dirty()

    def set_text(self, text: str):
        self._text = text
        self.set_dirty()
    def set_wrap_width(self, wrap_width: int):
        self._wrap_width = wrap_width
        self.set_dirty()
    def set_textAttributes(self, textAttributes: TextAttributes):
        self._textAttributes = textAttributes
        self.set_dirty()
    def set_anchor(self, anchor: Anchor):
        self._anchor = anchor
        self.set_dirty()

class LinkLabel(Label):
    def __init__(
            self, 
            u: float, 
            v: float, 
            text: str, 
            textAttributes = _profile.default_textAttributes, 
            hovered_textAttributes: _Optional[TextAttributes] = None, 
            padding = _profile.default_padding, 
            wrap_width: int = 0, 
            border: Border = Border(0, _colors.WHITE), 
            animator: _Optional[_animator.GAnimator] = None,
            anchor: Anchor = Anchor.CENTER,
            ) -> None:
        super().__init__(u, v, text, textAttributes, anchor, padding, wrap_width, border, animator, FeedbackOption(True, True), anchor)
        self.hovered_textAttributes = hovered_textAttributes
        self._last_hovered = self._frame.hovering

    def _render_text(self):
        if self._frame.hovering and self.hovered_textAttributes:
            textAttributes = self.hovered_textAttributes
        else:
            textAttributes = self._textAttributes

        self.text_surface = _pg.sysfont.SysFont(*textAttributes.getFontStyle()).render(
                self._text, True, *textAttributes.getTextColors(), wraplength=self._wrap_width)
        if textAttributes.OutlineColor:
            self.outline_surface = _pg.sysfont.SysFont(*textAttributes.getFontStyle()).render(
                self._text, True, textAttributes.OutlineColor, wraplength=self._wrap_width)
        else:
            self.outline_surface = None

        if self.parent is None:
            self.pos = _base._uv2pos((self.u, self.v), self.size.width, self.size.height, self._anchor)

    # @_base.Element.OnEnter()