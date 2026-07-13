'''
Group of functions used by package users.
'''

from typing import Callable

from . import layer

def createLayer():
    new_layer = layer.Layer()
    layer._LayerManager.pushLayer(new_layer)
    return new_layer