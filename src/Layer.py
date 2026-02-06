from typing import Optional

from . import Text, Button, Box
from . import Components
from . import Event
from .Log import *

class Layer:
    def __init__(self) -> None:
        self._layerComponent_stack: list[Components.LayerComponentBase] = []

    def attach(self, component: Components.LayerComponentBase):
        if type(component) == Button.Button:
            self._layerComponent_stack.append(component)
        elif type(component) == Text.Text:
            self._layerComponent_stack.append(component)
        elif type(component) == Box.Box:
            self._layerComponent_stack.append(component)
        else:
            Log.warn("Layer", f"{type(component)} is not allowed to attach to Layers.")

    def update(self):
        for component in self._layerComponent_stack:
            component.update()

    def draw(self):
        for component in self._layerComponent_stack:
            component.draw()

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
    


def createLayer() -> Layer:
    layer = Layer()
    LayerManager.pushLayer(layer)
    return layer