import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pygdk as GDK


class TestElementStick(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        GDK.init("GUI stick tests", width=240, height=160)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    @staticmethod
    def make_box(width, height):
        return GDK.GUI.Box(
            0, 0, width, height, (70, 90, 110),
            GDK.Padding(0),
            GDK.Border(0, GDK.colors.WHITE),
        )

    def test_stick_tracks_target_position_and_size_changes(self):
        target = self.make_box(20, 10)
        follower = self.make_box(8, 6)
        follower.stick(target, GDK.Direction.RIGHTBOTTOM)

        target.pos = GDK.Vec2(50, 60)
        target.size = GDK.Vec2(40, 20)
        with patch.object(follower._frame, "update"):
            follower.update()

        self.assertEqual(
            follower.pos.tuple,
            (target.pos.x + target.size.width, target.pos.y + target.size.height),
        )

    def test_stick_tracks_viewport_resize_for_root_target(self):
        target = self.make_box(20, 10)
        target.u = 0.5
        target.v = -0.25
        follower = self.make_box(8, 6)
        follower.stick(target, GDK.Direction.BOTTOM)

        with patch.object(GDK.profile, "width", 480), patch.object(GDK.profile, "height", 320):
            with patch.object(follower._frame, "update"):
                follower.update()
            target_y = 320 / 2 + 320 / 2 * target.v - target.size.height / 2

        self.assertEqual(follower.pos.y, target_y + target.size.height)

    def test_stick_converts_coordinates_between_parents(self):
        parent_a = self.make_box(100, 100)
        parent_b = self.make_box(100, 100)
        target = self.make_box(20, 10)
        follower = self.make_box(8, 4)
        parent_a.pos = GDK.Vec2(10, 20)
        parent_b.pos = GDK.Vec2(100, 40)
        parent_a.set_child(target)
        parent_b.set_child(follower)
        target.pos = GDK.Vec2(5, 6)

        follower.stick(target, GDK.Direction.RIGHT)

        self.assertEqual(follower.abs_pos.tuple, (35, 29))

    def test_stick_rejects_cycles(self):
        first = self.make_box(10, 10)
        second = self.make_box(10, 10)
        first.stick(second, GDK.Direction.RIGHT)

        with self.assertRaises(ValueError):
            second.stick(first, GDK.Direction.RIGHT)
