"""
GUI Components:
    AttachComponent:
        DraggableObj
        DockableObj
        
    LayerComponent:
        Box
        SpriteBox
        Button
        Text
        Panel
        
        VerticalAlignment
        VerticalSplitter

"""
from __future__ import annotations
import pygame as _pygame
from typing import Optional, Callable, Any
from functools import singledispatchmethod
from dataclasses import dataclass
from enum import Enum

from . import Profile
# from .Base import VerticalAlignment
from . import Animator
from .Log import *
from .Utils import *
from . import Time
from . import Sprite
from . import Constants
from . import Event
from . import Mouse
from . import Base

# TODO : More flexible Splitter.
# TODO : dealing with changing gui component classes
# TODO : fix the bugs: DraggableObj

# ===== Draggable object =====
class Draggable(Base.AttachComponentBase):
    _clicked_pos: Base.Pos = Base.Pos(0, 0)
    _dragging_pos: Base.Pos = Base.Pos(0, 0)
    _clicked_flag: bool = False
    _leaved_flag: bool = False
    _dragging_obj: Optional[Base.LayerComponentBase] = None
    _get_front_flag: bool = False

    def __init__(self) -> None:
        super().__init__()
        self._dragging_relpos: Base.Pos = Base.Pos(0, 0)
        self._dragging_flag: bool = False

    def update(self):
        assert self.component is not None
        mp = Mouse.get_pos()
        mx, my = mp.x - (Profile.window_width - Profile.width)/2, mp.y - (Profile.window_height - Profile.height)/2

        if Draggable._clicked_flag:
            isCollide = _pygame.Rect(self.component.x, self.component.y, self.component.width, self.component.height).collidepoint(mx, my)

            if isCollide:
                if Draggable._dragging_obj == None:
                    self._dragging_relpos = Draggable._clicked_pos - Base.Pos(self.component.x, self.component.y) - Base.Pos((Profile.window_width - Profile.width)/2, (Profile.window_height - Profile.height)/2)
                    self._dragging_flag = True
                    Draggable._dragging_obj = self.component

        if self._dragging_flag:
            self.component.x, self.component.y = (Base.Pos(mx, my) - self._dragging_relpos).pos

        if Draggable._leaved_flag:
            self._dragging_flag = False
            Draggable._dragging_obj = None

    @staticmethod
    def _reset_flag():
        Draggable._clicked_flag = False
        Draggable._leaved_flag = False

@Event.OnMousebuttonDown(Mouse.left)
def draggable_on_click(e):
    Draggable._clicked_flag = True
    Draggable._clicked_pos = Mouse.get_pos()
    Draggable._dragging_pos = Mouse.get_pos()

@Event.OnMousemove()
def draggable_on_mousemove(e):
    Draggable._dragging_pos = Mouse.get_pos()

@Event.OnMousebuttonUp(Mouse.left)
def draggable_on_mousebuttonup(e):
    Draggable._leaved_flag = True
    Draggable._get_front_flag = False

# Dockable Direction
class DockDirection(Enum):
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3
    FULL = 4
    NONE = 5

# ===== Dockable object =====
class Dockable(Draggable):
    """This Dockable class makes Vertical/Horizontal splitter on the panel automatically."""
    _mouseup_flag: bool = False

    def __init__(self) -> None:
        Draggable.__init__(self)

        self._docking_dir: DockDirection = DockDirection.NONE
        self._pre_docking_dir: DockDirection = DockDirection.NONE

    def update(self) -> None:
        assert self.component is not None
        super().update()
        
        if Dockable._dragging_pos.x < Profile.width * 0.2:
            self._pre_docking_dir = DockDirection.LEFT
        elif Dockable._dragging_pos.x > (Profile.width - Profile.width * 0.2):
            self._pre_docking_dir = DockDirection.RIGHT
        elif Dockable._dragging_pos.y < Profile.height * 0.2:
            self._pre_docking_dir = DockDirection.TOP
        elif Dockable._dragging_pos.y > (Profile.height - Profile.height * 0.2):
            self._pre_docking_dir = DockDirection.BOTTOM
        else:
            self._pre_docking_dir = DockDirection.NONE

        if Dockable._mouseup_flag:
            self._docking_dir = self._pre_docking_dir
            Dockable._mouseup_flag = False

        # if self._docking_dir 

@Event.OnMousebuttonUp(Mouse.left)
def on_mousebuttonup(e):
    Dockable._mouseup_flag = True

