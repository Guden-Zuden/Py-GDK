from . import Profile
from . import Entity, Tilemap

import pygame as _pygame

def _update(entity: Entity.Entity, tilemap: Tilemap.Tilemap):
    entity.x += entity.vx

    for x in range(tilemap.viewport.end_x - tilemap.viewport.start_x):
        for y in range(tilemap.viewport.end_y - tilemap.viewport.start_y):
            _x = x +  tilemap.viewport.start_x
            _y = y + tilemap.viewport.start_y
            
            if tilemap.collision_data[_y][_x] != 0:
                rect_x = _x*Profile.sprite_size
                rect_y = _y*Profile.sprite_size
                rect = _pygame.Rect(rect_x, rect_y, Profile.sprite_size, Profile.sprite_size)
                entity_rect = _pygame.Rect(entity.x - Profile.sprite_size/2, entity.y - Profile.sprite_size/2, Profile.sprite_size, Profile.sprite_size)
                
                if rect.colliderect(entity_rect):
                    if entity.vx > 0:
                        entity.x = rect.left - entity_rect.width/2
                    elif entity.vx < 0:
                        entity.x = rect.right + entity_rect.width/2

    entity.y += entity.vy

    for x in range(tilemap.viewport.end_x - tilemap.viewport.start_x):
        for y in range(tilemap.viewport.end_y - tilemap.viewport.start_y):
            _x = x +  tilemap.viewport.start_x
            _y = y + tilemap.viewport.start_y
            
            if tilemap.collision_data[_y][_x] != 0:
                rect_x = _x*Profile.sprite_size
                rect_y = _y*Profile.sprite_size
                rect = _pygame.Rect(rect_x, rect_y, Profile.sprite_size, Profile.sprite_size)
                entity_rect = _pygame.Rect(entity.x - Profile.sprite_size/2, entity.y - Profile.sprite_size/2, Profile.sprite_size, Profile.sprite_size)
                    
                if rect.colliderect(entity_rect):
                    if entity.vy > 0:
                        entity.y = rect.top - entity_rect.height/2
                    elif entity.vy < 0:
                        entity.y = rect.bottom + entity_rect.height/2

def _isCollide(self_entity: Entity.Entity, other_entity: Entity.Entity):
    self_entity_rect = _pygame.Rect(self_entity.x - Profile.sprite_size/2, self_entity.y - Profile.sprite_size/2, Profile.sprite_size, Profile.sprite_size)
    other_entity_rect = _pygame.Rect(other_entity.x - Profile.sprite_size/2, other_entity.y - Profile.sprite_size/2, Profile.sprite_size, Profile.sprite_size)
    if self_entity_rect.colliderect(other_entity_rect):
        return True
    return False