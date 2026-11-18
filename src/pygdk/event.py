from .base import *
from . import key, mouse
from . import profile

import pygame as _pygame
import sys as _sys
from enum import (
    Flag as _Flag, 
    auto as _auto
    )
from dataclasses import (
    dataclass as _dataclass, 
    field as _field
    )
from typing import (
    Callable as _Callable, 
    Any as _Any, 
    Self as _Self
    )
# TODO: Not complete yet. temporary.

# ===== Permissions =====
class InputPermission(_Flag):
    WASD = _auto()
    Arrows = _auto()

# ===== Global value in this file =====
pressedKeys: _pygame.key.ScancodeWrapper = _pygame.key.ScancodeWrapper()
pressedKeymods: int = 0
# pressedMousebuttons: mouse.MouseButtonData = mouse.MouseButtonData(False, False, False, False, False)
# mousePos: tuple[int, int] = (0, 0)

def _updateKeyEvents():
    global pressedKeys, pressedKeymods
    pressedKeys = _pygame.key.get_pressed()
    pressedKeymods = _pygame.key.get_mods()

def _updateMouseEvents():
    b = _pygame.mouse.get_pressed(5)
    mouse._pressedButton = mouse.MouseButtonData(b[0], b[1], b[2], b[3], b[4])

def _updateMousePos():
    assert profile.window
    mouse._pos = profile.window.get_mousePos()

# ===== Dataclasses =====
@_dataclass
class KeyEventData:
    keyData: key.KeyType
    pressed: bool
    mods: int

    def isShift(self, optional: str | None = None):
        if not self.pressed: return False
        if optional == 'r':
            return self.mods & _pygame.KMOD_RSHIFT > 0
        if optional == 'l':
            return self.mods & _pygame.KMOD_LSHIFT > 0
        return self.mods & _pygame.KMOD_SHIFT > 0

    def isCtrl(self, optional: str | None = None):
        if not self.pressed: return False
        if optional == 'r':
            return self.mods & _pygame.KMOD_RCTRL > 0
        if optional == 'l':
            return self.mods & _pygame.KMOD_LCTRL > 0
        return self.mods & _pygame.KMOD_CTRL > 0

    def isAlt(self, optional: str | None = None):
        if not self.pressed: return False
        if optional == 'r':
            return self.mods & _pygame.KMOD_RALT > 0
        if optional == 'l':
            return self.mods & _pygame.KMOD_LALT > 0
        return self.mods & _pygame.KMOD_ALT > 0
    
@_dataclass
class KeyModData:
    flag: int

    def isShift(self, optional: str | None = None):
        return self.flag & _pygame.KMOD_SHIFT

    def isCtrl(self, optional: str | None = None):
        return self.flag & _pygame.KMOD_CTRL

    def isAlt(self, optional: str | None = None):
        return self.flag & _pygame.KMOD_ALT

# ===== Event =====

from functools import update_wrapper as _update_wrapper

class EventCallable:
    def __init__(self, func: _Callable) -> None:
        self.owner = None
        self.func = func
        _update_wrapper(self, func, updated=())

    def __set_name__(self, owner, name):
        self.owner = owner
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self.func
        return self.func.__get__(instance, owner)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

def OnUpdate():
    def decorator(func):
        event_func = EventCallable(func)
        EventManager.register_update(event_func)
        return event_func
    return decorator

def OnWindowResized():
    def decorator(func):
        event_func = EventCallable(func)
        EventManager.register_windowresized(event_func)
        return event_func
    return decorator

def OnKeydown(key: key.KeyType):
    def decorator(func):
        event_func = EventCallable(func)
        EventManager.register_keydown(key, event_func)
        return event_func
    return decorator

def OnKeyup(key: key.KeyType):
    def decorator(func):
        event_func = EventCallable(func)
        EventManager.register_keyup(key, event_func)
        return event_func
    return decorator

def OnMousemove():
    def decorator(func):
        event_func = EventCallable(func)
        EventManager.register_mousemove(event_func)
        return event_func
    return decorator