# ===== Box =====
class Box(Base.LayerComponentBase):
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
                 anchor: Anchor = Anchor.center) -> None:
        super().__init__(u, v, width, height)
        self.width, self.height = width, height
        self.color = color
        self.border_width = border_width
        """Thickness of border outline."""
        self.border_color = border_color
        self.padding = padding
        self.anchor = anchor

        x, y = applyAnchor(self.x, self.y, self.width, self.height, self.anchor)
        self.rect = _pygame.Rect(x, y, self.width, self.height)
        self.border_rect = _pygame.Rect(x - self.border_width, y - self.border_width, self.width + self.border_width*2, self.height + self.width*2)

        self.child: Optional[Base.LayerComponentBase] = None

    def set_child(self, child_obj: Base.LayerComponentBase):
        self.child = child_obj

    def update(self):
        super().update()
        self.rect = _pygame.Rect(self.x, self.y, self.width, self.height)
        self.border_rect = _pygame.Rect(self.x - self.border_width, self.y - self.border_width, self.width + self.border_width*2, self.height + self.border_width*2)

    def draw(self):
        assert Profile.surface is not None

        if self.border_width > 0:
            _pygame.draw.rect(Profile.surface, self.border_color, self.border_rect)

        _pygame.draw.rect(Profile.surface, self.color, self.rect)

        if self.child:
            self.child.x = self.x + self.width/2
            self.child.y = self.y + self.height/2

            self.child.draw()
    
# ===== SpriteBox =====
class SpriteBox(Base.LayerComponentBase):
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
                 sprite_index: int = 0):
        if width and height:
            self.sprite = sprite.transform(width, height)
            self.width, self.height = width, height
        else:
            self.sprite = sprite
            self.width, self.height = self.sprite.sprites[0].get_size()
        super().__init__(u, v, self.width, self.height)
        self.animator = animator
        self.padding = padding
        self.anchor = anchor
        self.sprite_index = sprite_index

    def draw(self):
        assert Profile.surface is not None

        # if self.animator:
            # self.sprite.draw(self.animator.get_frame(), self.x, self.y, Anchor.default)
        # else:
            # self.sprite.draw(self.sprite_index, self.x, self.y, Anchor.default)
        self.sprite.draw(self.sprite_index, self.x, self.y, Anchor.default)

# ===== Button =====
class Button(Base.LayerComponentBase):
    """Allow to attach: Layer"""
    g_NEUTRAL_COLOR: int =  0
    g_HOVERED_COLOR: int = 48
    g_CLICKED_COLOR: int = 64

    g_isHovered: bool = False
    g_isClicked: bool = False
    g_eventExecuted: bool = False

    def __init__(
            self,
            name: str,
            u: float,
            v: float,
            textAttr: TextAttribute,
            text: Any,
            width: float,
            height: float,
            background_color: gdk_color,
            clickFunc: Optional[Callable] = None,
            flags: int = 0,
            border_width: int = 0,
            border_color: gdk_color = (0, 0, 0)) -> None:
        super().__init__(u, v, width, height)
        self.name = name
        self.textAttr = textAttr
        self.text = text

        self.width = width
        self.height = height
        self.background_color = background_color
        self.clickFunc = clickFunc
        self.border_width = border_width
        self.border_color = border_color

        self.box_obj = Box(u, v, width, height, background_color, border_width, border_color)
        self.text_obj = Text(self.textAttr, text, u, v, True)
        
        self.box_obj.set_child(self.text_obj)

        self.isHovered = False
        self.isPressed = False

        self.flags = flags

        self.overlay = _pygame.Surface([self.width, self.height], _pygame.SRCALPHA)

    @staticmethod
    def reset():
        Button.g_isHovered = False

    def update(self):
        super().update()

        self.box_obj.x, self.box_obj.y = self.x, self.y
        self.text_obj.x, self.text_obj.y = self.x, self.y
        self.box_obj.update()
        self.text_obj.update()

        self.isHovered = False
        self.isPressed = False

        mp = Mouse.get_pos()

        hovered = self.box_obj.rect.collidepoint(mp.x - (Profile.window_width - Profile.width)/2, mp.y - (Profile.window_height - Profile.height)/2)

        if not Button.g_isHovered and hovered:
            self.isHovered = True
            Button.g_isHovered = True
        if self.isHovered and not hovered:
            self.isHovered = False
            Button.g_isHovered = False

        if Mouse.get_pressed().left and self.isHovered:
            self.isPressed = True

        if Button.g_eventExecuted and self.isPressed:
            if self.isHovered:
                if self.clickFunc: self.clickFunc()

            self.isPressed = False
            Button.g_eventExecuted = False

    def draw(self):
        assert Profile.surface is not None

        color = (0, 0, 0, 0)

        if self.isPressed:
            plus = self.g_CLICKED_COLOR
        elif self.isHovered:
            plus = self.g_HOVERED_COLOR
        else:
            plus = self.g_NEUTRAL_COLOR

        is_darken = False

        if (self.background_color[0] + self.background_color[1] + self.background_color[2])/3 >= 128:
            is_darken = True

        if is_darken:
            color = (0, 0, 0, plus)
        else:
            color = (255, 255, 255, plus)

        self.box_obj.draw()

        self.overlay.fill((0, 0, 0, 0))

        if (self.isHovered
            and not self.flags & Constants.DIS_HOVERFEED
            and not self.isPressed
            ) or (
            self.isPressed
            and not self.flags & Constants.DIS_CLICKFEED
            ):
                    self.overlay.fill(color)

        _pygame.Surface.blit(Profile.surface, self.overlay, self.box_obj.rect)
    
    def set_text(self, text: Any):
        self.text_obj.set_text(text)

