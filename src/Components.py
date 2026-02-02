from enum import Enum

class ComponentType(Enum):
    entity = 0


class ComponentBase:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    def draw(self, offset_x: float, offset_y: float):
        pass
