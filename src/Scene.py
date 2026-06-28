from . import Entity
from . import Base
from . import Tilemap
from .Log import *
from . import Profile
from . import Collision

import pygame as _pygame
from typing import Optional

class Scene:
    def __init__(self) -> None:
        self.adaptedComponent: Base.SceneComponentBase = Base.SceneComponentBase(0, 0)
        self._offset_x: float = 0
        self._offset_y: float = 0
        self._tilemap: Tilemap.Tilemap = Tilemap.Tilemap()
        self._entity_stack: list[Entity.Entity] = []
        self._component_stack: list[Base.SceneComponentBase] = []

    def attach(self, component: Base.SceneComponentBase):
        if type(component) == Tilemap.Tilemap:
            self._tilemap = component
        elif type(component) == Entity.Entity:
            self._entity_stack.append(component)
        else:
            Log.error("Scene", f"{type(component)} is not allowed to attach to Scenes.")

    def adaptCameraOn(self, component: Base.SceneComponentBase):
        if (self._tilemap != component
            and component not in self._entity_stack
            and component not in self._component_stack):
            Log.error("Scene", f"{type(component)} is not attached in this Scene.")
            return
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
    _current_scene: Optional[Scene] = None
    _scene_stack: list[Scene] = []
    __warned: bool = False

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
            if SceneManager.__warned == False:
                Log.warn("SceneManager", "Any scene has not been set. So, there are nothing to draw.")
                SceneManager.__warned = True
            return
        else:
            assert SceneManager._current_scene is not None
            SceneManager._current_scene.draw()