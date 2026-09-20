import pygame as _pg

from . import entity as _entity

class Collider:
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

        