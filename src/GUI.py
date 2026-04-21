"""
GUI Components:
    AttachComponent:
        DraggableObj
    LayerComponent:
        Box
        SpriteBox
        Button
        Text
        Panel
        
        VerticalAlignment
        VerticalSplitter

"""

import pygame as _pygame
from typing import Optional, Callable, Any
from functools import singledispatchmethod

from . import Profile
# from .Base import VerticalAlignment
from . import Animator
from .Log import *
from .Utils import *
from . import Timer
from . import Sprite
from . import Constants
from . import TextAttribute
from . import Event
from . import Mouse
from . import Base

# TODO : More flexible Splitter.
# TODO : dealing with changing gui component classes

# ===== Draggable object =====
class DraggableObj(Base.AttachComponentBase):
    _dragging_pos: Base.Pos = Base.Pos(0, 0)
    _clicked_flag: bool = False
    _leaved_flag: bool = False
    def __init__(self) -> None:
        super().__init__()
        self._dragging_relpos: Base.Pos = Base.Pos(0, 0)
        self._dragging_flag: bool = False

    def update(self):
        assert self.component is not None
        mp = Mouse.get_pos()
        mx, my = mp.x - (Profile.window_width - Profile.width)/2, mp.y - (Profile.window_height - Profile.height)/2
        if DraggableObj._clicked_flag:
            if _pygame.Rect(self.component.x, self.component.y, self.component.width, self.component.height).collidepoint(mx, my):
                self._dragging_relpos = DraggableObj._dragging_pos - Base.Pos(self.component.x, self.component.y) - Base.Pos((Profile.window_width - Profile.width)/2, (Profile.window_height - Profile.height)/2)
                self._dragging_flag = True

            DraggableObj._clicked_flag = False
        if self._dragging_flag:
            self.component.x, self.component.y = (Base.Pos(mx, my) - self._dragging_relpos).pos

        if DraggableObj._leaved_flag:
            self._dragging_flag = False
            DraggableObj._leaved_flag = False
            pass

@Event.OnMousebuttonDown(Mouse.left)
def on_click(e):
    DraggableObj._clicked_flag = True
    DraggableObj._dragging_pos = Mouse.get_pos()

@Event.OnMousebuttonUp(Mouse.left)
def on_mousebuttonup(e):
    DraggableObj._leaved_flag = True

# ===== Dockable object =====
# class DockableObj(Base.LayerComponentBase, DraggableObj):
    # def __init__(self, component: Base.LayerComponentBase) -> None:
        # Base.LayerComponentBase.__init__(self, component.u, component.v, component.width, component.height)
        # DraggableObj.__init__(self, component)
        # self.component = component

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
        self._surf = _pygame.Surface([width, height], flags=_pygame.SRCALPHA)
        self._border_surf = _pygame.Surface([width + self.border_width*2, height + self.border_width*2], flags=_pygame.SRCALPHA)

    def draw(self):
        assert Profile.surface is not None

        self.rect = _pygame.Rect(self.x, self.y, self.width, self.height)
        _pygame.draw.rect(self._surf, self.color, self._surf.get_rect())
        if self.border_width > 0:
            _pygame.draw.rect(self._border_surf, self.border_color, self._border_surf.get_rect())

        Profile.surface.blit(self._border_surf, [self.x - self.border_width, self.y - self.border_width])
        Profile.surface.blit(self._surf, [self.x, self.y])
    
    """
    def _draw(self, x: float, y: float):
        assert Profile.surface is not None

        self.rect = _pygame.Rect(x, y, self.width, self.height)
        _pygame.draw.rect(self._surf, self.color, self._surf.get_rect())
        # if self.border_width > 0:
            # _pygame.draw.rect(self._border_surf, self.border_color, self._border_surf.get_rect(), 1)

        # _pygame.draw.rect(self.)

        Profile.surface.blit(self._border_surf, [x - self.border_width, y - self.border_width])
        Profile.surface.blit(self._surf, [x, y])


        # self.rect = _pygame.Rect(x, y, self.width, self.height)
        # border_width = self.width + 2*self.border_width + 2*self.padding
        # border_height = self.height + 2*self.border_width + 2*self.padding
        # x, y, = applyAnchor(x, y, border_width, border_height, Anchor.default)
        # _pygame.draw.rect(self._surf, self.color, self._surf.get_rect())
        # if self.border_width > 0:
        #     _pygame.draw.rect(self._surf, self.border_color, self._surf.get_rect(), self.border_width)

        # Profile.surface.blit(self._surf, [x, y])
    """
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
        # x, y = applyAnchor(self.x, self.y, self.width, self.height, self.anchor)

        if self.animator:
            self.sprite.draw(self.animator.get_frame(), self.x, self.y, Anchor.default)
        else:
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
            text: str,
            width: float,
            height: float,
            background_color: gdk_color,
            clickFunc: Callable,
            flags: int = 0,
            border_width: int = 0,
            border_color: gdk_color = (0, 0, 0)) -> None:
        super().__init__(u, v, width, height)
        self.name = name
        self.textAttr = textAttr
        self.text = text
        self._text_obj = Text(self.textAttr, self.text, u, v)

        self.width = width
        self.height = height
        self.background_color = background_color
        self.clickFunc = clickFunc
        self.border_width = border_width
        self.border_color = border_color

        self.box_obj = Box(u, v, width, height, background_color, border_width, border_color)

        self.isHovered = False
        self.isPressed = False

        self.flags = flags

        self.overlay = _pygame.Surface([self.width, self.height], _pygame.SRCALPHA)

    @staticmethod
    def reset():
        Button.g_isHovered = False

    def update(self):
        super().update()

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
            
            # self.isHovered = hovered

            if self.isHovered:
                self.clickFunc()
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

        self._text_obj.draw()#self.x, self.y)
        # self._text_obj._draw(self.x, self.y)
