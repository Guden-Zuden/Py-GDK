# import sys
# import pathlib
# sys.path.append(pathlib.Path().absolute().__str__())
from .. import profile
from .. import event, mouse

print(profile.clock)

class GUIBase:
    g_hovered = False
    g_clicked = False

    def __init__(self, u, v, width, height) -> None:
        self.u, self.v = u, v
        self.x = profile.width/2 + profile.width/2 * u - width/2
        self.y = profile.height/2 + profile.height/2 * v - height/2
        self.width, self.height = width, height

    def __init_subclass__(cls) -> None:
        event.EventManager.register_mousemove(GUIBase.on_hovered)
        event.EventManager.register_mousebuttondown(mouse.left, GUIBase.on_click)

    def on_hovered(self, e):
        print(e.pos)

    def on_click(self):
        pass