from .. import GUI as _GUI
from .. import profile as _profile
from ..base import *
from .. import colors as _colors
from .. import event as _event
from .. import time as _time
from .. import layer as _layer

class FpsCounter(_GUI.Label):
    def __init__(self, layer: _layer.Layer) -> None:
        super().__init__(1, -1, "FPS: NaN", TextAttributes("msgothic", 20, _colors.WHITE), Anchor.RIGHTTOP)
        layer.attach(self)

        self.timer = _time.Timer()
        self.frame_count = 0

    @_event.OnUpdate()
    def on_update(self):
        self.timer.update()
        self.frame_count += 1
        if self.timer.time > 1:
            self.text = f"FPS: {self.frame_count/self.timer.time :.1f}\ndt: {self.timer.time/self.frame_count*(10**3) :.3f}ms"
            self.frame_count = 0
            self.timer.reset()
