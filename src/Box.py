import pygame as _pygame
from typing import Optional

from . import Profile
from . import Utils
from . import Components
from . import Sprite
from . import Animator

class Box(Components.LayerComponentBase):
    def __init__(self,
                 u: float,
                 v: float,
                 width: float,
                 height: float,
                 color: _pygame.Color | tuple[int, int, int, int] | tuple[int, int, int],
                 border_width: int = 0,
                 border_color: _pygame.Color | tuple[int, int, int, int] | tuple[int, int, int] = (0, 0, 0),
                 padding: int = 0,
                 anchor: Utils.Anchor = Utils.Anchor.center) -> None:
        super().__init__(u, v)
        self.width, self.height = width, height
        self.color = color
        self.border_width = border_width
        """Thickness of border outline."""
        self.border_color = border_color
        self.padding = padding
        self.anchor = anchor

        x, y = Utils.applyAnchor(self.x, self.y, self.width, self.height, self.anchor)
        self.rect = _pygame.Rect(x, y, self.width, self.height)

    def draw(self):
        assert Profile.surface is not None

        x, y = Utils.applyAnchor(self.x, self.y, self.width, self.height, self.anchor)
        self.rect = _pygame.Rect(x, y, self.width, self.height)

        border_width = self.width + 2*self.border_width + 2*self.padding
        border_height = self.height + 2*self.border_width + 2*self.padding
        x, y = Utils.applyAnchor(self. x, self.y, border_width, border_height, self.anchor)
        border_rect = _pygame.Rect(self.x - self.border_width - self.padding,
                                   self.y - self.border_width - self.padding,
                                   border_width, border_height)
        _pygame.draw.rect(Profile.surface, self.color, self.rect)
        if self.border_width != 0:
            _pygame.draw.rect(Profile.surface, self.border_color, border_rect, self.border_width)

class BoxSprite(Components.LayerComponentBase):
    def __init__(self,
                 u: float,
                 v: float,
                 width: float,
                 height: float,
                 sprite: Sprite.Sprite,
                 animator: Optional[Animator] = None,
                 padding: int = 0,
                 anchor: Utils.Anchor = Utils.Anchor.center,
                 sprite_index: int = 0):
        super().__init__(u, v)
        self.width, self.height = width, height
        self.sprite = sprite
        self.animator = animator
        self.padding = padding
        self.anchor = anchor
        self.sprite_index = sprite_index

    def draw(self):
        assert Profile.surface is not None
        x, y = Utils.applyAnchor(self.x, self.y, self.width, self.height, self.anchor)
        rect = _pygame.Rect(x, y, self.width, self.height)

        if self.animator:
            self.sprite.draw(self.animator.get_frame(), x, y, anchor=Utils.Anchor.center)
        else:
            self.sprite.draw(self.sprite_index, x, y, anchor=Utils.Anchor.bottom)