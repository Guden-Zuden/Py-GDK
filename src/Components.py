from . import Profile

from enum import Enum

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
    def __init__(self, u: float, v: float):
        self.x = Profile.width/2 + Profile.width/2 * u
        self.y = Profile.height/2 + Profile.height/2 * v
    def update(self):
        pass
    def draw(self):
        pass
    def _draw(self, x: float, y: float):
        pass