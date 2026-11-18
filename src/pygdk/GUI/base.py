"""Normally, we import this file with wild card."""
from __future__ import annotations
from typing import TYPE_CHECKING as _TYPE_CHECKING

import pygame as _pg
from typing import (
    Self as _Self,
    Optional as _Optional,
    Callable as _Callable,
    overload as _overload,
    Annotated as _Annotated
    )
from functools import (
    wraps as _wraps
)
from enum import (
    Flag as _Flag,
    auto as _auto
)
import copy as _copy

import logging as _logging
logger = _logging.getLogger(__name__)

from pygdk.animator import GAnimator

from ..base import *
from .. import profile
from .. import event, mouse
from .. import colors
from ..time import BenchMark as _BenchMark
if _TYPE_CHECKING:
    from ..animator import GAnimator

def _pos2uv(pos: Vec2, width: float, height: float) -> Vec2:
    u = (2 * pos.x - profile.width + width) / profile.width
    v = (2 * pos.y - profile.height + height) / profile.height
    return Vec2(u, v)

def _pos2uv_elm(pos: Vec2, width: float, height: float, parent_width: float, parent_height: float) -> Vec2:
    u = (2 * pos.x - parent_width + width) / parent_width
    v = (2 * pos.y - parent_height + height) / parent_height
    return Vec2(u, v)

@_overload
def _uv2pos(uv: tuple[float, float], width: float, height: float) -> Vec2: ...

@_overload
def _uv2pos(uv: tuple[float, float], width: float, height: float, anchor: Anchor) -> Vec2: ...

def _uv2pos(uv: tuple[float, float], width: float, height: float, anchor: _Optional[Anchor] = None) -> Vec2:
    pos = Vec2(
        profile.width/2 + profile.width/2 * uv[0] - width/2,
        profile.height/2 + profile.height/2 * uv[1] - height/2
    )
    if anchor is None:
        pass # do nothing
    else:
        if anchor & Anchor.LEFT:
            pos.x += width/2
        if anchor & Anchor.RIGHT:
            pos.x -= width/2
        if anchor & Anchor.TOP:
            pos.y += height/2
        if anchor & Anchor.BOTTOM:
            pos.y -= height/2

    return pos

def _uv2pos_elm(
        uv: tuple[float, float], 
        width: float, height: float, 
        parent_width: float, parent_height: float, 
        anchor: _Optional[Anchor] = None
        ) -> Vec2:
    pos = Vec2(
        parent_width/2 + parent_width/2 * uv[0] - width/2,
        parent_height/2 + parent_height/2 * uv[1] - height/2)
    if anchor is None:
        pass # do nothing
    else:
        if anchor & Anchor.LEFT:
            pos.x += width/2
        if anchor & Anchor.RIGHT:
            pos.x -= width/2
        if anchor & Anchor.TOP:
            pos.y += height/2
        if anchor & Anchor.BOTTOM:
            pos.y -= height/2

    return pos

def _updateMouseStatus():
    from . import Button, ImageButton, LinkLabel
    if Frame.g_hovering and isinstance(Frame.g_hovering.element, (Button, ImageButton, LinkLabel)):
        _pg.mouse.set_cursor(_pg.SYSTEM_CURSOR_HAND)
    else:
        _pg.mouse.set_cursor(_pg.SYSTEM_CURSOR_ARROW)

