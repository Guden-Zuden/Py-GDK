"""experimental"""

from . import base
from ..base import *
from .. import profile

from typing import (
    Optional as _Optional
)
from dataclasses import (
    dataclass as _dataclass
)
import copy as _copy

class DockingData:
    def __init__(
            self,
            gui_component: base.GUIBase,
            docking_direction: DockingDirection,
            pos: Vec2,
            current_width: int, current_height: int) -> None:
        self.gui_component = gui_component
        self.docking_direction = docking_direction
        self.gui_component.pos = pos
        
        self.current_width = current_width # current blank width
        self.current_height = current_height # current blank height

        if (self.docking_direction == DockingDirection.LEFT
            or self.docking_direction == DockingDirection.RIGHT):
            # self.gui_component.height = current_height
            self.gui_component.set_size(Vec2(self.gui_component.size.width, self.current_height))
        if (self.docking_direction == DockingDirection.TOP
            or self.docking_direction == DockingDirection.BOTTOM):
            # self.gui_component.width = current_width
            self.gui_component.set_size(Vec2(self.current_width, self.gui_component.size.height))
        
class DockingData_End:
    def __init__(
            self,
            gui_component: base.GUIBase,
            pos: Vec2,
            current_width: int, current_height: int) -> None:
        self.gui_component = gui_component
        self.gui_component.pos = pos
        # self.gui_component.width = current_width
        # self.gui_component.height = current_height
        self.gui_component.set_size(Vec2(current_width, current_height))

class DockingManager:
    """Experimental"""
    def __init__(self, width: int, height: int) -> None:
        self.docking_datas: list[DockingData | DockingData_End] = []
        self.current_width = width
        self.current_height = height
        self.current_pos = Vec2(0, 0)

    def dock(self, gui_component: base.GUIBase, docking_direction: DockingDirection):
        self.docking_datas.append(
            DockingData(
                gui_component, docking_direction,
                _copy.copy(self.current_pos),
                self.current_width, self.current_height
            )
        )
        if (docking_direction == DockingDirection.LEFT
            or docking_direction == DockingDirection.RIGHT):
            self.current_width -= gui_component.size.width
            self.current_pos.x += gui_component.size.width
        if (docking_direction == DockingDirection.TOP
            or docking_direction == DockingDirection.BOTTOM):
            self.current_height -= gui_component.size.height
            self.current_pos.y += gui_component.size.height

        # print(gui_component.pos.pos, gui_component.width, gui_component.height)

    def fill(self, gui_component: base.GUIBase):
        """finish docking."""
        self.docking_datas.append(
            DockingData_End(
                gui_component,
                _copy.copy(self.current_pos),
                self.current_width, self.current_height
            )
        )

    def get_guiObjects(self):
        guis: list[base.GUIBase] = []
        for docking_data in self.docking_datas:
            guis.append(docking_data.gui_component)
        return guis

    def update(self):
        buf = self.docking_datas
        self.current_width, self.current_height = profile.width, profile.height
        self.docking_datas = []
        self.current_pos = Vec2(0, 0)
        for docking_data in buf:
            if type(docking_data) == DockingData:
                self.dock(docking_data.gui_component, docking_data.docking_direction)
            elif type(docking_data) == DockingData_End:
                self.fill(docking_data.gui_component)