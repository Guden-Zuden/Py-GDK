import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pygdk as GDK


class TestDockingManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        GDK.init("GUI docking tests", width=240, height=160)

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

    def test_dock_directions_and_fill_use_remaining_area(self):
        manager = GDK.GUI.DockingManager(100, 80)
        left = self.make_box(20, 1)
        top = self.make_box(1, 10)
        right = self.make_box(15, 1)
        bottom = self.make_box(1, 5)
        fill = self.make_box(1, 1)

        manager.dock(left, GDK.GUI.DockingDirection.LEFT)
        manager.dock(top, GDK.GUI.DockingDirection.TOP)
        manager.dock(right, GDK.GUI.DockingDirection.RIGHT)
        manager.dock(bottom, GDK.GUI.DockingDirection.BOTTOM)
        manager.fill(fill)

        self.assertEqual((left.pos.x, left.pos.y), (0, 0))
        self.assertEqual((left.size.width, left.size.height), (20, 80))
        self.assertEqual((top.pos.x, top.pos.y), (20, 0))
        self.assertEqual((top.size.width, top.size.height), (80, 10))
        self.assertEqual((right.pos.x, right.pos.y), (85, 10))
        self.assertEqual((right.size.width, right.size.height), (15, 70))
        self.assertEqual((bottom.pos.x, bottom.pos.y), (20, 75))
        self.assertEqual((bottom.size.width, bottom.size.height), (65, 5))
        self.assertEqual((fill.pos.x, fill.pos.y), (20, 10))
        self.assertEqual((fill.size.width, fill.size.height), (65, 65))

    def test_update_reapplies_layout_without_marking_unchanged_elements_dirty(self):
        manager = GDK.GUI.DockingManager(240, 160)
        left = self.make_box(20, 1)
        fill = self.make_box(1, 1)
        manager.dock(left, GDK.GUI.DockingDirection.LEFT)
        manager.fill(fill)
        left.draw()
        fill.draw()

        manager.update()

        self.assertFalse(left.should_draw())
        self.assertFalse(fill.should_draw())