@Event.OnMousebuttonUp(Event.Mouse.left)
def updateMousebuttonUp(e):
    Button.g_eventExecuted = True

@dataclass
class TextAttribute:
    font: str
    size: int
    text_color: gdk_color
    background_color: gdk_color | None = None
    antialias: bool = True
    bold: bool = False
    italic: bool = False

    def createFont(self) -> _pygame.font.Font:
        font = _pygame.font.SysFont(self.font, self.size, self.bold, self.italic)
        return font

# ===== Text =====
class Text(Base.LayerComponentBase):
    """Allow to attach: Scene, Layer"""
    def __init__(self,
                 textAttribute: TextAttribute,
                 text: Any,
                 u: float,
                 v: float,
                 is_centered: bool = False) -> None:
        self.textAttr = textAttribute
        self.font = self.textAttr.createFont()
        self.text: str = str(text)

        self._surf = self.font.render(self.text, self.textAttr.antialias, self.textAttr.text_color, self.textAttr.background_color)
        self.width, self.height = self._surf.get_size()
        super().__init__(u, v, self.width, self.height)
        
        self.is_centered = is_centered

    def draw(self):
        assert Profile.surface is not None
        surf = self.font.render(self.text, self.textAttr.antialias, self.textAttr.text_color, self.textAttr.background_color)

        if self.is_centered:
            Profile.surface.blit(surf, (self.x - self.width/2, self.y - self.height/2))
        else:
            Profile.surface.blit(surf, (self.x, self.y))
    
    def set_text(self, text: Any):
        self.text = str(text)
        self._surf = self.font.render(self.text, self.textAttr.antialias, self.textAttr.text_color, self.textAttr.background_color)
        self.width, self.height = self._surf.get_size()
        super().__init__(self.u, self.v, self.width, self.height)

# ===== Vertical alignment =====
class VerticalAlignment:
    def __init__(self, padding: float = Constants.dflt_padding, space: float = Constants.dflt_space) -> None:
        self.padding = padding
        self.space = space
        self._items: list[tuple[Base.LayerComponentBase, float]] = []

    @singledispatchmethod
    def pushItem(self, component: Any) -> None:
        Log.error("VerticalAlignment.pushItem",
                  f"Unexpected type!: {type(component)}\nVerticalAlignment object allows to be attached only text/button.")
        return

    @pushItem.register
    def _(self, text_obj: Text) -> None:
        self._items.append((text_obj, text_obj._surf.get_height()))

    @pushItem.register
    def _(self, button_obj: Button) -> None:
        self._items.append((button_obj, button_obj.height))

    def draw(self, clip_rect: _pygame.Rect, x: float, y: float) -> None:
        assert Profile.surface is not None
        Profile.surface.set_clip(clip_rect)
        current_x = x + self.padding
        current_y = y + self.padding
        for item, y in self._items:
            item.x, item.y = current_x, current_y
            item.update()
            item.draw()
            l_y = current_y
            current_y += y + self.space
            n_y = current_y

        Profile.surface.set_clip(None)

