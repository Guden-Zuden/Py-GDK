from . import Profile
from . import Utils
from .Log import *

import pygame as _pygame
import os
from enum import Enum

class Sprite:
    def __init__(self) -> None:
        self.sprites: list[_pygame.Surface] = []
    
    def load_tile(self, img_filepath: str | os.PathLike, sprite_size: int, sprite_padding: int, offset_x: int = 0, offset_y: int = 0):
        """If there are spaces around image, set offsets."""
        assert Profile.sprite_size is not None

        img = _pygame.image.load(img_filepath).convert_alpha()
        img_w, img_h = img.get_size()
        count = 0

        for h in range((img_h // (sprite_size + sprite_padding))):
            for w in range((img_w // (sprite_size + sprite_padding))):
                start_px = sprite_size*w + sprite_padding*w + offset_x
                start_py = sprite_size*h + sprite_padding*h + offset_y

                trim_img = img.subsurface((start_px, start_py), (sprite_size, sprite_size))
                trim_img = _pygame.transform.smoothscale(trim_img, (Profile.sprite_size, Profile.sprite_size))
                self.sprites.append(trim_img)
                count += 1

        Log.info("Sprite", f"Loaded {count} tiles from '{img_filepath}'.")

    def draw(self, sprite_num: int, x: float, y: float, anchor: Utils.Anchor = Utils.Anchor.default):
        assert Profile.surface is not None
        sprite_num = sprite_num % len(self.sprites)
        sprite = self.sprites[sprite_num]
        pos = Utils.applyAnchor(x, y, sprite.get_width(), sprite.get_height(), anchor)

        Profile.surface.blit(sprite, pos)

    def draw_border(self, sprite_num: int, x: float, y: float, anchor: Utils.Anchor = Utils.Anchor.default):
        assert Profile.sprite_size is not None
        assert Profile.surface is not None
        pos = Utils.applyAnchor(Profile.sprite_size, Profile.sprite_size, x, y, anchor)
        if Profile.surface == None:
            Log.critical("Sprite", "Screen is missing.")
        
        if sprite_num > 0:
            _pygame.draw.rect(Profile.surface, (255, 255, 255), _pygame.Rect(pos, [Profile.sprite_size, Profile.sprite_size]), 1)