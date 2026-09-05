from typing import (
    Optional as _Optional
)

from .. import (
    GUI as _GUI,
    layer as _layer,
)
from ..layer import LayerManager

class GUIDebugger:
    def __init__(self) -> None:
        self.current_layer: _Optional[_layer.Layer] = None
        

    def update(self):
        self.current_layer = LayerManager.current_layer

    