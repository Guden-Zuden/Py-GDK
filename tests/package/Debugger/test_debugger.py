import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pygdk as GDK


class TestDebugger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        GDK.init("Debugger tests", width=640, height=480)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.layer_stack = GDK.layer.LayerManager.layer_stack
        self.current_layer = GDK.layer.LayerManager.current_layer
        self.scene_stack = GDK.scene.SceneManager.scene_stack
        self.current_scene = GDK.scene.SceneManager.current_scene
        GDK.layer.LayerManager.layer_stack = {}
        GDK.layer.LayerManager.current_layer = None
        GDK.scene.SceneManager.scene_stack = {}
        GDK.scene.SceneManager.current_scene = None

    def tearDown(self):
        GDK.layer.LayerManager.layer_stack = self.layer_stack
        GDK.layer.LayerManager.current_layer = self.current_layer
        GDK.scene.SceneManager.scene_stack = self.scene_stack
        GDK.scene.SceneManager.current_scene = self.current_scene

    @staticmethod
    def make_box(width=40, height=20):
        return GDK.GUI.Box(
            0, 0, width, height, (50, 80, 110),
            GDK.Padding(0),
            GDK.Border(0, GDK.colors.WHITE),
        )

    def test_gui_debugger_refreshes_nested_component_tree(self):
        layer = GDK.layer.Layer()
        GDK.layer.LayerManager.pushLayer("main", layer)

        parent = self.make_box()
        child = self.make_box(10, 10)
        parent.set_child(child)
        layer.attach(parent)
        debugger = GDK.Debugger.GUIDebugger(layer)

        self.assertIn("abs=", debugger._format_component((0, parent)))
        self.assertEqual(len(debugger.TP_GUI_components.items), 2)
        debugger.update()
        self.assertEqual(len(debugger.TP_GUI_components.items), 2)

        layer.attach(self.make_box(12, 12))
        debugger.update()

        self.assertEqual(len(debugger.TP_GUI_components.items), 3)

    def test_scene_debugger_tracks_active_scene_and_entities(self):
        layer = GDK.layer.Layer()
        scene = GDK.scene.Scene()
        GDK.scene.SceneManager.push_scene("main", scene)
        debugger = GDK.Debugger.SceneDebugger(layer)

        self.assertEqual(debugger._entity_rows(), ["No entities"])

        entity = GDK.Scene.EntityBase(10, 20, 30, 40)
        scene._entity_stack.append(entity)
        camera = GDK.Scene.Camera("main", 100, 200)
        scene._camera_stack[camera.name] = camera
        scene.current_camera = camera
        collision_layer = GDK.Scene.CollisionLayer()
        collision_layer.attach(GDK.Scene.Collider(entity))
        scene.col_manager.push("solid", collision_layer)
        GDK.scene.SceneManager.current_scene = scene

        debugger.update()
        debugger.TP_scenes.items[0].on_update()
        debugger.TP_world.items[0].on_update()

        self.assertEqual(len(debugger.TP_entities.items), 1)
        entity_row = debugger.TP_entities.items[0]
        world_row = debugger.TP_world.items[0]
        scene_row = debugger.TP_scenes.items[0]
        assert isinstance(entity_row, GDK.GUI.Label)
        assert isinstance(world_row, GDK.GUI.Label)
        assert isinstance(scene_row, GDK.GUI.Label)
        self.assertIn("pos=(10, 20)", entity_row._text)
        self.assertIn("colliders=1", world_row._text)
        self.assertIn("* main", scene_row._text)

        scene._entity_stack.append(GDK.Scene.EntityBase(50, 60, 10, 10))
        debugger.update()
        self.assertEqual(len(debugger.TP_entities.items), 2)

    def test_scene_debugger_skips_refresh_for_inactive_entity_tab(self):
        layer = GDK.layer.Layer()
        scene = GDK.scene.Scene()
        debugger = GDK.Debugger.SceneDebugger(layer, scene)
        entity = GDK.Scene.EntityBase(10, 20, 30, 40)
        scene._entity_stack.append(entity)

        with patch.object(GDK.GUI.TabContainer, "update"):
            debugger.Scene_Container.update()
        entity_row = debugger.TP_entities.items[0]
        assert isinstance(entity_row, GDK.GUI.Label)
        self.assertEqual(entity_row._text, "No entities")

        debugger.Scene_Container.current_tabIndex = 1
        with patch.object(GDK.GUI.TabContainer, "update"):
            debugger.Scene_Container.update()
        entity_row = debugger.TP_entities.items[0]
        assert isinstance(entity_row, GDK.GUI.Label)
        self.assertIn("EntityBase", entity_row._text)


if __name__ == "__main__":
    unittest.main()
