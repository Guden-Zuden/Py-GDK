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
    u = 2 / profile.width * (pos.x + width - profile.width/2)
    v = 2 / profile.height * (pos.y + height - profile.height/2)
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

def _updateMouseStatus():
    from . import Button, ImageButton, LinkLabel
    if isinstance(GUIBase.g_hoveredObj, (Button, ImageButton, LinkLabel)):
        _pg.mouse.set_cursor(_pg.SYSTEM_CURSOR_HAND)
    else:
        _pg.mouse.set_cursor(_pg.SYSTEM_CURSOR_ARROW)

######################################
#############  GUI Base  #############
######################################
class GUIBase(event.EventObject):
    # for debug =====
    update_count = 0
    draw_count   = 0
    # ===============

    g_hoveredObj: _Optional[GUIBase] = None
    g_focusedObj: _Optional[GUIBase] = None

    _debug_position_stack: list[Vec2] = []
    
    def __init__(self, u: float, v: float, width: float, height: float,
                 padding = profile.default_padding, border: Border = Border(0, colors.WHITE),
                 animator: _Optional["GAnimator"] = None, no_register = False) -> None:        
        self.u, self.v = u, v
        self.size = Vec2(width, height)
        self.pos = Vec2(
            profile.width/2 + profile.width/2 * u - self.size.width/2,
            profile.height/2 + profile.height/2 * v - self.size.height/2)
        self.is_hide = False

        self.padding = padding
        self.border = border

        self.animator = animator

        self.hovered = False
        self.clicked = False
        self.focused = False

        self.parent: _Optional[object] = None
        self.children: list[GUIBase] = [] # event
        self.inners: list[GUIBase] = []   # size

        self.event_func: _Optional[_Callable] = None

        self.no_register = no_register

        if profile.is_show_gui_positions:
            GUIBase._debug_position_stack.append(self.pos)

        self.create_surface()

    def _regist_events(self):
        if not self.no_register:
            print(f"{self} events registed.")
            for component in self.children:
                component._regist_events()
            event.EventManager.register_update(type(self).on_hovered)
            event.EventManager.register_mousebuttonup(mouse.left, type(self).on_executed)
            event.EventManager.link_instance(self)

    def create_surface(self):
        self.surface = _pg.Surface((self.size).tuple, _pg.SRCALPHA)
        self.border_surface = _pg.Surface((self.size).tuple, _pg.SRCALPHA)
        for inner in self.inners:
            inner.create_surface()
        
    def _centering(self):
        self.pos.x -= self.size.width/2
        self.pos.y -= self.size.height/2

    def update(self) -> None:
        if self.is_hide: return
        GUIBase.update_count += 1

        self.on_update()

        if self.animator:
            self.animator.update()

        # if self.size.is_dirty():
        self.create_surface()
            # self.size.reset()
        
        if self.parent is None: return

    def draw(self, surface: _Optional[_pg.Surface] = None) -> None:
        if self.is_hide: return
        GUIBase.draw_count += 1
        if surface is None: surface = self.surface
        self.on_draw(surface)
        self.surface.fill((0,0,0,0))

        if self.border.width > 0:
            border_rect = surface.get_rect()

            width = int(self.border.width)

            if width > 0: _pg.draw.rect(self.border_surface, self.border.color, border_rect, width)

    def _flush(self, surface: _Optional[_pg.Surface] = None):
        """If surface is not specified, profile.surface will be used."""
        assert profile.window
        if surface is None:
            surface = profile.window.surface

        surface.blit(self.surface, (self.pos).tuple)
        surface.blit(self.border_surface, (self.pos).tuple)

    def stick(self, gui_obj: GUIBase, dir: Direction):
        self.pos.x = gui_obj.pos.x + gui_obj.size.width/2 - self.size.width/2
        self.pos.y = gui_obj.pos.y + gui_obj.size.height/2 - self.size.height/2

        if dir & Direction.TOP:
            self.pos.y = gui_obj.pos.y - self.size.height
        elif dir & Direction.BOTTOM:
            self.pos.y = gui_obj.pos.y + gui_obj.size.height

        if dir & Direction.LEFT:
            self.pos.x = gui_obj.pos.x - self.size.width
        elif dir & Direction.RIGHT:
            self.pos.x = gui_obj.pos.x + gui_obj.size.width
        return self

    def get_rect(self):
        return _pg.Rect(
            self.pos.x,
            self.pos.y,
            self.size.width,
            self.size.height
        )

    def get_size(self):
        return (self.size.width, self.size.height)

    @staticmethod
    def _reset_g_flag():
        GUIBase.g_hoveredObj = None

    def add_child(self, gui: GUIBase):
        gui.parent = self
        self.children.append(gui)

    def add_inner(self, gui: GUIBase):
        self.inners.append(gui)

    def get_top(self):
        gui = self

        while isinstance(gui.parent, GUIBase):
            gui = gui.parent

        return gui

    def get_parents(self):
        parents: list[GUIBase] = []
        gui = self

        while isinstance(gui.parent, GUIBase):
            gui = gui.parent
            parents.append(gui)

        return parents

    # events
    def on_hovered(self):
        with _BenchMark(f"{self}.on_hovered()"):
            if self.parent is None: return
            if self.is_hide: return
            from .. import layer
            if (layer.LayerManager.current_layer and 
                not self in layer.LayerManager.current_layer._GUIComponent_stack):
                flag = True

                for parent in self.get_parents():
                    if parent in layer.LayerManager.current_layer._GUIComponent_stack:
                        flag = False
                if flag:
                    self.hovered = False
                    return

            for child in self.children:
                child.on_hovered()

            mouse_pos = event.getMousePos()
            rect = self.get_rect()

            for parent in self.get_parents():
                rect.x += parent.pos.x
                rect.y += parent.pos.y

            isCollide = _pg.Rect.collidepoint(rect, *mouse_pos)

            if GUIBase.g_hoveredObj is None:
                if isCollide:
                    GUIBase.g_hoveredObj = self
                    self.hovered = True
                else:
                    self.hovered = False
            if self.hovered:
                if mouse.get_pressed().left:
                    self.clicked = True
                else:
                    self.clicked = False
            else:
                self.clicked = False
            if not isCollide:
                self.hovered = False

    def on_executed(self, e):
        if self.parent is None: return
        if self.event_func and self.hovered:
            self.event_func()

    def on_update(self):
        pass
    def on_draw(self, surface: _pg.Surface):
        pass

    # setters
    def set_pos(self, x: int | float, y: int | float):
        self.pos = Vec2(x, y)

    def set_uv(self, u: float, v: float):
        self.u, self.v = u, v
        self.pos = _uv2pos((u, v), self.size.width, self.size.height)

    def set_size(self, width: float, height: float):
        self.size.width, self.size.height = width, height

    def sync_size_to(self, component: GUIBase):
        self.size = component.size
    #

    def info(self):
        return {self.__str__(): [child.info() for child in self.children]}

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
            feedback_option: _Optional[FeedbackOption] = None) -> None:
        self._frame = Frame(self)
        
        self._uv = Vec2(u, v)
        self._pos = _uv2pos((u, v), width, height)
        self._size = Vec2(width, height)

        self.animator = animator

        self._padding = padding
        self._border = border

        self.parent: _Optional[object] = None
        self.children: list[Element] = []

        # TODO: hovered, --clicked-- pressed and focused states should be implemented?
        
        # properties
        self.visible = True

        self.create_surface()

        # event callbacks
        self.callback_enter: _Optional[_Callable] = None
        self.callback_leave: _Optional[_Callable] = None
        self.callback_mousewheelscrolled: _Optional[_Callable] = None
        self.callback_hovered: _Optional[_Callable] = None
        self.callback_pressed: _Optional[_Callable] = None
        self.callback_clicked: _Optional[_Callable] = None

        # dirty flags
        self._dirty = True

    def stick(self, target: Element, direction: Direction):
        """
        Stick to target element.
        """
        self.pos = Vec2(
            target.pos.x + target.size.width/2 - self.size.width/2,
            target.pos.y + target.size.height/2 - self.size.height/2)

        if direction & Direction.TOP:
            self.pos.y = target.pos.y - self.size.height
        elif direction & Direction.BOTTOM:
            self.pos.y = target.pos.y + target.size.height

        if direction & Direction.LEFT:
            self.pos.x = target.pos.x - self.size.width
        elif direction & Direction.RIGHT:
            self.pos.x = target.pos.x + target.size.width

        return self

    def should_update(self) -> bool:
        """if visible is true"""
        return (self.visible)

    def update(self) -> None:
        if self.visible == False: return

        self._frame.update()
        self.on_update()

        if self.animator:
            self.animator.update()

    def should_draw(self) -> bool:
        """if visible and dirty flag is true"""
        return (self.visible
                and self._dirty)

    def draw(self) -> None:
        """
        #### Description
            Draw on self.surface
        """
        if self.visible == False: return
        if self._dirty == False: return

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

    def flush(self, surface: _Optional[_pg.Surface] = None):
        """
        #### Description
            If self is child element, draw on parent's surface.
            `surface` is only for this class, Element.
            Call with no arguments.
        """
        assert profile.window
        if not self.should_flush(): return

        if surface:
            surface.blit(self.surface, self._pos.tuple)

        for child in self.children:
            child.flush(self.surface)
            child.surface

        if surface is None:
            profile.window.surface.blit(self.surface, self.abs_pos.tuple)

            if self._border:
                profile.window.surface.blit(
                    self.border_surface, (self.abs_pos - self._border.width).tuple)

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
                logger.debug(f"OnEnter executed: %s", self)
                return func(*args, **kwargs)

            self.callback_enter = wrapper
            return wrapper

        return decorator

    def OnLeave(self):
        def decorator(func: _Callable):
            @_wraps(func)
            def wrapper(*args, **kwargs):
                logger.debug(f"OnLeave executed: %s", self)
                return func(*args, **kwargs)

            self.callback_leave = wrapper
            return wrapper

        return decorator

    def OnMousewheelScroll(self):
        def decorator(func: _Callable):
            @_wraps(func)
            def wrapper(*args, **kwargs):
                logger.debug(f"OnMousewheelScroll executed: %s", self)
                return func(*args, **kwargs)

            self.callback_mousewheelscrolled = wrapper
            return wrapper

        return decorator


    def OnHovered(self):
        def decorator(func: _Callable):
            @_wraps(func)
            def wrapper(*args, **kwargs):
                logger.debug(f"OnHovered executed: %s", self)
                return func(*args, **kwargs)

            self.callback_hovered = wrapper
            return wrapper

        return decorator

    def OnPressed(self):
        def decorator(func):
            @_wraps(func)
            def wrapper(*args, **kwargs):
                logger.debug(f"OnPressed executed: %s", self)

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
        """Uses window-relative coordinates; do not use to position child elements."""
        self._uv = value.copy()
        self._pos = _uv2pos(value.tuple, *self.size)
        self.set_dirty()
    @property
    def u(self):
        return self._uv.x
    @u.setter
    def u(self, value: float):
        """Uses window-relative coordinates; do not use to position child elements."""
        self._uv.x = value
        self._pos = _uv2pos(self._uv.tuple, *self.size)
        self.set_dirty()
    @property
    def v(self):
        return self._uv.y
    @v.setter
    def v(self, value: float):
        """Uses window-relative coordinates; do not use to position child elements."""
        self._uv.y = value
        self._pos = _uv2pos(self._uv.tuple, *self.size)
        self.set_dirty()

    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self, value: Vec2):
        self._pos = value.copy()
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
        if self.element.callback_mousewheelscrolled:
            self.element.callback_mousewheelscrolled(e)

    @event.OnMousebuttonUp(mouse.left)
    def on_mousebuttonup(self, e):
        if Frame.g_hovering is not self: return
        if self.element.callback_clicked:
            self.element.callback_clicked()


class PanelBase(Element):
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