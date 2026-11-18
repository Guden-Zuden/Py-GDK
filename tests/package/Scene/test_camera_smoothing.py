import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pygdk as GDK
from pygdk import time as gdk_time


class TestCameraSmoothing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        GDK.init("Camera tests", width=640, height=480)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.original_dt = gdk_time.dt
        self.target = GDK.Scene.Entity(
            100,
            50,
            20,
            20,
            GDK.Scene.attachments.MovementModelPhysic(0, 0, 0),
            GDK.Sprite(),
        )

    def tearDown(self):
        gdk_time.dt = self.original_dt

    def get_position_after(self, frame_count, frame_dt, smoothing=0.01):
        camera = GDK.Scene.Camera("test", 0, 0, smoothing)
        camera.follow(self.target)

        gdk_time.dt = frame_dt
        for _ in range(frame_count):
            camera.update()

        return camera.pos

    def test_smoothing_is_independent_of_frame_rate(self):
        at_60_fps = self.get_position_after(60, 1 / 60)
        at_30_fps = self.get_position_after(30, 1 / 30)

        self.assertAlmostEqual(at_60_fps.x, at_30_fps.x)
        self.assertAlmostEqual(at_60_fps.y, at_30_fps.y)

    def test_smoothing_zero_and_one_keep_their_boundary_behavior(self):
        no_smoothing = self.get_position_after(1, 1 / 60, smoothing=0)
        immediate_follow = self.get_position_after(1, 1 / 60, smoothing=1)

        self.assertEqual(no_smoothing.tuple, (0, 0))
        self.assertEqual(immediate_follow.tuple, self.target.pos.tuple)


if __name__ == "__main__":
    unittest.main()
