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
    Self as _Self,
    Optional as _Optional,
    cast as _cast,
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
    """Keep method metadata while exposing normal descriptor binding."""

    def __init__(self, func: _Callable[..., _Any]) -> None:
        self.owner: type | None = None
        self.name: str | None = None
        self.func = func
        _update_wrapper(self, func, updated=())

    def __set_name__(self, owner: type, name: str) -> None:
        self.owner = owner
        self.name = name

    def __get__(
        self,
        instance: _Any,
        owner: type | None = None,
    ) -> _Callable[..., _Any]:
        if instance is None:
            return self.func
        return self.func.__get__(instance, owner)

    def __call__(self, *args: _Any, **kwargs: _Any) -> _Any:
        return self.func(*args, **kwargs)


_EventDecorator = _Callable[[_Callable[..., _Any]], EventCallable]


def _event_decorator(
    register: _Callable[[EventCallable], None],
) -> _EventDecorator:
    def decorator(func: _Callable[..., _Any]) -> EventCallable:
        event_func = EventCallable(func)
        register(event_func)
        return event_func

    return decorator


def OnUpdate() -> _EventDecorator:
    return _event_decorator(EventManager.register_update)


def OnWindowResized() -> _EventDecorator:
    return _event_decorator(EventManager.register_windowresized)


def OnKeydown(key: key.KeyType) -> _EventDecorator:
    return _event_decorator(lambda func: EventManager.register_keydown(key, func))


def OnKeyup(key: key.KeyType) -> _EventDecorator:
    return _event_decorator(lambda func: EventManager.register_keyup(key, func))


def OnMousemove() -> _EventDecorator:
    return _event_decorator(EventManager.register_mousemove)


def OnMousebuttonDown(button: mouse.MouseButtonType) -> _EventDecorator:
    return _event_decorator(
        lambda func: EventManager.register_mousebuttondown(button, func)
    )


def OnMousebuttonUp(button: mouse.MouseButtonType) -> _EventDecorator:
    return _event_decorator(
        lambda func: EventManager.register_mousebuttonup(button, func)
    )


def OnMousewheelScroll() -> _EventDecorator:
    return _event_decorator(EventManager.register_mousewheelscroll)

class EventType(_Flag):
    OnUpdate = _auto()
    OnWindowResized = _auto()
    OnKeydown = _auto()
    OnKeyup = _auto()
    OnMousebuttonDown = _auto()
    OnMousebuttonUp = _auto()
    OnMousemove = _auto()
    OnMousewheelScroll = _auto()


_PYGAME_EVENT_TYPES: dict[int, EventType] = {
    _pygame.WINDOWRESIZED: EventType.OnWindowResized,
    _pygame.KEYDOWN: EventType.OnKeydown,
    _pygame.KEYUP: EventType.OnKeyup,
    _pygame.MOUSEMOTION: EventType.OnMousemove,
    _pygame.MOUSEBUTTONDOWN: EventType.OnMousebuttonDown,
    _pygame.MOUSEBUTTONUP: EventType.OnMousebuttonUp,
    _pygame.MOUSEWHEEL: EventType.OnMousewheelScroll,
}


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


def _get_event_callable(handler: HandlerBase) -> EventCallable:
    # Read the stored descriptor itself rather than its bound-method view.
    return _cast(EventCallable, handler.__dict__["func"])


class EventObject:
    def __new__(cls: type[_Self], *args, **kwargs) -> _Self:
        instance = super().__new__(cls)
        EventManager.link_instance(instance)
        return instance

