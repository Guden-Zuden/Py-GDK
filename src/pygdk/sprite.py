from .base import *
from . import profile as _profile

import pygame as _pg
import pathlib

def _applyAnchor(x: float, y: float, width: float, height: float, anchor: Anchor) -> tuple[float, float]:
    if   anchor == Anchor.CENTER: return (x-width/2, y-height/2)
    elif anchor == Anchor.RIGHT: return (x-width, y-height/2)
    elif anchor == Anchor.LEFT: return (x, y-height/2)
    elif anchor == Anchor.TOP: return (x-width/2, y)
    elif anchor == Anchor.BOTTOM: return (x-width/2, y-height)
    elif anchor == Anchor.RIGHTTOP: return (x-width, y)
    elif anchor == Anchor.RIGHTBOTTOM: return (x-width, y-height)
    elif anchor == Anchor.LEFTTOP: return (x, y)
    elif anchor == Anchor.LEFTBOTTOM: return (x, y-height)
    return (x, y)

class Sprite:
    def __init__(self) -> None:
        self.sprites: list[_pg.Surface] = []
    
    def load_tile(self, img_filepath: str | pathlib.Path, sprite_size: int, sprite_padding: int, offset_x: int = 0, offset_y: int = 0, isAntialias: bool = False):
        """If there are spaces around image, set offsets."""
        assert _profile.sprite_size is not None

        img = _pg.image.load(img_filepath).convert_alpha()
        img_w, img_h = img.get_size()
        count = 0

        for h in range((img_h // (sprite_size + sprite_padding))):
            for w in range((img_w // (sprite_size + sprite_padding))):
                start_px = sprite_size*w + sprite_padding*w + offset_x
                start_py = sprite_size*h + sprite_padding*h + offset_y

                trim_img = img.subsurface((start_px, start_py), (sprite_size, sprite_size))
                if isAntialias:
                    trim_img = _pg.transform.smoothscale(trim_img, (_profile.sprite_size, _profile.sprite_size))
                else:
                    trim_img = _pg.transform.scale(trim_img, (_profile.sprite_size, _profile.sprite_size))
                self.sprites.append(trim_img)
                count += 1

        print(f"[Sprite] Loaded {count} tiles from '{img_filepath}'.")

    def draw(self, sprite_num: int, x: float, y: float, anchor: Anchor = Anchor.CENTER):
        assert _profile.window is not None
        sprite_num = sprite_num % len(self.sprites)
        sprite = self.sprites[sprite_num]
        pos = _applyAnchor(x, y, sprite.get_width(), sprite.get_height(), anchor)

        _profile.window.surface.blit(sprite, pos)

    def draw_border(self, sprite_num: int, x: float, y: float, anchor: Anchor = Anchor.CENTER):
        assert _profile.sprite_size is not None
        assert _profile.window is not None
        pos = _applyAnchor(_profile.sprite_size, _profile.sprite_size, x, y, anchor)
        
        if sprite_num > 0:
            _pg.draw.rect(_profile.window.surface, (255, 255, 255), _pg.Rect(pos, [_profile.sprite_size, _profile.sprite_size]), 1)

    def transform(self, width: float, height: float):
        transformed_sprites: list[_pg.Surface] = []
        for sprite in self.sprites:
            transformed_sprites.append(_pg.transform.scale(sprite, [width, height]))
        sprite_obj = Sprite()
        sprite_obj.sprites = transformed_sprites
        return sprite_obj