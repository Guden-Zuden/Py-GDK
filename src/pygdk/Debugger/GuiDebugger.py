from __future__ import annotations

from typing import Any as _Any

from .. import GUI as _GUI
from .. import event as _event
from .. import layer as _layer
from ..layer import LayerManager
from ._panel import DebuggerPanel, _TabSource


class GUIDebugger:
    def __init__(self, layer: _layer.Layer) -> None:
        self.current_layer = layer
        self._manual_components: list[_GUI.base.Element] = []

        self.GUI_Components_Container = DebuggerPanel([
            _TabSource(
                "GUI tree",
                self._component_rows,
                self._format_component,
                lambda row: (
                    row if isinstance(row, str) else (id(row[1]), row[0])
                ),
            ),
            _TabSource(
                "GUI callbacks",
                self._handler_rows,
                self._format_handler,
                lambda row: (
                    row[0],
                    id(row[1]),
                ) if not isinstance(row, str) else row,
            ),
            _TabSource(
                "Layers",
                self._layer_rows,
                self._format_layer,
                lambda row: row[0] if not isinstance(row, str) else row,
            ),
        ])
        self.TP_GUI_components, self.TP_GUI_handlers, self.TP_layers = (
            self.GUI_Components_Container.tab_properties
        )
        self.current_layer.attach(self.GUI_Components_Container)

    def _component_rows(self) -> list[tuple[int, _Any] | str]:
        rows: list[tuple[int, _Any] | str] = []
        visited: set[int] = set()
        debugger_panel = getattr(self, "GUI_Components_Container", None)

        def append_tree(component: _GUI.base.Element, depth: int) -> None:
            if component is debugger_panel or id(component) in visited:
                return
            visited.add(id(component))
            rows.append((depth, component))
            for child in component.children:
                append_tree(child, depth + 1)

        for component in self.current_layer._GUIComponent_stack:
            append_tree(component, 0)
        for component in self._manual_components:
            append_tree(component, 0)

        return rows or ["No GUI components"]

    @staticmethod
    def _format_component(row: _Any) -> str:
        if isinstance(row, str):
            return row
        depth, component = row
        indent = "  " * depth
        return (
            f"{indent}{type(component).__name__} "
            f"pos={component.pos.tuple} abs={component.abs_pos.tuple} "
            f"size={component.size.tuple} visible={component.visible} "
            f"dirty={component._dirty}"
        )

    @staticmethod
    def _handler_rows() -> list[_Any]:
        handlers = list(_event.EventManager._handlers)
        return handlers or ["No registered event handlers"]

    @staticmethod
    def _format_handler(row: _Any) -> str:
        if isinstance(row, str):
            return row

        event_type, handler = row
        event_func = getattr(handler, "func", None)
        name = getattr(event_func, "__qualname__", type(event_func).__name__)
        owner = getattr(event_func, "owner", None)
        if owner is not None:
            name = f"{owner.__name__}.{name}"

        trigger = ""
        if isinstance(handler, _event.KeyHandler):
            trigger = f" key={handler.key}"
        elif isinstance(handler, _event.MousebuttonHandler):
            trigger = f" button={handler.mousebutton}"

        return (
            f"{event_type.name}: {name}{trigger} "
            f"instances={len(handler.instances)}"
        )

    def _layer_rows(self) -> list[tuple[str, _layer.Layer] | str]:
        rows: list[tuple[str, _layer.Layer] | str] = list(
            LayerManager.layer_stack.items()
        )
        return rows or ["No layers registered"]

    def _format_layer(self, row: _Any) -> str:
        if isinstance(row, str):
            return row

        name, layer = row
        panel = getattr(self, "GUI_Components_Container", None)
        component_count = sum(
            component is not panel
            for component in layer._GUIComponent_stack
        )
        active = "*" if layer is LayerManager.current_layer else " "
        return f"{active} {name}: {component_count} GUI components"

    def update(self) -> None:
        self.GUI_Components_Container.refresh()

    def append_text(self, component: _GUI.base.Element) -> None:
        if not any(existing is component for existing in self._manual_components):
            self._manual_components.append(component)
        self.update()
