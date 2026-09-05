from .base import *
from . import profile
from . import GUI as _GUI
from . import event as _event
from .time import BenchMark as _BenchMark

from typing import (
    Any as _Any,
    Optional as _Optional
)

class AttachPermissionError(Exception):
    def __init__(self, component: _Any, attach_to: _Any):
        self.component = component
        self.attach_to = attach_to

    def __str__(self):
        return (
            f"{self.component} is not allowed to attach to {self.attach_to}."
        )

class Layer:
    PERMISSIONS: list[_Any] = [
        _GUI.Label,
        _GUI.Box,
        _GUI.Button,
        _GUI.ImageButton,
        _GUI.Image,
        _GUI.VerticalAlignContainer,
        _GUI.HorizontalAlignContainer,
        _GUI.TabContainer,
        _GUI.HorizontalScrollBar,
        _GUI.VerticalScrollBar,
    ]

    def __init__(self) -> None:
        self._GUIComponent_stack: list[_GUI.base.GUIBase] = []
        self.docking_manager = _GUI.DockingManager(profile.width, profile.height)

    def attach(self, *components: _GUI.base.GUIBase):
        for component in components:
            if any(issubclass(type(component), cls) for cls in Layer.PERMISSIONS):
                self._GUIComponent_stack.append(component)
                component.parent = self
                if profile._gdk_executed: # 実行中にGUI componentが追加されたときにイベント登録
                    component._regist_events()
            else:
                raise AttachPermissionError(component, self)
    
    def update(self):
        with _BenchMark(f"{self}.update()"):
            self.docking_manager.update()

            for component in reversed(self._GUIComponent_stack):
                with _BenchMark(f"{component}.update()"):
                    component.update()
        
    def draw(self):
        with _BenchMark(f"{self}.draw()"):
            for component in self._GUIComponent_stack:
                component.draw()

class LayerObject(Layer, _event.EventObject):
    pass

class LayerManager:
    current_layer: _Optional[Layer] = None
    layer_stack: list[Layer] = []

    @staticmethod
    def pushLayer(layer: Layer):
        if LayerManager.current_layer is None:
            LayerManager.current_layer = layer
        LayerManager.layer_stack.append(layer)

    @staticmethod
    def update():
        if LayerManager.current_layer is not None:
            LayerManager.current_layer.update()
    
    @staticmethod
    def draw():
        if LayerManager.current_layer is not None:
            LayerManager.current_layer.draw()