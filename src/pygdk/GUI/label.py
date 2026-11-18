import pygame as _pg
from typing import Optional as _Optional

from ..base import *
from . import base as _base
from .. import profile as _profile
from .. import colors as _colors
from .. import animator as _animator

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
            feedback_option: _Optional[FeedbackOption] = None,
            anchor: Anchor = Anchor.CENTER,
            ) -> None:
        self._text = text
        self._wrap_width = wrap_width
        self._textAttributes = textAttributes
        self._text_dirty = False

        (
            self.font,
            self.text_surface,
            self.outline_surface,
            self._rendered_text_surface,
            size,
        ) = self._create_text_cache(textAttributes)
        self._rendered_attributes = textAttributes
        self._rendered_attributes_key = self._text_attributes_key(textAttributes)

        super().__init__(
            u, v, size.width, size.height,
            padding, border, animator, feedback_option, anchor=anchor,
        )

    def _create_text_cache(self, textAttributes):
        font = _pg.sysfont.SysFont(*textAttributes.getFontStyle())
        text_surface = font.render(
            self._text,
            True,
            *textAttributes.getTextColors(),
            wraplength=self._wrap_width,
        )
        outline_surface = None
        size = Vec2(*text_surface.size)
        if textAttributes.OutlineColor:
            outline_surface = font.render(
                self._text,
                True,
                textAttributes.OutlineColor,
                wraplength=self._wrap_width,
            )
            size += textAttributes.OutlineWidth * 2

        rendered_surface = _pg.Surface(size.tuple, _pg.SRCALPHA)
        text_pos = (
            (size.width - text_surface.get_width()) / 2,
            (size.height - text_surface.get_height()) / 2,
        )
        if outline_surface:
            extent = int(textAttributes.OutlineWidth * 2)
            for dx in range(-extent, extent + 1):
                for dy in range(-extent, extent + 1):
                    rendered_surface.blit(
                        outline_surface,
                        (text_pos[0] + dx, text_pos[1] + dy),
                    )
        rendered_surface.blit(text_surface, text_pos)
        return font, text_surface, outline_surface, rendered_surface, size

    @staticmethod
    def _text_attributes_key(textAttributes):
        def color_key(color):
            return None if color is None else tuple(color)

        return (
            textAttributes.Font,
            textAttributes.FontSize,
            color_key(textAttributes.TextColor),
            color_key(textAttributes.BackGroundColor),
            textAttributes.OutlineWidth,
            color_key(textAttributes.OutlineColor),
            textAttributes.Bold,
            textAttributes.Italic,
        )

    def _get_text_attributes(self):
        return self._textAttributes

    def _render_text(self, textAttributes=None):
        if textAttributes is None:
            textAttributes = self._get_text_attributes()

        (
            self.font,
            self.text_surface,
            self.outline_surface,
            self._rendered_text_surface,
            size,
        ) = self._create_text_cache(textAttributes)
        if self.size.tuple != size.tuple:
            self.size = size
            if self.parent is None:
                pos = _base._uv2pos(
                    (self.u, self.v), self.size.width, self.size.height, self.anchor
                )
                if self.pos.tuple != pos.tuple:
                    self.pos = pos
        self._rendered_attributes = textAttributes
        self._rendered_attributes_key = self._text_attributes_key(textAttributes)
        self._text_dirty = False

    def _get_baseline_offset(self) -> float:
        return (
            (self.surface.get_height() - self.text_surface.get_height()) / 2
            + self.font.get_ascent()
        )

    def update(self):
        if not self.should_update(): return
        super().update()
        if self.parent is None:
            pos = _base._uv2pos(
                (self.u, self.v), self.size.width, self.size.height, self.anchor
            )
            if self.pos.tuple != pos.tuple:
                self.pos = pos

    def draw(self):
        textAttributes = self._get_text_attributes()
        textAttributes_key = self._text_attributes_key(textAttributes)
        text_dirty = (
            self._text_dirty
            or textAttributes is not self._rendered_attributes
            or textAttributes_key != self._rendered_attributes_key
        )
        if text_dirty and not self._dirty:
            self.set_dirty()
        if not self.should_draw(): return
        if text_dirty:
            self._render_text(textAttributes)
        super().draw()
        self.surface.blit(self._rendered_text_surface, (0, 0))
        self.reset_dirty()

    def set_text(self, text: str):
        if self._text == text: return
        self._text = text
        self._text_dirty = True
        self.set_dirty()
    def set_wrap_width(self, wrap_width: int):
        if self._wrap_width == wrap_width: return
        self._wrap_width = wrap_width
        self._text_dirty = True
        self.set_dirty()
    def set_textAttributes(self, textAttributes: TextAttributes):
        self._textAttributes = textAttributes
        self._text_dirty = True
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
        self.hovered_textAttributes = hovered_textAttributes
        super().__init__(u, v, text, textAttributes, padding, wrap_width, border, animator, FeedbackOption(True, True), anchor)

    def _get_text_attributes(self):
        if self._frame.hovering and self.hovered_textAttributes:
            return self.hovered_textAttributes
        return self._textAttributes

    def update(self):
        super().update()
        textAttributes = self._get_text_attributes()
        if (
            textAttributes is not self._rendered_attributes
            or self._text_attributes_key(textAttributes)
            != self._rendered_attributes_key
        ):
            self.set_dirty()