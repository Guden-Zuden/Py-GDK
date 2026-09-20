from . import time as _time

from dataclasses import dataclass as _dataclass
from typing import (
    Optional as _Optional,
)

@_dataclass
class AnimFrame:
    index: int
    time: float
@_dataclass
class AnimEnd:
    time: float

class EntityAnimData:
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
    def __init__(self, anim_datas: dict[str, EntityAnimData]) -> None:
        self.current_anim: _Optional[EntityAnimData] = None
        self.anim_datas: dict[str, EntityAnimData] = anim_datas

    def play(self, animation_name: str):
        self.current_anim = self.anim_datas[animation_name]

    def update(self):
        if self.current_anim is None: return
        self.current_anim.update()

    def get_index(self):
        if self.current_anim is None:
            raise Exception("Any animation are not played.")
        return self.current_anim.current_index

__all__ = [
    "AnimFrame",
    "EntityAnimData",
    "EAnimator"
]