# ===== Panel =====
class Panel(Base.LayerComponentBase):
    """Allow to attach: Layer"""
    def __init__(self, 
                 u: float, v: float, 
                 width: float, height: float, 
                 background_color: gdk_color, 
                 padding: float = Constants.dflt_padding, 
                 space: float = Constants.dflt_space, 
                 components: list[Base.LayerComponentBase] = []) -> None:
        super().__init__(u, v, width, height)
        self.width, self.height = width, height
        self._box = Box(u, v, width, height, background_color, 1, (255, 255, 255))
        self.splitter: Optional[SplitterBase] = None

        self._itemAlignment = VerticalAlignment(padding, space)
        for comp in components:
            self._itemAlignment.pushItem(comp)
    
    def update(self):
        super().update()
        self._box.x, self._box.y = self.x, self.y
        self._box.width, self._box.height = self.width, self.height
        self._box.update()

    def draw(self):
        assert Profile.surface is not None

        self._box.draw()
        
        if self.splitter:
            self.splitter.draw()

        self._itemAlignment.draw(self._box.rect, self.x, self.y)

    def get_pos(self) -> tuple[float, float]:
        return self.x, self.y

# ===== Splitter =====
class SplitterBase:
    def __init__(self, parent_panel: Panel, first_panel: Panel, second_panel: Panel) -> None:
        self.parent_panel = parent_panel
        self.first_panel = first_panel
        self.second_panel = second_panel
    
    def draw(self) -> None: pass

class VerticalSplitter(SplitterBase):
    """This is not an object to attach. This object has not be stored in a variable. Conected to parent_panel, this object's draw function was called and two panel were drawn."""
    def __init__(self, parent_panel: Panel, left_panel: Panel, right_panel: Panel) -> None:
        super().__init__(parent_panel, left_panel, right_panel)
        self.parent_panel.splitter = self
        self._split_ratio: float = 0.5
        self._min_split_ratio: float = 0.05

        self.split_line_color: gdk_color = (255, 255, 255)

    def draw(self) -> None:
        assert Profile.surface is not None
        left_panel_pos = self.parent_panel.get_pos()

        left_panel_pos = (left_panel_pos[0], left_panel_pos[1])
        right_panel_pos = (left_panel_pos[0] + self.parent_panel.width * self._split_ratio, left_panel_pos[1])

        self.first_panel.x, self.first_panel.y = left_panel_pos
        self.first_panel.width = self.parent_panel.width * self._split_ratio

        self.second_panel.x, self.second_panel.y = right_panel_pos
        self.second_panel.width = self.parent_panel.width * (1 - self._split_ratio)

        self.first_panel.update()
        self.second_panel.update()

        self.first_panel.draw()
        self.second_panel.draw()

        _pygame.draw.line(Profile.surface, self.split_line_color, right_panel_pos, (right_panel_pos[0], right_panel_pos[1] + self.parent_panel.height))

class HorizontalSplitter(SplitterBase):
    """This is not an object to attach. This object has not be stored in a variable. Conected to parent_panel, this object's draw function was called and two panel were drawn."""
    def __init__(self, parent_panel: Panel, top_panel: Panel, bottom_panel: Panel) -> None:
        super().__init__(parent_panel, top_panel, bottom_panel)
        self.parent_panel.splitter = self
        self._split_ratio: float = 0.5
        self._min_split_ratio: float = 0.05

        self.split_line_color: gdk_color = (255, 255, 255)

    def draw(self) -> None:
        assert Profile.surface is not None
        top_panel_pos = self.parent_panel.get_pos()

        top_panel_pos = (top_panel_pos[0], top_panel_pos[1])
        bottom_panel_pos = (top_panel_pos[0], top_panel_pos[1] + self.parent_panel.height * self._split_ratio)

        self.first_panel.x, self.first_panel.y = top_panel_pos
        self.first_panel.height = self.parent_panel.height * self._split_ratio

        self.second_panel.x, self.second_panel.y = bottom_panel_pos
        self.second_panel.height = self.parent_panel.height * (1 - self._split_ratio)

        self.first_panel.update()
        self.second_panel.update()

        self.first_panel.draw()
        self.second_panel.draw()

        _pygame.draw.line(Profile.surface, self.split_line_color, bottom_panel_pos, (bottom_panel_pos[0] + self.parent_panel.width, bottom_panel_pos[1]))