from .base import *
from . import key, mouse
from . import profile

import pygame as _pygame
import sys as _sys

# TODO: Not complete yet, temporary.

# ===== Permissions =====
class InputPermission(Flag):
    WASD = auto()
    Arrows = auto()

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
    x, y = _pygame.mouse.get_pos()
    mouse._pos = Vec2(x, y)

# ===== KeyData included some funcs =====
@dataclass
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

def OnKeydown(key: key.KeyType):
    def decorator(func):
        EventManager.register_keydown(key, func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorator

def OnKeyup(key: key.KeyType):
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

def OnMousebuttonDown(button: mouse.MouseButtonType):
    def decorator(func):
        EventManager.register_mousebuttondown(button, func)
    
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def OnMousebuttonUp(button: mouse.MouseButtonType):
    def decorator(func):
        EventManager.register_mousebuttonup(button, func)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

class EventType(Flag):
    OnUpdate = auto()
    OnWindowResized = auto()
    OnKeydown = auto()
    OnKeyup = auto()
    OnMousebuttonDown = auto()
    OnMousebuttonUp = auto()
    OnMousemove = auto()


@dataclass
class HandlerBase:
    func: Callable[..., None]
    instances: list[Any] = field(default_factory=list, init=False)

@dataclass
class Handler(HandlerBase):
    pass

@dataclass
class KeyHandler(HandlerBase):
    key: int

@dataclass
class MousebuttonHandler(HandlerBase):
    mousebutton: int


class EventObject:
    def __new__(cls: type[Self], *args, **kwargs) -> Self:
        instance = super().__new__(cls)
        EventManager.link_instance(instance)
        return instance

class EventManager:
    _handlers: list[tuple[EventType, Handler | KeyHandler | MousebuttonHandler]] = []

    @staticmethod
    def _handler_key(event_type: EventType, handler: Handler | KeyHandler | MousebuttonHandler):
        if isinstance(handler, KeyHandler):
            return (event_type, handler.func, handler.key)
        if isinstance(handler, MousebuttonHandler):
            return (event_type, handler.func, handler.mousebutton)
        return (event_type, handler.func, None)

    @staticmethod
    def _register_handler(event_type: EventType, handler: Handler | KeyHandler | MousebuttonHandler):
        if any(EventManager._handler_key(event_type, existing_handler) == EventManager._handler_key(event_type, handler)
               for existing_event_type, existing_handler in EventManager._handlers
               if existing_event_type == event_type):
            return
        EventManager._handlers.append((event_type, handler))

    @staticmethod
    def link_instance(instance: Any):
        '''
        Called by EventObject
        '''
        for _event_type, _handler in EventManager._handlers:
            owner_name = _handler.func.__qualname__.rsplit(".", 1)[0]

            if any(mro.__qualname__ == owner_name for mro in instance.__class__.__mro__):
                if not any(existing_instance is instance for existing_instance in _handler.instances):
                    _handler.instances.append(instance)

    # ===== Register =====
    @staticmethod
    def register_update(func: Callable[..., None]):
        EventManager._register_handler(EventType.OnUpdate, Handler(func))

    @staticmethod
    def register_windowresized(func: Callable[..., None]):
        EventManager._register_handler(EventType.OnWindowResized, Handler(func))

    @staticmethod
    def register_keydown(key: key.KeyType, func: Callable[..., None]):
        EventManager._register_handler(EventType.OnKeydown, KeyHandler(func, key.keyCode))

    @staticmethod
    def register_keyup(key: key.KeyType, func: Callable[..., None]):
        EventManager._register_handler(EventType.OnKeyup, KeyHandler(func, key.keyCode))

    @staticmethod
    def register_mousemove(func: Callable[..., None]):
        EventManager._register_handler(EventType.OnMousemove, Handler(func))

    @staticmethod
    def register_mousebuttondown(button: mouse.MouseButtonType, func: Callable[..., None]):
        EventManager._register_handler(EventType.OnMousebuttonDown, MousebuttonHandler(func, button.buttonType))

    @staticmethod
    def register_mousebuttonup(button: mouse.MouseButtonType, func: Callable[..., None]):
        EventManager._register_handler(EventType.OnMousebuttonUp, MousebuttonHandler(func, button.buttonType))

    # ===== Register ===== end

    @staticmethod
    def update(events: list[_pygame.event.Event]):
        EventManager.eventQueue = events

    @staticmethod
    def dispatch():
        # OnUpdate
        for handler in [handler for event_type, handler in EventManager._handlers
                        if event_type == EventType.OnUpdate]:
            if handler.instances != []:
                for instance in handler.instances:
                    handler.func(instance)
            elif not '.' in handler.func.__qualname__:
                handler.func()

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

            for handler in handlers:
                if handler.instances != []:
                    for instance in handler.instances:
                        handler.func(instance, e)
                elif not '.' in handler.func.__qualname__:
                    handler.func(e)

# ===== User Function ======
def getKey(key_data: key.KeyType) -> KeyEventData:
    keyStatus = KeyEventData(key_data, pressedKeys[key_data.keyCode], pressedKeymods)
    return keyStatus

def getMousePos() -> Vec2:
    return mouse._pos

def getMousePressed() -> mouse.MouseButtonData:
    return mouse.get_pressed()

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