def OnMousebuttonDown(button: mouse.MouseButtonType):
    def decorator(func):
        event_func = EventCallable(func)
        EventManager.register_mousebuttondown(button, event_func)
        return event_func
    return decorator

def OnMousebuttonUp(button: mouse.MouseButtonType):
    def decorator(func):
        event_func = EventCallable(func)
        EventManager.register_mousebuttonup(button, event_func)
        return event_func
    return decorator

# mouse wheel
def OnMousewheelScroll():
    def decorator(func):
        event_func = EventCallable(func)
        EventManager.register_mousewheelscroll(event_func)
        return event_func
    return decorator

class EventType(_Flag):
    OnUpdate = _auto()
    OnWindowResized = _auto()
    OnKeydown = _auto()
    OnKeyup = _auto()
    OnMousebuttonDown = _auto()
    OnMousebuttonUp = _auto()
    OnMousemove = _auto()
    OnMousewheelScroll = _auto()

@_dataclass
class HandlerBase:
    func: EventCallable
    instances: list[_Any] = _field(default_factory=list, init=False)

@_dataclass
class Handler(HandlerBase):
    pass

@_dataclass
class KeyHandler(HandlerBase):
    key: int

@_dataclass
class MousebuttonHandler(HandlerBase):
    mousebutton: int

class EventObject:
    def __new__(cls: type[_Self], *args, **kwargs) -> _Self:
        instance = super().__new__(cls)
        EventManager.link_instance(instance)
        return instance

class EventManager:
    _handlers: list[tuple[EventType, Handler | KeyHandler | MousebuttonHandler]] = []

    @staticmethod
    def _handler_key(event_type: EventType, handler: Handler | KeyHandler | MousebuttonHandler):
        """"""
        if isinstance(handler, KeyHandler):
            return (event_type, handler.func.func, handler.key)
        if isinstance(handler, MousebuttonHandler):
            return (event_type, handler.func.func, handler.mousebutton)
        return (event_type, handler.func.func, None)

    @staticmethod
    def _register_handler(event_type: EventType, handler: Handler | KeyHandler | MousebuttonHandler):
        if any(EventManager._handler_key(event_type, existing_handler) == EventManager._handler_key(event_type, handler)
               for existing_event_type, existing_handler in EventManager._handlers
               if existing_event_type == event_type):
            return
        EventManager._handlers.append((event_type, handler))

    @staticmethod
    def link_instance(instance: _Any):
        '''
        Called by EventObject.
        '''
        for _event_type, _handler in EventManager._handlers:
            owner = _handler.func.owner
            if owner is not None and isinstance(instance, owner):
                # Link the instance if it is not already linked to the handler.
                if not any(existing_instance is instance for existing_instance in _handler.instances):
                    _handler.instances.append(instance)

    # ===== Register =====
    @staticmethod
    def register_update(func: EventCallable):
        EventManager._register_handler(EventType.OnUpdate, Handler(func))

    @staticmethod
    def register_windowresized(func: EventCallable):
        EventManager._register_handler(EventType.OnWindowResized, Handler(func))

    @staticmethod
    def register_keydown(key: key.KeyType, func: EventCallable):
        EventManager._register_handler(EventType.OnKeydown, KeyHandler(func, key.keyCode))

    @staticmethod
    def register_keyup(key: key.KeyType, func: EventCallable):
        EventManager._register_handler(EventType.OnKeyup, KeyHandler(func, key.keyCode))

    @staticmethod
    def register_mousemove(func: EventCallable):
        EventManager._register_handler(EventType.OnMousemove, Handler(func))

    @staticmethod
    def register_mousebuttondown(button: mouse.MouseButtonType, func: EventCallable):
        EventManager._register_handler(EventType.OnMousebuttonDown, MousebuttonHandler(func, button.buttonType))

    @staticmethod
    def register_mousebuttonup(button: mouse.MouseButtonType, func: EventCallable):
        EventManager._register_handler(EventType.OnMousebuttonUp, MousebuttonHandler(func, button.buttonType))

    @staticmethod
    def register_mousewheelscroll(func: EventCallable):
        EventManager._register_handler(EventType.OnMousewheelScroll, Handler(func))

    # ===== Register ===== end

    @staticmethod
    def update(events: list[_pygame.event.Event]):
        EventManager.eventQueue = events

    @staticmethod
    def dispatch():
        # OnUpdate
        for handler in [handler for event_type, handler in EventManager._handlers
                        if event_type == EventType.OnUpdate]:
            if handler.func.owner is not None:
                for instance in handler.instances:
<<<<<<< HEAD
                    handler.func.func(instance)
            else:
                handler.func.func()
=======
                    handler.func(instance)
            else:
                handler.func()
>>>>>>> ae538d05c1ce8f2e5ee51a797bd15b2b06e5c7aa

        for e in EventManager.eventQueue:
            handlers: list[HandlerBase] = []
            if e.type == _pygame.QUIT:
                _pygame.quit()
                _sys.exit()

            # Others
            if e.type == _pygame.WINDOWRESIZED:
                handlers += [handler for event_type, handler in EventManager._handlers
                             if event_type == EventType.OnWindowResized]

            if e.type == _pygame.KEYDOWN:
                handlers += [handler for event_type, handler in EventManager._handlers
                             if event_type == EventType.OnKeydown and handler.key == e.key] # pyright: ignore

            if e.type == _pygame.KEYUP:
                handlers += [handler for event_type, handler in EventManager._handlers
                             if event_type == EventType.OnKeyup and handler.key == e.key] # pyright: ignore
                    
            if e.type == _pygame.MOUSEMOTION:
                handlers += [handler for event_type, handler in EventManager._handlers
                             if event_type == EventType.OnMousemove]

            if e.type == _pygame.MOUSEBUTTONDOWN:
                handlers += [handler for event_type, handler in EventManager._handlers
                             if event_type == EventType.OnMousebuttonDown and handler.mousebutton == e.button] # pyright: ignore
            
            if e.type == _pygame.MOUSEBUTTONUP:
                handlers += [handler for event_type, handler in EventManager._handlers
                             if event_type == EventType.OnMousebuttonUp and handler.mousebutton == e.button] # pyright: ignore

            if e.type == _pygame.MOUSEWHEEL:
                handlers += [handler for event_type, handler in EventManager._handlers
                             if event_type == EventType.OnMousewheelScroll]

            for handler in handlers:
                if handler.func.owner is not None:
                    for instance in handler.instances:
                        handler.func.func(instance, e)
                else:
                    handler.func.func(e)

# ===== User Function ======
def getKey(key_data: key.KeyType) -> KeyEventData:
    keyStatus = KeyEventData(key_data, pressedKeys[key_data.keyCode], pressedKeymods)
    return keyStatus

def getMousePos() -> Vec2:
    return mouse._pos

def getMousePressed() -> mouse.MouseButtonData:
    return mouse.get_pressed()

def getMod():
    return KeyModData(_pygame.key.get_mods())

# ===== Input producing like Movements =====
class Input:
    vertical = 0
    horizontal = 0
    permission = InputPermission.Arrows | InputPermission.WASD
    
    @staticmethod
    def update():
        Input.vertical = 0
        Input.horizontal = 0
        if Input.permission & InputPermission.Arrows:
            if getKey(key.UP).pressed:
                Input.vertical -= 1
            if getKey(key.DOWN).pressed:
                Input.vertical += 1
            if getKey(key.LEFT).pressed:
                Input.horizontal -= 1
            if getKey(key.RIGHT).pressed:
                Input.horizontal += 1
        if Input.permission & InputPermission.WASD:
            if getKey(key.w).pressed and Input.vertical != -1:
                Input.vertical -= 1
            if getKey(key.s).pressed and Input.vertical != 1:
                Input.vertical += 1
            if getKey(key.a).pressed and Input.horizontal != -1:
                Input.horizontal -= 1
            if getKey(key.d).pressed and Input.horizontal != 1:
                Input.horizontal += 1