class Element:
    """
    Element manages updating and drawing.

    - Description
        Position coordinates are relative to the parent element for child elements,
        and to the window for root elements. The `u` and `v` values are window-relative;
        use `pos` to set a child element's local position.

    - attributes
        uv: Vec2(u, v)
        pos: Vec2(x, y)
        size: Vec2(width, height)
    """
    def __init__(
            self, 
            u: float, 
            v: float, 
            width: float, 
            height: float,
            padding: Padding, 
            border: _Optional[Border] = None, 
            animator: _Optional["GAnimator"] = None,
            feedback_option: _Optional[FeedbackOption] = None,
            anchor: Anchor = Anchor.CENTER) -> None:
        self._frame = Frame(self)
        
        self._uv = Vec2(u, v)
        self._pos = _uv2pos((u, v), width, height)
        self._size = Vec2(width, height)
        self._anchor = anchor

        self.animator = animator
        if feedback_option:
            self.feedback_option = feedback_option
        else:
            self.feedback_option = FeedbackOption()

        self._padding = padding
        self._border = border

        self.parent: _Optional[object] = None
        self.children: list[Element] = []
        self._stick_target: _Optional[Element] = None
        self._stick_direction: _Optional[Direction] = None
        self._stick_target_layout_signature: _Optional[tuple[object, ...]] = None
        self._stick_parent_layout_signature: _Optional[tuple[object, ...]] = None

        # TODO: hovered, --clicked-- pressed and focused states should be implemented?
        
        # properties
        self.visible = True

        # event callbacks
        self.callback_enter: _Optional[_Callable] = None
        self.callback_leave: _Optional[_Callable] = None
        self.callback_mousewheelscrolled: _Optional[_Callable] = None
        self.callback_hovered: _Optional[_Callable] = None
        self.callback_pressed: _Optional[_Callable] = None
        self.callback_clicked: _Optional[_Callable] = None

        # dirty flags
        self._dirty = True

        # feedbacks
        self._feedback_color = Color(0, 0, 0, 60)
        self._hover_feedback_color = self._feedback_color
        self._click_feedback_color = self._feedback_color

        self.create_surface()

    def stick(self, target: Element, direction: Direction) -> _Self:
        """
        Keep this element positioned relative to target.
        """
        if target is self or self in target.get_parents():
            raise ValueError("An element cannot stick to itself or one of its children.")

        current: _Optional[Element] = target
        visited: set[Element] = set()
        while current is not None and current not in visited:
            if current is self:
                raise ValueError("Sticking elements cannot form a cycle.")
            visited.add(current)
            current = current._stick_target

        self._stick_target = target
        self._stick_direction = direction
        self._stick_target_layout_signature = target._layout_signature()
        self._stick_parent_layout_signature = (
            self.parent._layout_signature()
            if isinstance(self.parent, Element)
            else None
        )
        self._apply_stick()

        return self

    def _layout_signature(self) -> tuple[object, ...]:
        signature: list[object] = [(profile.width, profile.height)]
        parent = self.parent
        while isinstance(parent, Element):
            signature.append((id(parent), parent.size.tuple))
            parent = parent.parent
        return tuple(signature)

    def _abs_pos_from_uv(self) -> Vec2:
        if isinstance(self.parent, Element):
            pos = _uv2pos_elm(
                self.uv.tuple,
                self.size.width,
                self.size.height,
                self.parent.size.width,
                self.parent.size.height,
            )
            return self.parent._abs_pos_from_uv() + pos
        return _uv2pos(
            self.uv.tuple,
            self.size.width,
            self.size.height,
            self.anchor,
        )

    def _apply_stick(self) -> None:
        target = self._stick_target
        direction = self._stick_direction
        if target is None or direction is None:
            return

        target_signature = target._layout_signature()
        target_pos = (
            target._abs_pos_from_uv()
            if target_signature != self._stick_target_layout_signature
            else target.abs_pos
        )
        self._stick_target_layout_signature = target_signature

        pos = Vec2(
            target_pos.x + target.size.width / 2 - self.size.width / 2,
            target_pos.y + target.size.height / 2 - self.size.height / 2,
        )

        if direction & Direction.TOP:
            pos.y = target_pos.y - self.size.height
        elif direction & Direction.BOTTOM:
            pos.y = target_pos.y + target.size.height

        if direction & Direction.LEFT:
            pos.x = target_pos.x - self.size.width
        elif direction & Direction.RIGHT:
            pos.x = target_pos.x + target.size.width

        parent = self.parent
        if isinstance(parent, Element):
            parent_signature = parent._layout_signature()
            parent_pos = (
                parent._abs_pos_from_uv()
                if parent_signature != self._stick_parent_layout_signature
                else parent.abs_pos
            )
            pos -= parent_pos
            self._stick_parent_layout_signature = parent_signature
        else:
            self._stick_parent_layout_signature = None

        if self.pos.tuple != pos.tuple:
            self.pos = pos

    def should_update(self) -> bool:
        """if visible is true"""
        return (self.visible)

    def update(self) -> None:
        if self.visible == False: return

        self._frame.update()
        self.on_update()

        if self.animator:
            self.animator.update()

        self._apply_stick()

    def should_draw(self) -> bool:
        """if visible and dirty flag is true"""
        return ((self.visible and self._dirty)
                 or self.size.get_dirty())

    def draw(self) -> None:
        """
        #### Description
            Draw on self.surface
        """
        if self.visible == False: return
        if self.should_draw() == False: return

        self.create_surface()
        self.surface.fill((0,0,0,0))
        self.on_draw()

        if self._border and self._border.width > 0:
            width = int(self._border.width)
            if width > 0:
                if self._border.type == BorderType.INSIDE:
                    _pg.draw.rect(self.border_surface,
                                  self._border.color,
                                  (self._border.width, self._border.width, self.size.width, self.size.height),
                                  width)
                elif self._border.type == BorderType.CENTER:
                    _pg.draw.rect(self.border_surface,
                                  self._border.color,
                                  (self._border.width/2, self._border.width/2, self.size.width + self._border.width, self.size.height + self._border.width),
                                  width)
                elif self._border.type == BorderType.OUTSIDE:
                    _pg.draw.rect(self.border_surface,
                                  self._border.color,
                                  (0, 0, self.size.width + self._border.width*2, self.size.height + self._border.width * 2),
                                  width)
        logger.debug(f"Drawn: %s", self)

    def should_flush(self):
        return (self.visible)

    def _get_baseline_offset(self) -> _Optional[float]:
        return None

    def _flush_into(self, surface: _pg.Surface, parent_pos: Vec2):
        if not self.should_flush():
            return

        pos = parent_pos + self._pos
        surface.blit(self.surface, pos.tuple)

        for child in self.children:
            child._flush_into(surface, pos)

        if self.feedback_option.hover and self._frame.hovering:
            surface.blit(self._hover_feedback_surface, pos.tuple)
        if self.feedback_option.click and self._frame.clicking:
            surface.blit(self._click_feedback_surface, pos.tuple)

    def flush(self, surface: _Optional[_pg.Surface] = None):
        """
        #### Description
            If self is child element, draw on parent's surface.
            `surface` is only for this class, Element.
            Call with no arguments.
        """
        assert profile.window
        if not self.should_flush(): return

        if surface is not None:
            self._flush_into(surface, Vec2(0, 0))
            return

        abs_pos = self.abs_pos
        if self.anchor & Anchor.LEFT:
            abs_pos.x += self.size.width/2
        if self.anchor & Anchor.RIGHT:
            abs_pos.x -= self.size.width/2
        if self.anchor & Anchor.TOP:
            abs_pos.y += self.size.height/2
        if self.anchor & Anchor.BOTTOM:
            abs_pos.y -= self.size.height/2
        
        if surface is None:
            # final draw
            self.output_surface.fill((0, 0, 0, 0))

            self.output_surface.blit(self.surface)

            for child in self.children:
                child.flush(self.output_surface)
                child.surface

            if self.feedback_option.hover and self._frame.hovering:
                self.output_surface.blit(self._hover_feedback_surface)
            if self.feedback_option.click and self._frame.clicking:
                self.output_surface.blit(self._click_feedback_surface)

            # show on the screen
            profile.window.surface.blit(self.output_surface, abs_pos.tuple)

            if self._border:
                profile.window.surface.blit(
                    self.border_surface, (abs_pos - self._border.width).tuple)

    def create_surface(self):
        """
        #### Description
            Called when resized and instantiated.
            Children's surfaces are also created when their parent is called.
            The size of border surface is always size + width * 2.
            The border drawing position depends on the border type.
        """
        if self._border:
            self.border_surface = _pg.Surface((self.size + self._border.width*2).tuple, _pg.SRCALPHA)
        
        if self._border and self._border.type == BorderType.INSIDE:
            self.surface = _pg.Surface(self.size.tuple, _pg.SRCALPHA)
        else: # no border, center and outside border
            self.surface = _pg.Surface(self.size.tuple, _pg.SRCALPHA)

        self.output_surface = self.surface.copy()
        """Final result will be draw on this surface."""

        # Keep hover and click feedback independent so either can be tuned separately.
        self._hover_feedback_surface = _pg.Surface(self.size.tuple, _pg.SRCALPHA)
        self._hover_feedback_surface.fill(self._hover_feedback_color)
        self._click_feedback_surface = _pg.Surface(self.size.tuple, _pg.SRCALPHA)
        self._click_feedback_surface.fill(self._click_feedback_color)

        logger.debug(f"Surface was created: %s", self)

    def collide_pos(self, pos: Vec2):
        return self.surface.get_rect().move(self.abs_pos.tuple)\
                .collidepoint(pos.tuple)

    def set_dirty(self):
        """(core)Call after changing some attributes."""
        self._dirty = True

    def reset_dirty(self):
        """(core)Call the end of drawing."""
        self._dirty = False
        self.pos.reset_dirty()
        self.size.reset_dirty()

    def on_update(self):
        """Called before update."""
        pass

    def on_draw(self):
        """Called before draw."""
        pass

    # event callback decorators
    def OnEnter(self):
        def decorator(func: _Callable):
            @_wraps(func)
            def wrapper(*args, **kwargs):
                logger.debug("OnEnter executed: %s", self)
                return func(*args, **kwargs)

            self.callback_enter = wrapper
            return wrapper

        return decorator

    def OnLeave(self):
        def decorator(func: _Callable):
            @_wraps(func)
            def wrapper(*args, **kwargs):
                logger.debug("OnLeave executed: %s", self)
                return func(*args, **kwargs)

            self.callback_leave = wrapper
            return wrapper

        return decorator

    def OnMousewheelScroll(self):
        def decorator(func: _Callable):
            @_wraps(func)
            def wrapper(*args, **kwargs):
                logger.debug("OnMousewheelScroll executed: %s", self)
                return func(*args, **kwargs)

            self.callback_mousewheelscrolled = wrapper
            return wrapper

        return decorator


    def OnHovered(self):
        def decorator(func: _Callable):
            @_wraps(func)
            def wrapper(*args, **kwargs):
                logger.debug("OnHovered executed: %s", self)
                return func(*args, **kwargs)

            self.callback_hovered = wrapper
            return wrapper

        return decorator

    def OnPressed(self):
        def decorator(func):
            @_wraps(func)
            def wrapper(*args, **kwargs):
                logger.debug("OnPressed executed: %s", self)

                return func(*args, **kwargs)

            self.callback_pressed = wrapper
            return wrapper

        return decorator

    def OnClicked(self):
        def decorator(func):
            @_wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            self.callback_clicked = wrapper
            return wrapper
        
        return decorator

    # properties
    @property
    def uv(self):
        return self._uv
    @uv.setter
    def uv(self, value: Vec2):
        """
        If parent is element, uses element-relative coordinates.
        If not, uses window-relative coordinates.
        """
        self._uv = value.copy()
        if issubclass(type(self.parent), Element):
            self._pos = _uv2pos_elm(value.tuple, *self.size, *self.parent.size)
        else:
            self._pos = _uv2pos(value.tuple, *self.size)
        self.set_dirty()
    @property
    def u(self):
        return self._uv.x
    @u.setter
    def u(self, value: float):
        """
        If parent is element, uses element-relative coordinates.
        If not, uses window-relative coordinates.
        """
        self._uv.x = value
        if issubclass(type(self.parent), Element):
            self._pos = _uv2pos_elm(self.uv.tuple, *self.size, *self.parent.size) # pyright: ignore
        else:
            self._pos = _uv2pos(self.uv.tuple, *self.size)
        self.set_dirty()
    @property
    def v(self):
        return self._uv.y
    @v.setter
    def v(self, value: float):
        """
        If parent is element, uses element-relative coordinates.
        If not, uses window-relative coordinates.
        """
        self._uv.y = value
        if issubclass(type(self.parent), Element):
            self._pos = _uv2pos_elm(self.uv.tuple, *self.size, *self.parent.size) # pyright: ignore
        else:
            self._pos = _uv2pos(self.uv.tuple, *self.size)
        self.set_dirty()

    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self, value: Vec2):
        self._pos = value.copy()
        if isinstance(self.parent, Element):
            self._uv = _pos2uv_elm(value, *self.size, *self.parent.size)
        else:
            self._uv = _pos2uv(value, *self.size)
        self.set_dirty()
        
    @property
    def abs_pos(self):
        """Read-only"""
        pos = self.pos.copy()
        for parent in self.get_parents():
            pos += parent.pos
        return pos

    @property
    def size(self):
        return self._size
    @size.setter
    def size(self, value: Vec2):
        self._size = value.copy()
        self.uv = self.uv
        self.set_dirty()

    @property
    def anchor(self):
        return self._anchor
    @anchor.setter
    def anchor(self, value: Anchor):
        self._anchor = value
        self.set_dirty()

    # get methods
    def get_parents(self):
        parents: list[Element] = []
        current = self

        while isinstance(current.parent, Element):
            parents.append(current.parent)
            current = current.parent

        return parents

    # set methods
    def set_padding(self, padding: Padding):
        self._padding = padding
        self.set_dirty()
    def set_border(self, border: Border):
        self._border = border
        self.set_dirty()

    # children
    def set_child(self, element: Element):
        self.children.append(element)
        element.parent = self
    def rm_child(self, element: Element):
        self.children.remove(element)
        element.parent = None

