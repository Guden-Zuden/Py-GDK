from __future__ import annotations

from typing import Any as _Any

from .. import layer as _layer
from .. import scene as _scene
from ._panel import DebuggerPanel, _TabSource


class SceneDebugger:
    def __init__(
        self,
        layer: _layer.Layer,
        scene: _scene.Scene | None = None,
    ) -> None:
        self.current_layer = layer
        self._selected_scene = scene

        self.Scene_Container = DebuggerPanel([
            _TabSource(
                "Scenes",
                self._scene_rows,
                self._format_scene,
                lambda row: row[0] if not isinstance(row, str) else row,
            ),
            _TabSource(
                "Entities",
                self._entity_rows,
                self._format_entity,
                lambda row: id(row) if not isinstance(row, str) else row,
            ),
            _TabSource(
                "Cameras",
                self._camera_rows,
                self._format_camera,
                lambda row: getattr(row, "name", id(row))
                if not isinstance(row, str)
                else row,
            ),
            _TabSource(
                "World",
                self._world_rows,
                self._format_world,
                lambda row: id(row) if not isinstance(row, str) else row,
            ),
        ])
        self.TP_scenes, self.TP_entities, self.TP_cameras, self.TP_world = (
            self.Scene_Container.tab_properties
        )
        self.current_layer.attach(self.Scene_Container)

    def _get_scene(self) -> _scene.Scene | None:
        if self._selected_scene is not None:
            return self._selected_scene
        return _scene.SceneManager.current_scene

    @staticmethod
    def _scene_rows() -> list[tuple[str, _scene.Scene] | str]:
        rows: list[tuple[str, _scene.Scene] | str] = list(
            _scene.SceneManager.scene_stack.items()
        )
        return rows or ["No scenes registered"]

    def _entity_rows(self) -> list[_Any]:
        scene = self._get_scene()
        if scene is None or not scene._entity_stack:
            return ["No entities"]
        return list(scene._entity_stack)

    def _camera_rows(self) -> list[_Any]:
        scene = self._get_scene()
        if scene is None or not scene._camera_stack:
            return ["No cameras"]
        return list(scene._camera_stack.values())

    def _world_rows(self) -> list[_Any]:
        scene = self._get_scene()
        return [scene] if scene is not None else ["No active scene"]

    @staticmethod
    def _format_scene(row: _Any) -> str:
        if isinstance(row, str):
            return row

        name, scene = row
        active = "*" if scene is _scene.SceneManager.current_scene else " "
        return (
            f"{active} {name}: entities={len(scene._entity_stack)} "
            f"cameras={len(scene._camera_stack)} "
            f"tilemap={'yes' if scene._tilemap is not None else 'no'}"
        )

    @staticmethod
    def _format_entity(entity: _Any) -> str:
        if isinstance(entity, str):
            return entity

        movement_model = getattr(entity, "movement_model", None)
        movement_velocity = getattr(movement_model, "velocity", None)
        colliders = getattr(entity, "colliders", ())
        return (
            f"{type(entity).__name__} pos={entity.pos.tuple} "
            f"size={entity.size.tuple} velocity={entity.velocity.tuple} "
            f"movement={type(movement_model).__name__} "
            f"movement_velocity={getattr(movement_velocity, 'tuple', None)} "
            f"colliders={len(colliders)}"
        )

    def _format_camera(self, camera: _Any) -> str:
        if isinstance(camera, str):
            return camera

        scene = self._get_scene()
        active = scene is not None and camera is scene.current_camera
        following = getattr(camera, "following_entity", None)
        following_name = (
            type(following).__name__ if following is not None else "none"
        )
        marker = "*" if active else " "
        return (
            f"{marker} {getattr(camera, 'name', type(camera).__name__)} "
            f"pos={camera.pos.tuple} smoothing={getattr(camera, 'smoothing', 'n/a')} "
            f"following={following_name}"
        )

    def _format_world(self, scene: _Any) -> str:
        if isinstance(scene, str):
            return scene

        tilemap = scene._tilemap
        map_data = getattr(tilemap, "map_data", None)
        if map_data is None:
            tilemap_info = "none" if tilemap is None else "not loaded"
        else:
            layer_names = ", ".join(
                map_layer.name for map_layer in map_data.map_datas
            )
            tilemap_info = (
                f"{map_data.width}x{map_data.height} layers=[{layer_names}]"
            )

        collision_layers = scene.col_manager.collision_layers
        collider_count = sum(
            len(collision_layer.colliders)
            for collision_layer in collision_layers.values()
        )
        camera_name = (
            scene.current_camera.name
            if scene.current_camera is not None
            else "none"
        )
        return (
            f"view={scene.view_position.tuple} camera={camera_name} "
            f"tilemap={tilemap_info} "
            f"collision_layers={len(collision_layers)} colliders={collider_count}"
        )

    def update(self) -> None:
        self.Scene_Container.refresh()
