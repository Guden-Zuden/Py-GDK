'''
Group of functions used by package users.
'''

from .base import *
from . import layer

def createLayer():
    new_layer = layer.Layer()
    layer._LayerManager.pushLayer(new_layer)
    return new_layer

__all__ = [
    "createLayer",
]