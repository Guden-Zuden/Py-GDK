from . import Key, Mouse
from . import Utils
from .Base import *

import pygame as _pygame
import sys as _sys
from pygame import constants as _cst
from dataclasses import dataclass
from enum import Flag, auto
from typing import Optional, Any, Callable

__all__ = ["InputPermission", "getKey"]

# TODO Fix OnUpdate function (maybe misunderstanding) (Execute per frame)

# ===== Permissions =====
class InputPermission(Flag):
    WASD = auto()
    Arrows = auto()

# ===== Global value in this file =====
pressedKeys: _pygame.key.ScancodeWrapper = _pygame.key.ScancodeWrapper()
pressedKeymods: int = 0
# pressedMousebuttons: Mouse.MouseButtonData = Mouse.MouseButtonData(False, False, False, False, False)
# mousePos: tuple[int, int] = (0, 0)

def _updateKeyEvents():
    global pressedKeys, pressedKeymods
    pressedKeys = _pygame.key.get_pressed()
    pressedKeymods = _pygame.key.get_mods()

def _updateMouseEvents():
    b = _pygame.mouse.get_pressed(5)
    Mouse._pressedButton = Mouse.MouseButtonData(b[0], b[1], b[2], b[3], b[4])

def _updateMousePos():
    x, y = _pygame.mouse.get_pos()
    Mouse._pos = Pos(x, y)

# ===== KeyData included some funcs =====
@dataclass
class KeyEventData:
    keyData: Key.KeyType
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
    

# ===== Event =====

from functools import wraps

def OnUpdate():
    def decorator(func):
        EventManager.register_update(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def OnWindowResized():
    def decorator(func):
        EventManager.register_windowresized(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def OnKeydown(key: Key.KeyType):
    def decorator(func):
        EventManager.register_keydown(key, func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorator

def OnKeyup(key: Key.KeyType):
    def decorator(func):
        EventManager.register_keyup(key, func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def OnMousemove():
    def decorator(func):
        EventManager.register_mousemove(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def OnMousebuttonDown(button: Mouse.MouseButtonType):
    def decorator(func):
        EventManager.register_mousebuttondown(button, func)
    
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def OnMousebuttonUp(button: Mouse.MouseButtonType):
    def decorator(func):
        EventManager.register_mousebuttonup(button, func)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

class EventManager:
    eventQueue:                 list[_pygame.event.Event]   = []
    _update_handlers:           list[Callable]              = []
    _windowresized_handlers:    list[Callable]              = []
    _keydown_handlers:          dict[int, list[Callable]]   = {}
    _keyup_handlers:            dict[int, list[Callable]]   = {}
    _mousebuttondown_handlers:  dict[int, list[Callable]]   = {}
    _mousebuttonup_handlers:    dict[int, list[Callable]]   = {}
    _mousemove_handlers:        list[Callable]              = []

    @staticmethod
    def register_update(func: Callable):
        EventManager._update_handlers.append(func)

    @staticmethod
    def register_windowresized(func: Callable):
        EventManager._windowresized_handlers.append(func)

    @staticmethod
    def register_keydown(key: Key.KeyType, func: Callable):
        EventManager._keydown_handlers.setdefault(key.keyCode, []).append(func)

    @staticmethod
    def register_keyup(key: Key.KeyType, func: Callable):
        EventManager._keyup_handlers.setdefault(key.keyCode, []).append(func)

    @staticmethod
    def register_mousemove(func: Callable):
        EventManager._mousemove_handlers.append(func)

    @staticmethod
    def register_mousebuttondown(button: Mouse.MouseButtonType, func: Callable):
        EventManager._mousebuttondown_handlers.setdefault(button.buttonType, []).append(func)

    @staticmethod
    def register_mousebuttonup(button: Mouse.MouseButtonType, func: Callable):
        EventManager._mousebuttonup_handlers.setdefault(button.buttonType, []).append(func)

    @staticmethod
    def update(events: list[_pygame.event.Event]):
        EventManager.eventQueue = events

    @staticmethod
    def dispatch():
        updated = False
        for e in EventManager.eventQueue:
            if e.type == _pygame.QUIT:
                _pygame.quit()
                _sys.exit()

            if updated == False:
                handlers = EventManager._update_handlers
                for h in handlers:
                    h(e)
                updated = True

            if e.type == _pygame.WINDOWRESIZED:
                handlers = EventManager._windowresized_handlers
                for h in handlers:
                    h(e)

            if e.type == _pygame.KEYDOWN:
                handlers = EventManager._keydown_handlers.get(e.key, [])
                for h in handlers:
                    h(e)

            if e.type == _pygame.KEYUP:
                handlers = EventManager._keyup_handlers.get(e.key, [])
                for h in handlers:
                    h(e)
                    
            if e.type == _pygame.MOUSEMOTION:
                for h in EventManager._mousemove_handlers:
                    h(e)

            if e.type == _pygame.MOUSEBUTTONDOWN:
                handlers = EventManager._mousebuttondown_handlers.get(e.button, [])
                for h in handlers:
                    h(e)
            
            if e.type == _pygame.MOUSEBUTTONUP:
                handlers = EventManager._mousebuttonup_handlers.get(e.button, [])
                for h in handlers:
                    h(e)


# ===== User Function ======
def getKey(key_data: Key.KeyType) -> KeyEventData:
    keyStatus = KeyEventData(key_data, pressedKeys[key_data.keyCode], pressedKeymods)
    return keyStatus

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
            if getKey(Key.UP).pressed:
                Input.vertical -= 1
            if getKey(Key.DOWN).pressed:
                Input.vertical += 1
            if getKey(Key.LEFT).pressed:
                Input.horizontal -= 1
            if getKey(Key.RIGHT).pressed:
                Input.horizontal += 1
        if Input.permission & InputPermission.WASD:
            if getKey(Key.w).pressed and Input.vertical != -1:
                Input.vertical -= 1
            if getKey(Key.s).pressed and Input.vertical != 1:
                Input.vertical += 1
            if getKey(Key.a).pressed and Input.horizontal != -1:
                Input.horizontal -= 1
            if getKey(Key.d).pressed and Input.horizontal != 1:
                Input.horizontal += 1


# def set_event(key_status: KeyEventData):



