from .base import *
from . import profile
from . import GUI

class AttachPermissionError(Exception):
    def __init__(self, component: Any, attach_to: Any):
        self.component = component
        self.attach_to = attach_to

    def __str__(self):
        return (
            f"{self.component} is not allowed to attach to {self.attach_to}."
        )

class Layer:
    PERMISSIONS: list[Any] = [
        GUI.Text,
        GUI.Box,
        GUI.VerticalAlignContainer,
        GUI.HorizontalAlignContainer
    ]

    def __init__(self) -> None:
        self.__GUIComponent_stack: list[GUI.base.GUIBase] = []

    def attach(self, *components: GUI.base.GUIBase):
        for component in components:
            if any(type(component) == cls for cls in Layer.PERMISSIONS):
                self.__GUIComponent_stack.append(component)
            else:
                raise AttachPermissionError(component, self)
    
    def update(self):
        for component in reversed(self.__GUIComponent_stack):
            component._reset_flag()
            component.update()
        
    def draw(self):
        for component in self.__GUIComponent_stack:
            component.draw()

class _LayerManager:
    current_layer: Optional[Layer] = None
    layer_stack: list[Layer] = []

    @staticmethod
    def pushLayer(layer: Layer):
        if _LayerManager.current_layer is None:
            _LayerManager.current_layer = layer
        _LayerManager.layer_stack.append(layer)

    @staticmethod
    def update():
        if _LayerManager.current_layer is not None:
            _LayerManager.current_layer.update()
    
    @staticmethod
    def draw():
        if _LayerManager.current_layer is not None:
            _LayerManager.current_layer.draw()