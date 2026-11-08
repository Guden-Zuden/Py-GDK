from typing import Any

import pygame as _pg
from enum import (
    Enum as _Enum,
    auto as _auto
)

from . import base as _base
from . import entity as _entity

# Collision Manager Class
class Collision:
    """not implemented yet."""
    def __init__(self) -> None:
        self.colliders: list[Collider] = []

    def attach(self, collider: Collider) -> None:
        self.colliders.append(collider)

    def solve(self, entity: _base.EntityBase, dx: float, dy: float, rect: _pg.Rect):
        """call after movement execution"""
        if entity.collider is None: return
        if entity.collider.collider_type == ColliderType.TRIGGER: return

        for collider in self.colliders:
            if collider is None: continue
            if collider is entity.collider: continue
            if entity.collider.collider_type == ColliderType.TRIGGER: continue

            # if _pg.Rect.colliderect(entity.get_collider_rect(), collider)


# Colliders
class ColliderType(_Enum):
    SOLID = _auto()
    TRIGGER = _auto()

class Collider:
    def __init__(
            self, 
            owner: _base.EntityBase, 
            width: float, 
            height: float, 
            collider_type = ColliderType.SOLID) -> None:
        self.owner = owner
        self.width = width
        self.height = height
        self.collider_type = collider_type
        self.enabled = True

class TilemapCollider:
    def __init__(
            self,
            tilemap
            ):
        self.tilemap = tilemap

"""
    def __init__(self) -> None:
        self._entity_stack: list[_entity.Entity] = []

    def append(self, entity: _entity.Entity):
        if not issubclass(type(entity), _entity.Entity):
            raise Exception(f"Invalid object: {entity} is not entity.")
        self._entity_stack.append(entity)

    def collide(self, entity: _entity.Entity):
        colliding_entities = [
            other_ent for other_ent in self._entity_stack
            if _pg.Rect.colliderect(
                _pg.Rect(entity.pos.x, entity.pos.y, entity.size.width, entity.size.height),
                _pg.Rect(other_ent.pos.x, other_ent.pos.y, other_ent.size.width, other_ent.size.height)
            )
        ]

        entity.pos.x += entity.velocity.x

"""