from . import time as _time
from . import GUI as _GUI

from dataclasses import dataclass as _dataclass
from typing import (
    Optional as _Optional,
    Self as _Self
)
import pytweening as _pytweening

@_dataclass
class AnimFrame:
    index: int
    time: float
@_dataclass
class AnimEnd:
    time: float

class EAnimData:
    def __init__(self, frame_data: list[AnimFrame | AnimEnd]) -> None:
        self.frame_datas: list[AnimFrame | AnimEnd] = frame_data

        self._timer = _time.Timer()
        self.current_index = 0

    def update(self):
        self._timer.update()
        if self.current_index == len(self.frame_datas)-1:
            if self.frame_datas[self.current_index].time < self._timer.time:
                self._timer.reset()
                self.current_index = 0
            return
        if self.frame_datas[self.current_index+1].time < self._timer.time:
            self.current_index += 1

class EAnimator:
    """Entity Animator"""
    def __init__(self, anim_datas: dict[str, EAnimData]) -> None:
        self.current_anim: _Optional[EAnimData] = None
        self.anim_datas: dict[str, EAnimData] = anim_datas

    def play(self, animation_name: str):
        self.current_anim = self.anim_datas[animation_name]

    def update(self):
        if self.current_anim is None: return
        self.current_anim.update()

    def get_index(self):
        if self.current_anim is None:
            raise Exception("Any animation are not played.")
        return self.current_anim.current_index

class EasingBase:
    def __init__(self, dx: float, dy: float, dt: float) -> None:
        self.dx, self.dy = dx, dy
        self.dt = dt

    def update(self, timer: _time.Timer) -> tuple[float, float]: ...

class EasingLinear(EasingBase):
    def update(self, timer: _time.Timer) -> tuple[float, float]:
        buf = _pytweening.linear(timer.time / self.dt)
        dx = self.dx * buf
        dy = self.dy * buf
        return (dx, dy)

class EasingInCubic(EasingBase):
    def update(self, timer: _time.Timer) -> tuple[float, float]:
        buf = _pytweening.easeInCubic(timer.time / self.dt)
        dx = self.dx * buf
        dy = self.dy * buf
        return (dx, dy)

class GAnimBase:
    def __init__(self) -> None:
        self.start_x = 0.0
        self.start_y = 0.0
        self.dx = 0.0
        self.dy = 0.0
        self.is_ended = False
        self.timer = _time.Timer()

    def begin(self, gui_component: _GUI.base.GUIBase) -> None:
        self.timer.reset()
        self.start_x = gui_component.pos.x
        self.start_y = gui_component.pos.y
        self.is_ended = False

    def end(self) -> None:
        self.is_ended = True

    def reset(self) -> None:
        self.is_ended = False
        self.timer.reset()

    def update(self, gui_component: _GUI.base.GUIBase) -> None: ...

class GAnim_MoveTo(GAnimBase):
    def __init__(
            self,
            dx: float, dy: float, dt: float,
            easing: _Optional[EasingBase] = None) -> None:
        super().__init__()
        self.dx = dx
        self.dy = dy
        self.dt = dt
        if easing is None:
            self.easing = EasingLinear(dx, dy, dt)
        else:
            self.easing = easing

    def update(self, gui_component: _GUI.base.GUIBase):
        self.timer.update()

        x, y = self.easing.update(self.timer)

        gui_component.pos.x = self.start_x + x
        gui_component.pos.y = self.start_y + y
        if self.dt < self.timer.time:
            self.is_ended = True
            gui_component.pos.x = self.start_x + self.dx
            gui_component.pos.y = self.start_y + self.dy

class GAnimData:
    def __init__(self) -> None:
        self.current_anim: _Optional[GAnimBase] = None
        self.anim_datas: list[GAnimBase] = []
        self.anim_index = 0

        self.anim_end = False

    def begin(self, gui_component: _GUI.base.GUIBase):
        self.anim_end = False
        self.anim_index = 0
        if self.current_anim is None: return

        self.current_anim.begin(gui_component)
        self.current_anim = None

    def update(self, gui_component: _GUI.base.GUIBase):
        if self.current_anim is None:
            if self.anim_datas == []:
                raise Exception(f"[GAnimData]: Animation data is empty.")

            self.current_anim = self.anim_datas[self.anim_index]

        if self.current_anim.is_ended:
            if self.anim_index >= len(self.anim_datas) - 1:
                # print(f"anim_end: {self.anim_index}")
                self.anim_index = 0
                self.anim_end = True
                self.current_anim.reset()
            else:
                self.anim_index += 1
            self.current_anim = self.anim_datas[self.anim_index]
            self.current_anim.reset()
            self.current_anim.start_x = gui_component.pos.x
            self.current_anim.start_y = gui_component.pos.y

        self.current_anim.update(gui_component)

    def moveTo(
            self,
            delta_x: float,
            delta_y: float,
            time: float,
            easing: _Optional[EasingBase] = None) -> _Self:
        self.anim_datas.append(GAnim_MoveTo(delta_x, delta_y, time, easing))
        if self.current_anim is None:
            self.current_anim = self.anim_datas[0]
        return self

class GAnimator:
    def __init__(self, gui_component: _GUI.base.GUIBase) -> None:
        self.gui_component: _GUI.base.GUIBase = gui_component
        self.anim_datas: dict[str, GAnimData] = {}
        self.playing_anim_data: _Optional[GAnimData] = None

    def add_anim(self, anim_name: str, anim_data: GAnimData):
        self.anim_datas[anim_name] = anim_data
        # print(f"[GAnimator.add_anim]: added {anim_name}")

    def play(self, anim_name: str):
        """play animation"""
        self.playing_anim_data = self.anim_datas[anim_name]
        self.playing_anim_data.begin(self.gui_component)
        # print(f"[GAnimator.play]: play {anim_name}")

    def playf(self, anim_name: str):
        """play animation if any animation is not played"""
        if self.playing_anim_data: return
        self.playing_anim_data = self.anim_datas[anim_name]
        self.playing_anim_data.begin(self.gui_component)
        # print(f"[GAnimator.playf]: play {anim_name}")

    def update(self):
        if self.playing_anim_data is None: return

        if self.playing_anim_data.anim_end:
            self.playing_anim_data = None
            return

        self.playing_anim_data.update(self.gui_component)

__all__ = [
    "AnimFrame",
    "EAnimData",
    "EAnimator",

    "EasingLinear",
    "GAnim_MoveTo",
    "GAnimData",
    "GAnimator",
]