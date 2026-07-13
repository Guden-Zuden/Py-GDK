# import sys
# import pathlib
# sys.path.append(pathlib.Path().absolute().__str__())
from typing import Self

from .. import profile
from .. import event, mouse

print(profile.clock)

class GUIBase(event.EventObject):
    g_hovered = False
    g_clicked = False

    def __init__(self, u: float, v: float, width: float, height: float) -> None:
        self.u, self.v = u, v
        self.x = profile.width/2 + profile.width/2 * u - width/2
        self.y = profile.height/2 + profile.height/2 * v - height/2
        self.width, self.height = width, height

    def update(self): pass
    def draw(self): pass

    # commons
    def __init_subclass__(cls: type[Self]) -> None:
        event.EventManager.register_mousemove(cls.on_hovered)
        event.EventManager.register_mousebuttondown(mouse.left, cls.on_click)

    def on_hovered(self, e):
        print(e.pos) # TODO: update()でhovered変数を変える

    def on_click(self, e):
        pass