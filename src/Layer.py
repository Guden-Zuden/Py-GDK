from typing import Optional

from . import GUI
from . import Base
from . import Event
from .Log import *

class MouseProcedure:
    def __init__(self) -> None:
        pass

    def reset(self) -> None:
        pass

class Layer:
    def __init__(self) -> None:
        self._layerComponent_stack: list[Base.LayerComponentBase] = []
        self._panel_stack: list[GUI.Panel] = []

    def attach(self, component: Base.LayerComponentBase):
        if type(component) == GUI.Button:
            self._layerComponent_stack.append(component)
        elif type(component) == GUI.Text:
            self._layerComponent_stack.append(component)
        elif type(component) == GUI.Box:
            self._layerComponent_stack.append(component)
        elif type(component) == GUI.SpriteBox:
            self._layerComponent_stack.append(component)
        elif type(component) == GUI.Panel:
            self._panel_stack.append(component)
        elif type(component) == GUI.DraggableObj:
            self._layerComponent_stack.append(component)
        else:
            Log.warn("Layer", f"{type(component)} is not allowed to attach to Layers.")

    def update(self):
        GUI.Button.reset()
        for component in reversed(self._layerComponent_stack):
            component.update()
        for panel in self._panel_stack:
            panel.update()

    def draw(self):
        for component in self._layerComponent_stack:
            component.draw()
        for panel in self._panel_stack:
            panel.draw()

class LayerManager:
    _current_layer: Optional[Layer] = None
    _layer_stack: list[Layer] = []

    _mouseX, _mouseY = 0, 0

    @staticmethod
    def pushLayer(layer: Layer):
        if LayerManager._current_layer is None:
            LayerManager._current_layer = layer
        LayerManager._layer_stack.append(layer)

    @staticmethod
    def update():
        if LayerManager._current_layer is not None:
            LayerManager._current_layer.update()

    @staticmethod
    def draw():
        if LayerManager._current_layer is not None:
            LayerManager._current_layer.draw()

@Event.OnMousemove()
def updateLayerMousePos(e):
    LayerManager._mouseX, LayerManager._mouseY = e.pos[0], e.pos[1]