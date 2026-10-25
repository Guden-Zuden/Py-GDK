'''
Group of functions used by package users.
'''

from .base import *
from . import layer as _layer
from . import scene as _scene

def createLayer(layer_name: str):
    new_layer = _layer.Layer()
    _layer.LayerManager.pushLayer(layer_name, new_layer)
    return new_layer

def changeLayer(layer_name: str):
    _layer.LayerManager.changeLayer(layer_name)

def createScene(layer_name: str):
    new_scene = _scene.Scene()
    _scene.SceneManager.push_scene(layer_name, new_scene)
    return new_scene

def changeScene(scene_name: str):
    _scene.SceneManager.change_scene(scene_name)

__all__ = [
    "createLayer",
    "createScene",
]