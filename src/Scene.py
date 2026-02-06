from . import Entity, Text
from . import Components
from . import Tilemap
from .Log import *
from . import Profile
from . import Collision

import pygame as _pygame


class Scene:
    def __init__(self) -> None:
        self.adaptedComponent: Components.ComponentBase = Components.ComponentBase(0, 0)
        self._offset_x: float = 0
        self._offset_y: float = 0
        self._tilemap: Tilemap.Tilemap = Tilemap.Tilemap()
        self._entity_stack: list[Entity.Entity] = []
        self._component_stack: list[Components.ComponentBase] = []

    def attach(self, component: Components.ComponentBase):
        if type(component) == Tilemap.Tilemap:
            self._tilemap = component
        elif type(component) == Entity.Entity:
            self._entity_stack.append(component)
        elif type(component) == Text.Text:
            self._component_stack.append(component)

    def adaptCameraOn(self, component: Components.ComponentBase):
        if (self._tilemap != component
            and component not in self._entity_stack
            and component not in self._component_stack):
            Log.error("Scene", f"{component} is not attached in this Scene.")            
        self.adaptedComponent = component

    def update(self):
        self._tilemap.update()
        self._offset_x, self._offset_y = self.adaptedComponent.x - Profile.width/2, self.adaptedComponent.y - Profile.height/2
        for entity in self._entity_stack:
            entity.update()
            Collision._update(entity, self._tilemap)

    def draw(self):
        self._tilemap.draw(self._offset_x, self._offset_y)
        for entity in self._entity_stack:
            entity.draw(self._offset_x, self._offset_y)
        for comp in self._component_stack:
            comp.draw(self._offset_x, self._offset_y)

class SceneManager:
    _current_scene: Scene | None = None
    _scene_stack: list[Scene] = []

    @staticmethod
    def pushScene(scene: Scene):
        if SceneManager._current_scene is None:
            SceneManager._current_scene = scene
        SceneManager._scene_stack.append(scene)

    @staticmethod
    def update():
        # assert SceneManager._current_scene is not None
        if SceneManager._current_scene is not None:
            SceneManager._current_scene.update()

    @staticmethod
    def draw():
        if SceneManager._current_scene is None:
            Log.warn("SceneManager", "Any scene has not been set. So, there are nothing to draw.")
        else: SceneManager._current_scene.draw()


def createScene() -> Scene:
    scene = Scene()
    SceneManager.pushScene(scene)
    return scene
