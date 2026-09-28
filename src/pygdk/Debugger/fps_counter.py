from .. import GUI
from .. import profile as _profile
from ..base import *
from .. import colors
from .. import event
from .. import time
from .. import layer

class FpsCounter(GUI.Label):
    def __init__(self, layer: layer.Layer) -> None:
        super().__init__(1, -1, "FPS: NaN", TextAttributes("msgothic", 20, colors.WHITE), Anchor.RIGHTTOP)
        layer.attach(self)

        self.timer = time.Timer()
        self.frame_count = 0

    @event.OnUpdate()
    def on_update(self):
        self.timer.update()
        self.frame_count += 1
        if self.timer.time > 1:
            self.text = f"FPS: {self.frame_count/self.timer.time :.1f}\ndt: {self.timer.time/self.frame_count*(10**3) :.3f}ms"
            self.frame_count = 0
            self.timer.reset()