"""
    def _draw(self, x: float, y: float):
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

        # self.box_obj.draw()
        self.box_obj._draw(x, y)

        self.overlay.fill((0, 0, 0, 0))

        if (self.isHovered
            and not self.flags & Constants.DIS_HOVERFEED
            and not self.isPressed
            ) or (
            self.isPressed
            and not self.flags & Constants.DIS_CLICKFEED
            ):
                    self.overlay.fill(color)

        _pygame.Surface.blit(Profile.surface, self.overlay, _pygame.Rect(x, y, self.width, self.height))

        # self._text_obj.draw()#self.x, self.y)
        self._text_obj._draw(x + (self._text_obj.x - self.x), y + (self._text_obj.y - self.y))

        # _pygame.draw.line(Profile.surface, (255, 128, 255), [x, y], [x, y+self.height], 4)
"""
# @Event.OnMousemove()
# def updateMousePos(e):
    # Button.g_mouseX, Button.g_mouseY = e.pos[0], e.pos[1]

@Event.OnMousebuttonUp(Event.Mouse.left)
def updateMousebuttonUp(e):
    Button.g_eventExecuted = True

# ===== Text =====
class Text(Base.LayerComponentBase):
    """Allow to attach: Scene, Layer"""
    def __init__(self,
                 textAttribute: TextAttribute,
                 text: str,
                 u: float,
                 v: float) -> None:
        self.textAttr = textAttribute
        self.font = self.textAttr.createFont()
        self.text = text
        # self.anchor: Anchor = anchor

        self._surf = self.font.render(self.text, self.textAttr.antialias, self.textAttr.text_color, self.textAttr.background_color)
        self.width, self.height = self._surf.get_size()
        super().__init__(u, v, self.width, self.height)

    def draw(self):
        assert Profile.surface is not None
        surf = self.font.render(self.text, self.textAttr.antialias, self.textAttr.text_color, self.textAttr.background_color)
        Profile.surface.blit(surf, (self.x, self.y))#applyAnchor(self.x, self.y, surf.get_width(), surf.get_height(), self.anchor))
"""
    def _draw(self, x: float, y: float):
        assert Profile.surface is not None
        Profile.surface.blit(self._surf, (x, y))#applyAnchor(x, y, self._surf.get_width(), self._surf.get_height(), Anchor.default))
        # _pygame.draw.line(Profile.surface, (255, 128, 255), [x, y], [x, y+self.height], 4)
        """
# ===== Vertical alignment =====
class VerticalAlignment:
    def __init__(self, padding: float = Constants.dflt_padding, space: float = Constants.dflt_space) -> None:
        self.padding = padding
        self.space = space
        self._items: list[tuple[Base.LayerComponentBase, float]] = []

    @singledispatchmethod
    def pushItem(self, component: Any) -> None:
        Log.error("VerticalAlignment.pushItem", "Unexpected type!")

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
        for item in self._items:
            item[0].x, item[0].y = current_x, current_y
            # item[0]._draw(current_x, current_y)
            item[0].draw()
            l_y = current_y
            current_y += item[1] + self.space
            n_y = current_y
            # _pygame.draw.line(Profile.surface, (255, 255, 128), [current_x, l_y+item[1]], [current_x, n_y], 4)
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
        self.panel_rect = _pygame.Rect(self.x, self.y, self.width, self.height)
        self.children: list[VerticalSplitter] = []

        self._itemAlignment = VerticalAlignment(padding, space)
        for comp in components:
            self._itemAlignment.pushItem(comp)
    
    def update(self):
        super().update()
        self._box.x, self._box.y = self.x, self.y
        # self._itemAlignment.

    def draw(self):
        assert Profile.surface is not None

        self._box.draw()
        # self._box._draw(self.x, self.y)
        _pygame.draw.circle(Profile.surface, (255,255,0), (self.x, self.y), 10)
        # _pygame.draw.rect(Profile.surface, (128, 255, 128), self.panel_rect)
        for child in self.children:
            child.draw()
        self._itemAlignment.draw(self.panel_rect, self.x, self.y)
        """
    def _draw(self, x: float, y: float):
        self._box._draw(x, y)
        self._itemAlignment.draw(_pygame.Rect(x, y, self.width, self.height), x, y)
"""""
    def get_pos(self) -> tuple[float, float]:
        return self.x, self.y

# ===== Splitter =====
class SplitterBase:
    def __init__(self, parent_panel: Panel, first_panel: Panel, second_panel: Panel) -> None:
        self.parent_panel = parent_panel
        self.first_panel = first_panel
        self.second_panel = second_panel

class VerticalSplitter(SplitterBase):
    """This is not an object to attach. This object has not be stored in a variable. Conected to parent_panel, this object's draw function was called and two panel were drawn."""
    def __init__(self, parent_panel: Panel, left_panel: Panel, right_panel: Panel) -> None:
        super().__init__(parent_panel, left_panel, right_panel)
        self.parent_panel.children.append(self)
        self._split_ratio: float = 0.5
        self._min_split_ratio: float = 0.05

        self.split_line_color: gdk_color = (255, 255, 255)

    def draw(self) -> None:
        assert Profile.surface is not None
        left_panel_pos = self.parent_panel.get_pos()

        left_panel_pos = (left_panel_pos[0], left_panel_pos[1])
        right_panel_pos = (left_panel_pos[0] + self.parent_panel.width * self._split_ratio, left_panel_pos[1])

        self.first_panel._draw(*left_panel_pos)
        self.second_panel._draw(*right_panel_pos)
        _pygame.draw.line(Profile.surface, self.split_line_color, right_panel_pos, (right_panel_pos[0], right_panel_pos[1] + self.parent_panel.height))