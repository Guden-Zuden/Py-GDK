from .base import *
from . import profile
from . import Scene as _Scene
from . import event as _event
from .time import BenchMark as _BenchMark
from .exceptions import *

from typing import (
    Any as _Any,
    Optional as _Optional
)

class Scene:
    PERMISSIONS: list[_Any] = [
        _Scene.Entity,
        _Scene.Collider,
        _Scene.Camera,
    ]

    def __init__(self, tilemap: _Optional[_Scene.Tilemap] = None) -> None:
        from .Scene.camera import Camera
        self.current_camera: _Optional[Camera] = None
        self.view_position = Vec2(0, 0)

        self._tilemap = tilemap
        self._camera_stack: dict[str, Camera] = {}
        self._entity_stack: list[_Scene.EntityBase] = []

    def attach(self, *entities: _Scene.EntityBase):
        from .Scene.camera import Camera
        for entity in entities:
            if any(issubclass(type(entity), cls) for cls in Scene.PERMISSIONS):
                if issubclass(type(entity), Camera):
                    self._camera_stack[entity.name] = entity
                else:
                    self._entity_stack.append(entity)

                if profile._gdk_executed: # 今のところ保留
                    # entity._regist_events()
                    pass
            else:
                raise AttachPermissionError(entity, self)

    def set_camera(self, name: str):
        self.current_camera = self._camera_stack[name]
    
    def update(self):
        with _BenchMark(f"{self}.update()"):
            if self._tilemap: self._tilemap.update()
            for entity in reversed(self._entity_stack):
                with _BenchMark(f"{entity}.update()"):
                    entity.update()
            if self.current_camera: self.current_camera.update()
        
    def draw(self):
        if self.current_camera:
            _view_position = self.current_camera.pos - Vec2(profile.window.surface_width, profile.window.surface_height)/2
        else:
            _view_position = Vec2(0, 0)
        with _BenchMark(f"{self}.draw()"):
            if self._tilemap: self._tilemap.draw(*_view_position)
            for entity in self._entity_stack:
                entity.draw(_view_position)
            if self.current_camera: self.current_camera.draw(_view_position)

class SceneObject(Scene, _event.EventObject):
    pass

class SceneManager:
    current_scene: _Optional[Scene] = None
    scene_stack: list[Scene] = []

    @staticmethod
    def pushScene(scene: Scene):
        if SceneManager.current_scene is None:
            SceneManager.current_scene = scene
        SceneManager.scene_stack.append(scene)

    @staticmethod
    def update():
        if SceneManager.current_scene is not None:
            SceneManager.current_scene.update()
    
    @staticmethod
    def draw():
        if SceneManager.current_scene is not None:
            SceneManager.current_scene.draw()