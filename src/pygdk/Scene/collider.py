from typing import Any

import pygame as _pg
from enum import (
    Enum as _Enum,
    auto as _auto
)

from ..base import *
from . import base as _base
from . import entity as _entity
from .. import time as _time

class Collider:
    """
    #### Description
        This class provides the connection to entity data.
    #### Parameters
        - `entity`: To get the data.
        - `collider_type`: There are types: SOLID, TRIGGER.
        - `enabled`: Whether enables colliding.
    """
    def __init__(
            self, 
            entity: _base.EntityBase, 
            collider_type = ColliderType.SOLID) -> None:
        self.entity = entity
        self.collider_type = collider_type
        self.enabled = True

        self._moved = False # flag (not to move multiple time in same frame.)

    @property
    def x(self): return self.entity.pos.x
    @x.setter
    def x(self, value: float): self.entity.pos.x = value

    @property
    def y(self): return self.entity.pos.y
    @y.setter
    def y(self, value: float): self.entity.pos.y = value

    @property
    def width(self): return self.entity.size.width

    @property
    def height(self): return self.entity.size.height

    @property
    def rect(self): return self.entity.get_rect()


class TilemapCollider:
    """Not implemented yet."""
    def __init__(
            self,
            tilemap
            ):
        self.tilemap = tilemap


# Collision Detector: detect overlapping entity
class Detector:
    """Detect colliding."""
    @staticmethod
    def detect(current_col: Collider, other_col: Collider):
        return current_col.rect.colliderect(other_col.rect)

# Collision Resolver
class Resolver:
    """Resolve collisions."""
    @staticmethod
    def resolve(current_col: Collider, other_cols: list[Collider], dt: float):
        if not current_col.enabled:
            return

        if current_col.collider_type == ColliderType.TRIGGER:
            return

        entity = current_col.entity
        if entity is None:
            return

        # X axis
        entity.pos.x += entity.movement_model.velocity.x * dt

        for other_col in other_cols:
            if other_col is current_col or not other_col.enabled:
                continue

            if other_col.collider_type == ColliderType.TRIGGER:
                continue

            if Detector.detect(current_col, other_col):
                if entity.velocity.x > 0:
                    entity.pos.x -= (
                        current_col.rect.right - other_col.rect.left
                    )
                    entity.velocity.x = 0

                elif entity.velocity.x < 0:
                    entity.pos.x += (
                        other_col.rect.right - current_col.rect.left
                    )
                    entity.velocity.x = 0

        # Y axis
        entity.pos.y += entity.movement_model.velocity.y * dt

        for other_col in other_cols:
            if other_col is current_col or not other_col.enabled:
                continue

            if other_col.collider_type == ColliderType.TRIGGER:
                continue

            if Detector.detect(current_col, other_col):
                if entity.velocity.y > 0:
                    entity.pos.y -= (
                        current_col.rect.bottom - other_col.rect.top
                    )
                    entity.velocity.y = 0

                elif entity.velocity.y < 0:
                    entity.pos.y += (
                        other_col.rect.bottom - current_col.rect.top
                    )
                    entity.velocity.y = 0

# Collision Layer
class CollisionLayer:
    """
    Manages a collection of colliders and handles collision detection,
    resolution, and collision event dispatching.

    Collision events (enter, stay, exit) are tracked between frames.
    Trigger colliders generate collision events without physical resolution,
    while solid colliders are processed by the collision resolver.
    """
    def __init__(self) -> None:
        self.colliders: list[Collider] = []

        self._prev_pairs: set[tuple[Collider, Collider]] = set()
        self._curr_pairs: set[tuple[Collider, Collider]] = set()

    def attach(self, *colliders: Collider) -> None:
        for collider in colliders:
            self.colliders.append(collider)

    def _collect_collision_pairs(self):
        pairs: set[tuple[Collider, Collider]] = set() # [0] collides to [1]

        for i, col_a in enumerate(self.colliders):
            if not col_a.enabled or col_a.entity is None:
                continue

            for col_b in self.colliders[i + 1:]:
                if not col_b.enabled or col_b.entity is None:
                    continue

                if col_a is col_b:
                    continue

                # Trigger同士、またはTriggerとSolidだけをイベント対象にする
                if (col_a.collider_type != ColliderType.TRIGGER
                    and col_b.collider_type != ColliderType.TRIGGER):
                    continue

                if Detector.detect(col_a, col_b):
                    pairs.add((col_a, col_b))

        return pairs
    
    def _dispatch_collision_event(self, pair: tuple[Collider, Collider], event: str):
        col_a, col_b = pair

        for current, other in ((col_a, col_b), (col_b, col_a)):
            entity = current.entity

            if entity is None:
                continue

            match event:
                case "enter":
                    callback = entity.callback_col_enter
                case "stay":
                    callback = entity.callback_col_stay
                case "exit":
                    callback = entity.callback_col_exit
                case _:
                    raise Exception(f"wrong event: event")

            if callback is not None:
                callback(other.entity)

    def _update_collision_events(self):
        self._curr_pairs = self._collect_collision_pairs()

        entered = self._curr_pairs - self._prev_pairs
        stayed = self._curr_pairs & self._prev_pairs
        exited = self._prev_pairs - self._curr_pairs

        for pair in entered:
            self._dispatch_collision_event(pair, "enter")

        for pair in stayed:
            self._dispatch_collision_event(pair, "stay")

        for pair in exited:
            self._dispatch_collision_event(pair, "exit")

    def solve(self):
        self._prev_pairs = self._curr_pairs

        for collider in self.colliders:
            if not collider.enabled:
                continue

            if collider.collider_type == ColliderType.TRIGGER:
                collider.entity.pos.x += collider.entity.movement_model.velocity.x * _time.dt
                collider.entity.pos.y += collider.entity.movement_model.velocity.y * _time.dt
                continue

            Resolver.resolve(
                collider,
                self.colliders,
                _time.dt
            )

        self._update_collision_events()

# Collision Manager Class
class CollisionManager:
    def __init__(self) -> None:
        self.collision_layers: dict[str, CollisionLayer] = {}

    def push(self, layer_name: str, collision_layer: CollisionLayer):
        self.collision_layers[layer_name] = collision_layer

    def update(self):
        for layer_name, col_layer in self.collision_layers.items():
            col_layer.solve()