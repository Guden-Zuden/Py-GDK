'''
Group of functions used by package users.
'''

from .base import *
from . import layer as _layer
from . import scene as _scene

def createLayer():
    new_layer = _layer.Layer()
    _layer.LayerManager.pushLayer(new_layer)
    return new_layer

def createScene():
    new_scene = _scene.Scene()
    _scene.SceneManager.pushScene(new_scene)
    return new_scene

__all__ = [
    "createLayer",
    "createScene",
]