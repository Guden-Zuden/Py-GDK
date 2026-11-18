import os
from pathlib import Path
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pygdk as GDK


class TestGUIDirtyFlags(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        GDK.init("GUI dirty flag tests", width=240, height=160)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        GDK.mouse._pos = GDK.Vec2(10000, 10000)
        GDK.mouse._pressedButton = GDK.mouse.MouseButtonData(
            False, False, False, False, False,
        )
        GDK.GUI.base.Frame._reset_g_flag()
        self.button = GDK.GUI.Button(
            0,
            0,
            64,
            32,
            "Test",
            color=(120, 160, 200),
            border=GDK.Border(0, GDK.colors.WHITE),
            padding=GDK.Padding(0),
        )
        self.button.draw()

    def tearDown(self):
        GDK.mouse._pos = GDK.Vec2(10000, 10000)
        GDK.mouse._pressedButton = GDK.mouse.MouseButtonData(
            False, False, False, False, False,
        )
        GDK.GUI.base.Frame._reset_g_flag()

    def create_all_gui_elements(self):
        padding = GDK.Padding(2)
        border = GDK.Border(0, GDK.colors.WHITE)
        text_style = GDK.TextAttributes("consolas", 14, GDK.colors.WHITE)
        image_path = Path(__file__).resolve().parents[3] / "res" / "image" / "test.png"

        def make_label(text):
            return GDK.GUI.Label(0, 0, text, text_style, padding=padding)

        def make_button(text):
            return GDK.GUI.Button(
                0, 0, 48, 24, text, text_style,
                color=(70, 90, 110), border=border, padding=padding,
            )

        elements = [
            make_label("Label"),
            GDK.GUI.LinkLabel(0, 0, "Link", text_style, padding=padding),
            GDK.GUI.Box(0, 0, 48, 24, (70, 90, 110), padding, border),
            make_button("Button"),
            GDK.GUI.Image(0, 0, image_path, 24, padding, border),
            GDK.GUI.ImageButton(
                0, 0, 48, "ImageButton", text_style,
                image=GDK.GUI.Image(0, 0, image_path, 24, padding, border),
                border=border,
                padding=padding,
            ),
            GDK.GUI.VerticalAlignContainer(
                0, 0, 80, 48, items=[make_button("Vertical")],
                padding=padding, border=border,
            ),
            GDK.GUI.HorizontalAlignContainer(
                0, 0, 80, 48, items=[make_button("Horizontal")],
                padding=padding, border=border,
            ),
            GDK.GUI.GridContainer(
                0, 0, 80, 48, grid_col=1, grid_row=1,
                items=[make_button("Grid")], padding=padding, border=border,
            ),
            GDK.GUI.TabContainer(
                0, 0, 100, 72,
                GDK.Background((50, 60, 70)),
                GDK.Background((80, 90, 100)),
                tab_textAttributes=text_style,
                tab_properties=[
                    GDK.TabProperty("Tab", [make_label("Tab content")]),
                ],
                padding=padding,
                border=border,
            ),
            GDK.GUI.VerticalScrollBar(
                0, 0, GDK.Vec2(120, 90), GDK.Vec2(60, 45),
                padding=padding,
            ),
            GDK.GUI.HorizontalScrollBar(
                0, 0, GDK.Vec2(120, 90), GDK.Vec2(60, 45),
                padding=padding,
            ),
        ]

        toolbar = GDK.GUI.ToolBar(0, 0, text_style, padding=padding, border=border)
        toolbar.push_item(GDK.ToolBarItemProperty("Menu", [("Action", lambda: None)]))
        elements.append(toolbar)
        return elements

    def test_all_gui_elements_follow_dirty_draw_lifecycle(self):
        GDK.mouse._pos = GDK.Vec2(10000, 10000)
        GDK.mouse._pressedButton = GDK.mouse.MouseButtonData(
            False, False, False, False, False,
        )

        for element in self.create_all_gui_elements():
            with self.subTest(element=type(element).__name__):
                GDK.GUI.base.Frame._reset_g_flag()
                element.update()
                element.draw()

                self.assertFalse(element._dirty)
                self.assertFalse(element.size.get_dirty())

                element.set_dirty()
                self.assertTrue(element.should_draw())
                element.draw()
                self.assertFalse(element._dirty)

    def test_draw_clears_dirty_and_size_flags(self):
        self.assertFalse(self.button._dirty)
        self.assertFalse(self.button.size.get_dirty())

        self.button.set_dirty()
        self.assertTrue(self.button.should_draw())
        self.button.draw()
        self.assertFalse(self.button._dirty)

        self.button.size.width += 8
        self.assertTrue(self.button.should_draw())
        self.button.draw()

        self.assertEqual(self.button.surface.get_size(), self.button.size.tuple)
        self.assertEqual(
            self.button._hover_feedback_surface.get_size(),
            self.button.size.tuple,
        )
        self.assertEqual(
            self.button._click_feedback_surface.get_size(),
            self.button.size.tuple,
        )
        self.assertFalse(self.button.size.get_dirty())

    def test_hidden_dirty_button_waits_until_visible_to_draw(self):
        self.button.visible = False
        self.button.set_dirty()

        self.assertFalse(self.button.should_update())
        self.assertFalse(self.button.should_draw())
        self.button.draw()
        self.assertTrue(self.button._dirty)

        self.button.visible = True
        self.assertTrue(self.button.should_draw())
        self.button.draw()
        self.assertFalse(self.button._dirty)

    def test_hover_and_click_feedback_are_separate_and_dynamic(self):
        self.assertIsNot(
            self.button._hover_feedback_surface,
            self.button._click_feedback_surface,
        )
        self.assertEqual(self.button._hover_feedback_surface.get_at((0, 0)).a, 51)
        self.assertEqual(self.button._click_feedback_surface.get_at((0, 0)).a, 102)
        self.assertFalse(self.button.should_draw())

        target = pygame.Surface((240, 160), pygame.SRCALPHA)
        sample_pos = (
            round(self.button.pos.x) + 1,
            round(self.button.pos.y) + 1,
        )

        def render_feedback(hovering, clicking):
            target.fill((0, 0, 0, 0))
            self.button._frame.hovering = hovering
            self.button._frame.clicking = clicking
            self.button._flush_into(target, GDK.Vec2(0, 0))
            return tuple(target.get_at(sample_pos))[:3]

        normal = render_feedback(False, False)
        hovered = render_feedback(True, False)
        clicked = render_feedback(True, True)
        released = render_feedback(False, False)

        self.assertNotEqual(hovered, normal)
        self.assertNotEqual(clicked, hovered)
        self.assertEqual(released, normal)
        self.assertFalse(self.button.should_draw())

    def test_toolbar_is_top_aligned_and_its_buttons_receive_input(self):
        toolbar = GDK.GUI.ToolBar(
            0,
            -1,
            GDK.TextAttributes("consolas", 14, GDK.colors.WHITE),
            padding=GDK.Padding(2),
        )
        toolbar.push_item(
            GDK.ToolBarItemProperty("Menu", [("Action", lambda: None)])
        )
        button = toolbar.HC_ToolBar.items[0]

        self.assertAlmostEqual(toolbar.pos.y, 0)

        GDK.mouse._pos = button.abs_pos + GDK.Vec2(
            button.size.width / 2,
            button.size.height / 2,
        )
        GDK.mouse._pressedButton = GDK.mouse.MouseButtonData(
            True, False, False, False, False,
        )
        GDK.GUI.base.Frame._reset_g_flag()
        toolbar.update()

        self.assertTrue(button._frame.hovering)
        self.assertTrue(button._frame.clicking)

    def test_scrollbar_thumb_tracks_content_scroll(self):
        vertical = GDK.GUI.VerticalScrollBar(
            0, 0, GDK.Vec2(100, 300), GDK.Vec2(20, 60),
            GDK.ScrollBarStyle(width=4),
            GDK.Padding(0),
        )
        horizontal = GDK.GUI.HorizontalScrollBar(
            0, 0, GDK.Vec2(300, 100), GDK.Vec2(60, 20),
            GDK.ScrollBarStyle(width=4),
            GDK.Padding(0),
        )

        vertical.update()
        horizontal.update()
        vertical.draw()
        horizontal.draw()
        initial_vertical = vertical.start_pos.y
        initial_horizontal = horizontal.start_pos.x

        vertical.scroll_v = -30
        horizontal.scroll_h = -30
        vertical.update()
        horizontal.update()

        self.assertGreater(vertical.start_pos.y, initial_vertical)
        self.assertGreater(horizontal.start_pos.x, initial_horizontal)
        self.assertTrue(vertical.should_draw())
        self.assertTrue(horizontal.should_draw())

        vertical.draw()
        horizontal.draw()
        self.assertFalse(vertical._dirty)
        self.assertFalse(horizontal._dirty)

    def test_container_scroll_updates_its_scrollbar_thumb(self):
        container = GDK.GUI.VerticalAlignContainer(
            0,
            0,
            100,
            40,
            items=[
                GDK.GUI.Button(
                    0, 0, 40, 20, f"Item {index}",
                    padding=GDK.Padding(0),
                )
                for index in range(4)
            ],
            padding=GDK.Padding(0),
        )
        container.update()
        scrollbar = container.v_scrollBar_obj
        self.assertIsNotNone(scrollbar)
        assert scrollbar is not None
        initial_thumb_position = scrollbar.start_pos.y

        container.on_mousewheelscroll(type("WheelEvent", (), {"y": -10})())
        container.update()

        self.assertLess(container.scroll_v, 0)
        self.assertGreater(scrollbar.start_pos.y, initial_thumb_position)
        self.assertTrue(scrollbar.should_draw())

    def test_alignment_containers_support_optional_borders(self):
        padding = GDK.Padding(0)
        text_style = GDK.TextAttributes("consolas", 14, GDK.colors.WHITE)

        def make_label(text):
            return GDK.GUI.Label(0, 0, text, text_style, padding=padding)

        vertical_item = make_label("Vertical")
        vertical = GDK.GUI.VerticalAlignContainer(
            0, 0, 100, 40,
            items=[vertical_item],
            padding=padding,
            border=None,
        )

        horizontal_item = make_label("Horizontal")
        horizontal = GDK.GUI.HorizontalAlignContainer(
            0, 0, 100, 40,
            items=[horizontal_item],
            padding=padding,
            border=None,
        )

        grid_item = make_label("Grid")
        grid = GDK.GUI.GridContainer(
            0, 0, 100, 40,
            grid_col=1,
            grid_row=1,
            items=[grid_item],
            padding=padding,
            border=None,
        )

        self.assertIs(vertical.items[0], vertical_item)
        self.assertIs(horizontal.items[0], horizontal_item)
        self.assertIs(grid.items[0], grid_item)
        self.assertEqual(vertical_item.pos.tuple, (0, 0))
        self.assertEqual(horizontal_item.pos.tuple, (0, 0))
        self.assertEqual(grid_item.pos.tuple, (0, 0))


if __name__ == "__main__":
    unittest.main()