class Frame(event.EventObject):
    """
    Frame manages mouse events and other events.
    """
    g_hovering: _Optional[Frame] = None
    @staticmethod
    def _reset_g_flag():
        Frame.g_hovering = None

    def __init__(self, element: Element) -> None:
        self.element = element
        self.hovering = False
        self.clicking = False

    def update(self):
        last_hovering = self.hovering # for enter and leave detecting

        self.hovering = False
        self.clicking = False

        if Frame.g_hovering: return
        if self.element.collide_pos(mouse.get_pos()):
            Frame.g_hovering = self
            self.hovering = True
            if mouse.get_pressed().left:
                self.clicking = True

        # entering
        if last_hovering == False and self.hovering == True:
            if self.element.callback_enter:
                self.element.callback_enter()
        # leaving
        elif last_hovering == True and self.hovering == False:
            if self.element.callback_leave:
                self.element.callback_leave()

    @event.OnUpdate()
    def on_update(self):
        if Frame.g_hovering is not self: return
        if self.element.callback_hovered:
            self.element.callback_hovered()

    @event.OnMousewheelScroll()
    def on_mousewheelscroll(self, e):
        if Frame.g_hovering is not self: return
        element: _Optional[Element] = self.element
        while element is not None:
            if element.callback_mousewheelscrolled:
                element.callback_mousewheelscrolled(e)
                return
            parent = element.parent
            element = parent if isinstance(parent, Element) else None

    @event.OnMousebuttonUp(mouse.left)
    def on_mousebuttonup(self, e):
        if Frame.g_hovering is not self: return
        if self.element.callback_clicked:
            self.element.callback_clicked()


class PanelBase(Element):
    """Not implemented yet."""
    def __init__(
            self, 
            u: float, 
            v: float, 
            width: float, 
            height: float, 
            padding: profile.Padding, 
            border: profile.Border, 
            animator: GAnimator | None = None) -> None:
        super().__init__(u, v, width, height, padding, border, animator)