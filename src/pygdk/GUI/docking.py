"""Experimental GUI docking layout."""

from . import base
from ..base import DockingDirection, Vec2
from .. import profile


def _set_geometry(gui_component: base.Element, pos: Vec2, size: Vec2) -> None:
    if gui_component.size.tuple != size.tuple:
        gui_component.size = size
    if gui_component.pos.tuple != pos.tuple:
        gui_component.pos = pos


class DockingData:
    def __init__(
            self,
            gui_component: base.Element,
            docking_direction: DockingDirection,
            pos: Vec2,
            current_width: int,
            current_height: int) -> None:
        self.gui_component = gui_component
        self.docking_direction = docking_direction

        width = gui_component.size.width
        height = gui_component.size.height
        if docking_direction == DockingDirection.LEFT:
            size = Vec2(width, current_height)
            target_pos = pos.copy()
        elif docking_direction == DockingDirection.RIGHT:
            size = Vec2(width, current_height)
            target_pos = Vec2(pos.x + current_width - width, pos.y)
        elif docking_direction == DockingDirection.TOP:
            size = Vec2(current_width, height)
            target_pos = pos.copy()
        elif docking_direction == DockingDirection.BOTTOM:
            size = Vec2(current_width, height)
            target_pos = Vec2(pos.x, pos.y + current_height - height)
        else:
            raise ValueError(f"Unsupported docking direction: {docking_direction!r}")

        _set_geometry(gui_component, target_pos, size)


class DockingData_End:
    def __init__(
            self,
            gui_component: base.Element,
            pos: Vec2,
            current_width: int,
            current_height: int) -> None:
        self.gui_component = gui_component
        _set_geometry(
            gui_component,
            pos,
            Vec2(current_width, current_height)
        )


class DockingManager:
    """Experimental"""

    def __init__(self, width: int, height: int) -> None:
        self.docking_datas: list[DockingData | DockingData_End] = []
        self.current_width = width
        self.current_height = height
        self.current_pos = Vec2(0, 0)

    def dock(
            self,
            gui_component: base.Element,
            docking_direction: DockingDirection) -> None:
        if not isinstance(gui_component, base.Element):
            raise TypeError("gui_component must be a GUI Element")
        if not isinstance(docking_direction, DockingDirection):
            raise TypeError("docking_direction must be a DockingDirection")

        width = gui_component.size.width
        height = gui_component.size.height
        if docking_direction in (DockingDirection.LEFT, DockingDirection.RIGHT):
            if width > self.current_width:
                raise ValueError("Docked component is wider than the remaining area")
            data = DockingData(
                gui_component,
                docking_direction,
                self.current_pos.copy(),
                self.current_width,
                self.current_height
            )
            self.current_width -= width
            if docking_direction == DockingDirection.LEFT:
                self.current_pos.x += width
        else:
            if height > self.current_height:
                raise ValueError("Docked component is taller than the remaining area")
            data = DockingData(
                gui_component,
                docking_direction,
                self.current_pos.copy(),
                self.current_width,
                self.current_height
            )
            self.current_height -= height
            if docking_direction == DockingDirection.TOP:
                self.current_pos.y += height

        self.docking_datas.append(data)

    def fill(self, gui_component: base.Element) -> None:
        """Finish docking by filling the remaining area."""
        if not isinstance(gui_component, base.Element):
            raise TypeError("gui_component must be a GUI Element")
        self.docking_datas.append(
            DockingData_End(
                gui_component,
                self.current_pos.copy(),
                self.current_width,
                self.current_height
            )
        )

    def get_guiObjects(self) -> list[base.Element]:
        return [data.gui_component for data in self.docking_datas]

    def update(self) -> None:
        previous_data = self.docking_datas
        self.current_width = profile.width
        self.current_height = profile.height
        self.docking_datas = []
        self.current_pos = Vec2(0, 0)

        for docking_data in previous_data:
            if isinstance(docking_data, DockingData):
                self.dock(
                    docking_data.gui_component,
                    docking_data.docking_direction
                )
            elif isinstance(docking_data, DockingData_End):
                self.fill(docking_data.gui_component)
