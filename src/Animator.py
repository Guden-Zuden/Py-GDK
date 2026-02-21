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
    isLoop: bool = True
    current_index: int = 0
    @property
    def length(self): return len(self.data)
    def update(self, timer: Timer.Timer):
        timer.update()

class Animator:
    def __init__(self) -> None:
        self.animation_datas: dict[str, AnimationData] = {}
        self.state_name: str = ""
        self._timer = Timer.Timer()
        self.endLoop_flag = False

    def _get_animData(self, state_name: str) -> AnimationData:
        try:
            return self.animation_datas[state_name]
        except KeyError as e:
            Log.error("Animator", f"'{state_name}' doesn't exist!")
            return self.animation_datas[state_name]

    def set_state(self, state_name: str):
        self._timer.reset()
        self.state_name = state_name

    def push(self, animation_data: AnimationData):
        try:
            self.animation_datas[animation_data.name]
            Log.error("Animator", f"{animation_data.name} has already existed.")
        except KeyError:
            pass
        
        self.animation_datas[animation_data.name] = animation_data

    def update(self) -> None:
        self._timer.update()
        if self.state_name == "": return
        anim_data = self._get_animData(self.state_name)
        anim_data.current_index = int(anim_data.fps * self._timer.time) % anim_data.length
        print(anim_data.current_index)
        if anim_data.current_index == anim_data.length-1:
            self.endLoop_flag = True
            print(self.endLoop_flag)

    def get_frame(self) -> int:
        if self.state_name == "": return 0
        anim_data = self._get_animData(self.state_name)
        return anim_data.data[anim_data.current_index]
