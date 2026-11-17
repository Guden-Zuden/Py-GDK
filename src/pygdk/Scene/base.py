from typing import TYPE_CHECKING

from ..base import *
from .. import profile as _profile
from ..time import Timer as _Timer
from . import attachments as _attachments

if TYPE_CHECKING:
    from . import collider as _collider

import pygame as _pg
from typing import (
    Optional as _Optional,
    Callable as _Callable,
    Sequence as _Sequence
)
from functools import (
    wraps as _wraps
)
from logging import (
    getLogger as _getLogger
)

logger = _getLogger(__name__)

class EntityBase():
    def __init__(
            self, 
            x: float, 
            y: float, 
            width: float, 
            height: float, 
            movement_model: _Optional[_attachments.MovementModelBase] = None,
            colliders: _Sequence[_collider.Collider] = (),
            callback_col_enter: _Optional[_Callable[[EntityBase], None]] = None,
            callback_col_stay: _Optional[_Callable[[EntityBase], None]] = None,
            callback_col_leave: _Optional[_Callable[[EntityBase], None]] = None,
            ) -> None:
        self._timer = _Timer()
        self.pos = Vec2(x, y)
        self.velocity = Vec2(0, 0)

        self.size = Vec2(width, height)
        if movement_model:
            self.movement_model = movement_model
        else:
            self.movement_model = _attachments.MovementModelMob(0, 0, 0)
        
        self.colliders: list[_collider.Collider] = list(colliders)

        self.callback_col_enter: _Optional[_Callable[[EntityBase], None]] = callback_col_enter
        self.callback_col_stay: _Optional[_Callable[[EntityBase], None]] = callback_col_stay
        self.callback_col_exit: _Optional[_Callable[[EntityBase], None]] = callback_col_leave

    def update(self):
        self._timer.update()

        if self.movement_model:
            # self.movement_model.velocity = self.velocity
            self.movement_model.update()
            vel = self.movement_model.velocity
            vel = self.movement_model.velocity.normalized * min(vel.distance(), self.movement_model.max_speed)
        
        self._timer.reset()

    def draw(self, view_position: Vec2):
        pass

    def get_rect(self) -> _pg.Rect:
        if self.colliders is None:
            raise Exception("No collider")

        return _pg.Rect(
            self.pos.x - self.size.width/2, 
            self.pos.y - self.size.height/2, 
            self.size.width, 
            self.size.height
            )

    def make_collision(self, type: _collider.ColliderType) -> _collider.Collider:
        """
        #### Description
            Create a collider for this entity and return it.

        #### Parameters
            type (ColliderType): The type of collider to create.
                - `SOLID`: Collides with other solid colliders.
                - `TRIGGER`: Detects collisions without physical collision resolution.

        #### Returns
            collider: The created collider
        """
        from . import collider as _collider
        collider = _collider.Collider(self, type)
        self.colliders.append(collider)
        return collider

    def OnEnter(self):
        """
        #### Description
            Register a callback that is invoked when this entity starts colliding
            with another entity.

        #### Parameters
            other (EntityBase): The entity that this entity starts colliding with.
        """
        def decorator(func: _Callable):
            @_wraps(func)
            def wrapper(other: EntityBase):
                logger.debug("OnEnter executed: %s", self)
                return func(other)

            self.callback_col_enter = wrapper
            return wrapper

        return decorator

    def OnStay(self):
        """
        #### Description
            Register a callback that is invoked when this entity is colliding
            with another entity.

        #### Parameters
            other (EntityBase): The entity that this entity is colliding with.
        """
        def decorator(func: _Callable):
            @_wraps(func)
            def wrapper(other: EntityBase):
                logger.debug("OnStay executed: %s", self)
                return func(other)

            self.callback_col_stay = wrapper
            return wrapper

        return decorator

    def OnExit(self):
        """
        #### Description
            Register a callback that is invoked when this entity ends colliding
            with another entity.

        #### Parameters
            other (EntityBase): The entity that this entity ends colliding with.
        """
        def decorator(func: _Callable):
            @_wraps(func)
            def wrapper(other: EntityBase):
                logger.debug("OnExit executed: %s", self)
                return func(other)

            self.callback_col_exit = wrapper
            return wrapper

        return decorator

__all__ = [
    "EntityBase",
]