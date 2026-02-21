from . import Profile

from enum import Enum
from typing import Optional

class ComponentType(Enum):
    entity = 0

class ComponentBase:
    pass

class SceneComponentBase(ComponentBase):
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    def update(self):
        pass
    def draw(self, offset_x: float, offset_y: float):
        pass

class LayerComponentBase(ComponentBase):
    def __init__(self, u: float, v: float, width: float, height: float):
        self.x = Profile.width/2 + Profile.width/2 * u - width/2
        self.y = Profile.height/2 + Profile.height/2 * v - height/2
        self.parent: Optional[LayerComponentBase] = None

    def update(self):
        pass
    
    def draw(self):
        """drawing centered position"""
        pass

    def _draw(self, x: float, y: float):
        """drawing non-centerd position"""
        pass