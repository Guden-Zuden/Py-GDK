import unittest
from unittest.mock import patch

import pygame

from pygdk.Scene.collider import Collider, ColliderType, CollisionLayer, Detector
from pygdk.Scene.base import EntityBase


class RectEntity(EntityBase):
    def __init__(self, rect: pygame.Rect):
        super().__init__(rect.centerx, rect.centery, rect.width, rect.height)
        self.rect = rect

    def get_rect(self) -> pygame.Rect:
        return self.rect


class TestCollisionPairs(unittest.TestCase):
    def make_collider(
        self,
        rect: pygame.Rect,
        collider_type: ColliderType = ColliderType.TRIGGER,
    ) -> Collider:
        return Collider(RectEntity(rect), collider_type)

    def test_collection_matches_brute_force_for_mixed_colliders(self):
        colliders = [
            self.make_collider(pygame.Rect(-20, -10, 50, 30)),
            self.make_collider(pygame.Rect(0, 0, 20, 20), ColliderType.SOLID),
            self.make_collider(pygame.Rect(30, 0, 20, 20)),
            self.make_collider(pygame.Rect(50, 0, 20, 20), ColliderType.SOLID),
            self.make_collider(pygame.Rect(200, 200, 10, 10)),
        ]
        colliders[-1].enabled = False
        layer = CollisionLayer()
        layer.attach(*colliders)

        expected = set()
        for index, col_a in enumerate(colliders):
            if not col_a.enabled:
                continue
            for col_b in colliders[index + 1:]:
                if not col_b.enabled or col_a is col_b:
                    continue
                if (
                    col_a.collider_type != ColliderType.TRIGGER
                    and col_b.collider_type != ColliderType.TRIGGER
                ):
                    continue
                if col_a.rect.colliderect(col_b.rect):
                    expected.add((col_a, col_b))

        self.assertEqual(layer._collect_collision_pairs(), expected)

    def test_sparse_colliders_do_not_run_pairwise_detection(self):
        for vertical in (False, True):
            with self.subTest(vertical=vertical):
                layer = CollisionLayer()
                colliders = []
                for index in range(300):
                    x, y = (0, index * 40) if vertical else (index * 40, 0)
                    colliders.append(
                        self.make_collider(pygame.Rect(x, y, 20, 20))
                    )
                layer.attach(*colliders)

                with patch.object(Detector, "detect", wraps=Detector.detect) as detect:
                    self.assertEqual(layer._collect_collision_pairs(), set())

                detect.assert_not_called()

    def test_pair_order_remains_stable_when_colliders_move_past_each_other(self):
        entity_a = RectEntity(pygame.Rect(0, 0, 20, 20))
        entity_b = RectEntity(pygame.Rect(5, 0, 20, 20))
        collider_a = Collider(entity_a, ColliderType.TRIGGER)
        collider_b = Collider(entity_b, ColliderType.SOLID)
        layer = CollisionLayer()
        layer.attach(collider_a, collider_b)

        first_pairs = layer._collect_collision_pairs()
        entity_a.rect = pygame.Rect(10, 0, 20, 20)
        entity_b.rect = pygame.Rect(0, 0, 20, 20)
        second_pairs = layer._collect_collision_pairs()

        self.assertEqual(first_pairs, {(collider_a, collider_b)})
        self.assertEqual(second_pairs, first_pairs)


if __name__ == "__main__":
    unittest.main()
