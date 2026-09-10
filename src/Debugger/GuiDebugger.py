from typing import (
    Optional as _Optional
)

from src.colors import WHITE

from .. import (
    GUI as _GUI,
    layer as _layer,
    colors as _colors
)
from ..layer import LayerManager
from ..base import *

class _Label(_GUI.Label):
    from .. import profile as _profile
    def __init__(self, u: float, v: float, component: _GUI.base.GUIBase, textAttributes=_profile.default_textAttributes, anchor: _layer.Anchor = Anchor.CENTER, padding=_profile.default_padding, wrap_width: int = 0, border: _layer.Border = Border(0, _colors.WHITE), no_register=False) -> None:
        self._component = component
        super().__init__(u, v, "no component", textAttributes, anchor, padding, wrap_width, border, no_register)

    def on_update(self):
        self.text = self._component.__str__() + " " + self._component.size.__str__()

class GUIDebugger:
    def __init__(self, layer: _layer.Layer) -> None:
        self.current_layer = layer
        self.GUI_Components_Container = _GUI.TabContainer(
            0, 0, 500, 300, Background(_colors.BLACK), Background((0, 70, 70)), Background(_colors.BLACK),
            tab_textAttributes=TextAttributes("msgothic", 12, _colors.WHITE),
            tab_properties=[
                TabProperty(
                    "GUI components", 
                    [_Label(0, 0, component, TextAttributes("msgothic", 15, _colors.WHITE))
                    for component in self.current_layer._GUIComponent_stack]
                )
            ]
        )

        self.current_layer.attach(self.GUI_Components_Container)

    def update(self):
        self.current_layer = LayerManager.current_layer
        if self.current_layer is None: return

        # self.GUI_Components_Container.VC_TabItems.set_items([
        #     _GUI.Label(
        #         0, 0, component.__str__(),
        #         TextAttributes("msgothic", 15, Color(0,255,255) if component is _GUI.base.GUIBase.g_hoveredObj else _colors.WHITE))
        #     for component in self.current_layer._GUIComponent_stack
        # ])
    
    def append_text(self, component: _GUI.base.GUIBase):
        label = _Label(
            0, 0, component,
            TextAttributes("msgothic", 15, Color(255,255,255))
        )

        self.GUI_Components_Container.VC_TabItems.push_item(
            label
        )