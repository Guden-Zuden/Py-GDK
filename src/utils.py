'''
Group of functions used by package users.
'''

from .base import *
from . import layer as _layer

def createLayer():
    new_layer = _layer.Layer()
    _layer.LayerManager.pushLayer(new_layer)
    return new_layer

__all__ = [
    "createLayer",
]