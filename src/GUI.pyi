import pygame as _pygame
from typing import Optional, Callable

from . import Profile
from . import Components
from . import Animator
from .Log import *
from .Utils import *
from . import Timer
from . import Sprite
from . import Constants
from . import TextAttribute
from . import Event

# TODO : More flexible Splitter.

# ===== Draggable object =====
class DraggableObj:
    def __init__(self, component: Components.LayerComponentBase | Components.SceneComponentBase) -> None: ...

    # def update(self): ...

# ===== Box =====
class Box(Components.LayerComponentBase):
    """Allow to attach: Layer"""
    def __init__(self,
                 u: float,
                 v: float,
                 width: float,
                 height: float,
                 color: gdk_color,
                 border_width: int = 0,
                 border_color: gdk_color = (0, 0, 0),
                 padding: int = 0,
                 anchor: Anchor = Anchor.center) -> None: ...

    def draw(self): ...
    
    def _draw(self, x: float, y: float): ...

# ===== SpriteBox =====
class SpriteBox(Components.LayerComponentBase):
    """Allow to attach: Layer"""
    def __init__(self,
                 u: float,
                 v: float,
                 sprite: Sprite.Sprite,
                 width: Optional[float] = None,
                 height: Optional[float] = None,
                 animator: Optional[Animator] = None,
                 padding: int = 0,
                 anchor: Anchor = Anchor.center,
                 sprite_index: int = 0): ...

    def draw(self): ...

# ===== Button =====
class Button(Components.LayerComponentBase):
    """Allow to attach: Layer"""

    def __init__(
            self,
            name: str,
            u: float,
            v: float,
            textAttr: TextAttribute,
            text: str,
            width: float,
            height: float,
            background_color: gdk_color,
            clickFunc: Callable,
            flags: int = 0,
            border_width: int = 0,
            border_color: gdk_color = (0, 0, 0)) -> None: ...

    @staticmethod
    def reset(): ...

    def update(self): ...

    def draw(self): ...

    def _draw(self, x: float, y: float): ...

# ===== Text =====
class Text(Components.LayerComponentBase):
    """Allow to attach: Scene, Layer"""
    def __init__(self,
                 textAttribute: TextAttribute,
                 text: str,
                 u: float,
                 v: float) -> None: ...

    def draw(self): ...

    def _draw(self, x: float, y: float): ...
        
# ===== Panel =====
class Panel(Components.LayerComponentBase):
    """Allow to attach: Layer"""
    def __init__(self, 
                 u: float, 
                 v: float, 
                 width: float, 
                 height: float, 
                 background_color: gdk_color, 
                 padding: float = Constants.dflt_padding, 
                 space: float = Constants.dflt_space, 
                 components: list[Components.LayerComponentBase] = []) -> None: ...
    
    def draw(self): ...
        
    def _draw(self, x: float, y: float): ...

    def get_pos(self) -> tuple[float, float]: ...

# ===== Splitter =====
class SplitterBase:
    def __init__(self, parent_panel: Panel, first_panel: Panel, second_panel: Panel) -> None: ...

class VerticalSplitter(SplitterBase):
    """This is not an object to attach. This object has not be stored in a variable. Conected to parent_panel, this object's draw function was called and two panel were drawn."""
    def __init__(self, parent_panel: Panel, left_panel: Panel, right_panel: Panel) -> None: ...

    def draw(self) -> None: ...