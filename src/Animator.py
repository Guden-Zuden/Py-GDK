from . import Timer
from . import Profile
from .Log import *

from dataclasses import dataclass

__all__ = ["Animator", "AnimationData"]

@dataclass
class AnimationData:
    name: str
    data: list[int]
    fps: int = Profile.fps
    current_index: int = 0
    
    def get_length(self): return len(self.data)
    def update(self, timer: Timer.Timer):
        timer.update()

class Animator:
    def __init__(self) -> None:
        self.animation_datas: dict[str, AnimationData] = {}
        self.state_name: str = ""
        self._timer = Timer.Timer()

    def _get_animData(self, state_name: str) -> AnimationData:
        try:
            return self.animation_datas[state_name]
        except KeyError as e:
            Log.error("Animator", f"'{state_name}' doesn't exist!")
            return self.animation_datas[state_name]

    def set_state(self, state_name: str):
        self.state_name = state_name

    def push(self, state_name: str, animation_data: AnimationData):
        try:
            self.animation_datas[state_name]
            Log.error("Animator", f"{state_name} has already existed.")
        except KeyError:
            pass
        
        self.animation_datas[state_name] = animation_data

    def update(self) -> None:
        self._timer.update()
        if self.state_name == "": return
        anim_data = self._get_animData(self.state_name)
        anim_data.current_index = int(anim_data.fps * self._timer.time) % anim_data.get_length()

    def get_frame(self) -> int:
        if self.state_name == "": return 0
        anim_data = self._get_animData(self.state_name)
        return anim_data.data[anim_data.current_index]
