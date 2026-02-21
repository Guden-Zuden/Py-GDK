import pygame as _pygame
import sys as _sys
from enum import Enum

__all__ = ["gdk_color", "Anchor", "applyAnchor", "quit"]

type gdk_color = _pygame.Color | tuple[int, int, int, int] | tuple[int, int, int]

# ===== types ======
class Anchor(Enum):
    center      = 0
    right       = 1
    left        = 2
    top         = 3
    bottom      = 4
    righttop    = 5
    rightbottom = 6
    lefttop     = 7
    leftbottom  = 8
    default     = lefttop

# ===== Anchor =====
def applyAnchor(x: float, y: float, width: float, height: float, anchor: Anchor) -> tuple[float, float]:
    if   anchor == Anchor.center: return (x-width/2, y-height/2)
    elif anchor == Anchor.right: return (x-width, y-height/2)
    elif anchor == Anchor.left: return (x, y-height/2)
    elif anchor == Anchor.top: return (x-width/2, y)
    elif anchor == Anchor.bottom: return (x-width/2, y-height)
    elif anchor == Anchor.righttop: return (x-width, y)
    elif anchor == Anchor.rightbottom: return (x-width, y-height)
    elif anchor == Anchor.lefttop: return (x, y)
    elif anchor == Anchor.leftbottom: return (x, y-height)
    return (x, y)

def quit():
    _pygame.quit()
    _sys.exit()