class EventManager:
    _handlers: list[tuple[EventType, HandlerBase]] = []
    eventQueue: list[_pygame.event.Event] = []

    @staticmethod
    def _handler_key(
        event_type: EventType,
        handler: HandlerBase,
    ) -> tuple[EventType, _Callable[..., _Any], _Optional[int]]:
        event_func = _get_event_callable(handler)
        if isinstance(handler, KeyHandler):
            trigger = handler.key
        elif isinstance(handler, MousebuttonHandler):
            trigger = handler.mousebutton
        else:
            trigger = None
        return event_type, event_func.func, trigger

    @staticmethod
    def _register_handler(event_type: EventType, handler: HandlerBase) -> None:
        handler_key = EventManager._handler_key(event_type, handler)
        for existing_event_type, existing_handler in EventManager._handlers:
            if (
                existing_event_type == event_type
                and EventManager._handler_key(existing_event_type, existing_handler)
                == handler_key
            ):
                return
        EventManager._handlers.append((event_type, handler))

    @staticmethod
    def link_instance(instance: _Any) -> None:
        """Associate an object with decorated handlers declared on its class."""
        for _, handler in EventManager._handlers:
            owner = _get_event_callable(handler).owner
            if owner is not None and isinstance(instance, owner):
                if not any(existing is instance for existing in handler.instances):
                    handler.instances.append(instance)

    # ===== Register =====
    @staticmethod
    def register_update(func: EventCallable) -> None:
        EventManager._register_handler(EventType.OnUpdate, Handler(func))

    @staticmethod
    def register_windowresized(func: EventCallable) -> None:
        EventManager._register_handler(EventType.OnWindowResized, Handler(func))

    @staticmethod
    def register_keydown(key: key.KeyType, func: EventCallable) -> None:
        EventManager._register_handler(
            EventType.OnKeydown,
            KeyHandler(func, key.keyCode),
        )

    @staticmethod
    def register_keyup(key: key.KeyType, func: EventCallable) -> None:
        EventManager._register_handler(
            EventType.OnKeyup,
            KeyHandler(func, key.keyCode),
        )

    @staticmethod
    def register_mousemove(func: EventCallable) -> None:
        EventManager._register_handler(EventType.OnMousemove, Handler(func))

    @staticmethod
    def register_mousebuttondown(
        button: mouse.MouseButtonType,
        func: EventCallable,
    ) -> None:
        EventManager._register_handler(
            EventType.OnMousebuttonDown,
            MousebuttonHandler(func, button.buttonType),
        )

    @staticmethod
    def register_mousebuttonup(
        button: mouse.MouseButtonType,
        func: EventCallable,
    ) -> None:
        EventManager._register_handler(
            EventType.OnMousebuttonUp,
            MousebuttonHandler(func, button.buttonType),
        )

    @staticmethod
    def register_mousewheelscroll(func: EventCallable) -> None:
        EventManager._register_handler(EventType.OnMousewheelScroll, Handler(func))

    # ===== Register ===== end

    @staticmethod
    def update(events: list[_pygame.event.Event]) -> None:
        EventManager.eventQueue = events

    @staticmethod
    def _handlers_for_type(event_type: EventType) -> list[HandlerBase]:
        return [
            handler
            for registered_type, handler in tuple(EventManager._handlers)
            if registered_type == event_type
        ]

    @staticmethod
    def _matches_event(handler: HandlerBase, event: _pygame.event.Event) -> bool:
        if isinstance(handler, KeyHandler):
            return handler.key == getattr(event, "key", None)
        if isinstance(handler, MousebuttonHandler):
            return handler.mousebutton == getattr(event, "button", None)
        return True

    @staticmethod
    def _handlers_for_event(event: _pygame.event.Event) -> list[HandlerBase]:
        event_type = _PYGAME_EVENT_TYPES.get(event.type)
        if event_type is None:
            return []

        return [
            handler
            for handler in EventManager._handlers_for_type(event_type)
            if EventManager._matches_event(handler, event)
        ]

    @staticmethod
    def _invoke_handler(handler: HandlerBase, *args: _Any) -> None:
        event_func = _get_event_callable(handler)
        if event_func.owner is None:
            event_func.func(*args)
            return

        for instance in tuple(handler.instances):
            event_func.func(instance, *args)

    @staticmethod
    def dispatch() -> None:
        for handler in EventManager._handlers_for_type(EventType.OnUpdate):
            EventManager._invoke_handler(handler)

        for event in tuple(EventManager.eventQueue):
            if event.type == _pygame.QUIT:
                _pygame.quit()
                _sys.exit()

            for handler in EventManager._handlers_for_event(event):
                EventManager._invoke_handler(handler, event)

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