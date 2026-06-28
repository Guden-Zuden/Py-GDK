from . import Base
from . import Time
from . import Profile
from .Log import *

from dataclasses import dataclass
from typing import Self, Optional
import pytweening

__all__ = ["EasingLinear", "EasingInCubic", "Animator", "Animation", "AnimationData"]

@dataclass
class AnimationData:
    name: str
    data: list[int]
    fps: int = Profile.fps
    isLoop: bool = True
    current_index: int = 0
    @property
    def length(self): return len(self.data)
    def update(self, timer: Time.Timer):
        timer.update()

# class Animator:
#     def __init__(self) -> None:
#         self.animation_datas: dict[str, AnimationData] = {}
#         self.state_name: str = ""
#         self._timer = Timer.Timer()
#         self.endLoop_flag = False

#     def _get_animData(self, state_name: str) -> AnimationData:
#         try:
#             return self.animation_datas[state_name]
#         except KeyError as e:
#             Log.error("Animator", f"'{state_name}' doesn't exist!")
#             return self.animation_datas[state_name]

#     def set_state(self, state_name: str):
#         self._timer.reset()
#         self.state_name = state_name

#     def push(self, animation_data: AnimationData):
#         try:
#             self.animation_datas[animation_data.name]
#             Log.error("Animator", f"{animation_data.name} has already existed.")
#         except KeyError:
#             pass
        
#         self.animation_datas[animation_data.name] = animation_data

#     def update(self) -> None:
#         self._timer.update()
#         if self.state_name == "": return
#         anim_data = self._get_animData(self.state_name)
#         anim_data.current_index = int(anim_data.fps * self._timer.time) % anim_data.length
#         print(anim_data.current_index)
#         if anim_data.current_index == anim_data.length-1:
#             self.endLoop_flag = True
#             print(self.endLoop_flag)

#     def get_frame(self) -> int:
#         if self.state_name == "": return 0
#         anim_data = self._get_animData(self.state_name)
#         return anim_data.data[anim_data.current_index]

class EasingLinear(Base.EasingBase):
    def __init__(self, dx: float, dy: float, dt: float) -> None:
        super().__init__(dx, dy, dt)

    def update(self, timer) -> tuple[float, float]:
        buf = pytweening.linear(timer.time / self.dt)
        dx = self.dx * buf
        dy = self.dy * buf
        return (dx, dy)

class EasingInCubic(Base.EasingBase):
    def __init__(self, dx: float, dy: float, dt: float) -> None:
        super().__init__(dx, dy, dt)
    
    def update(self, timer) -> tuple[float, float]:
        buf = pytweening.easeInCubic(timer.time / self.dt)

        dx = self.dx * buf
        dy = self.dy * buf
        return (dx, dy)

class Anim_MoveTo(Base.AnimBase):
    def __init__(self, component: Base.LayerComponentBase, dx, dy, dt, easing: Optional[Base.EasingBase] = None) -> None:
        super().__init__()
        self.component = component

        self.start_x, self.start_y = self.component.x, self.component.y
        self.dx = dx
        self.dy = dy
        self.dt = dt
        if easing is None:
            self.easing = EasingLinear(dx, dy, dt)
        else:
            self.easing = easing

    def update(self):
        self.timer.update()

        x, y = self.easing.update(self.timer)

        self.component.x = self.start_x + x
        self.component.y = self.start_y + y
        if self.dt < self.timer.time:
            self.isOutOfDate = True
            self.component.x = self.start_x + self.dx
            self.component.y = self.start_y + self.dy

class Animation:
    def __init__(self, component: Base.LayerComponentBase) -> None:
        self.component = component
        self.current_anim: Optional[Base.AnimBase] = None
        self.anim_datas: list[Base.AnimBase] = []
        self.anim_index = 0

        self.anim_end = False

    def reset(self):
        self.anim_end = False
        self.anim_index = 0
        if self.current_anim is None: return

        self.current_anim.timer.reset()
        self.current_anim.isOutOfDate = False
        self.current_anim.start_x = self.component.x
        self.current_anim.start_y = self.component.y
        self.current_anim = None

    def update(self):
        if self.current_anim is None:
            if self.anim_datas == []:
                Log.error("Animation", "Animation data is empty.")
                return
            self.current_anim = self.anim_datas[self.anim_index]

        if self.current_anim.isOutOfDate:
            if self.anim_index >= len(self.anim_datas)-1:
                Log.debug("anim_end", self.anim_index)
                self.anim_index = 0
                self.anim_end = True
                self.current_anim.reset()
            else:
                self.anim_index += 1
            self.current_anim = self.anim_datas[self.anim_index]
            self.current_anim.reset()
            self.current_anim.start_x = self.component.x
            self.current_anim.start_y = self.component.y

        self.current_anim.update()

    # def fadeOut(self, time: float):
        # self.anim_datas.append(Anim_MoveTo(self.component, time))
    
    def moveTo(self, delta_x: float, delta_y: float, time: float, easing: Optional[Base.EasingBase] = None) -> Self:
        self.anim_datas.append(Anim_MoveTo(self.component, delta_x, delta_y, time, easing))
        if self.current_anim is None:
            self.current_anim = self.anim_datas[0]
        return self

class Animator(Base.LayerComponentBase):
    """
    Attach to layer
    """

    def __init__(self) -> None:
        # super().__init__()
        self.component: Optional[Base.LayerComponentBase]
        self.animations: list[tuple[str, Animation]] = []
        self.animation_index = 0
        self.playing_animation: Optional[Animation] = None
    
    def add_anim(self, anim_name: str, animation: Animation):
        self.animations.append((anim_name, animation))
        Log.debug("add_anim", anim_name)
    
    def play(self, anim_name: str):
        index = [name for name, anim in self.animations].index(anim_name)
        self.playing_animation = self.animations[index][1]
        self.playing_animation.reset()
        Log.debug("play", self.playing_animation)

    def update(self):
        if self.playing_animation is None:
            return
        if self.playing_animation.anim_end:
            self.playing_animation = None
            return
        self.playing_animation.update()