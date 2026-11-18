import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pygdk as GDK


class TestTextBaseline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        GDK.init("GUI text baseline tests", width=320, height=160)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_label_baseline_is_independent_of_glyph_bounds(self):
        text_style = GDK.TextAttributes("consolas", 18, GDK.colors.WHITE)
        labels = [
            GDK.GUI.Label(0, 0, text, text_style, padding=GDK.Padding(0))
            for text in ("H", "gyp")
        ]

        for label in labels:
            label.draw()
            self.assertAlmostEqual(
                label._get_baseline_offset(),
                label.font.get_ascent(),
            )

        self.assertAlmostEqual(
            labels[0]._get_baseline_offset(),
            labels[1]._get_baseline_offset(),
        )

    def test_horizontal_container_aligns_button_text_baselines(self):
        padding = GDK.Padding(0)
        buttons = [
            GDK.GUI.Button(
                0,
                0,
                80,
                40,
                "gyp",
                GDK.TextAttributes(font, 18, GDK.colors.WHITE),
                padding=padding,
            )
            for font in ("consolas", "msgothic")
        ]
        container = GDK.GUI.HorizontalAlignContainer(
            0,
            0,
            220,
            60,
            items=buttons,
            padding=padding,
        )

        self.assertIs(buttons[0].parent, container)
        baselines = [
            button.pos.y + button._get_baseline_offset()
            for button in buttons
        ]
        self.assertAlmostEqual(baselines[0], baselines[1])

    def test_label_reuses_text_rendering_for_non_text_changes(self):
        label = GDK.GUI.Label(
            0,
            0,
            "cached",
            GDK.TextAttributes(
                "consolas",
                18,
                GDK.colors.WHITE,
                OutlineWidth=1,
                OutlineColor=GDK.colors.BLACK,
            ),
            padding=GDK.Padding(0),
        )
        label.draw()

        render_count = 0
        create_cache = label._create_text_cache

        def count_cache_creations(textAttributes):
            nonlocal render_count
            render_count += 1
            return create_cache(textAttributes)

        label._create_text_cache = count_cache_creations
        label.set_dirty()
        label.draw()
        self.assertEqual(render_count, 0)

        label.set_text("updated")
        label.draw()
        self.assertEqual(render_count, 1)

        label._textAttributes.TextColor = (255, 0, 0)
        label.draw()
        self.assertEqual(render_count, 2)

    def test_label_update_does_not_dirty_unchanged_root_position(self):
        label = GDK.GUI.Label(
            0,
            0,
            "stable",
            GDK.TextAttributes("consolas", 18, GDK.colors.WHITE),
            padding=GDK.Padding(0),
        )
        label.draw()

        GDK.mouse._pos = GDK.Vec2(10000, 10000)
        GDK.GUI.base.Frame._reset_g_flag()
        label.update()

        self.assertFalse(label.should_draw())

    def test_link_label_switches_text_cache_on_hover_changes(self):
        normal_style = GDK.TextAttributes("consolas", 18, GDK.colors.WHITE)
        hovered_style = GDK.TextAttributes("consolas", 18, (0, 255, 255))
        label = GDK.GUI.LinkLabel(
            0,
            0,
            "link",
            normal_style,
            hovered_textAttributes=hovered_style,
            padding=GDK.Padding(0),
        )
        label.draw()

        GDK.mouse._pos = label.abs_pos + GDK.Vec2(
            label.size.width / 2,
            label.size.height / 2,
        )
        GDK.GUI.base.Frame._reset_g_flag()
        label.update()
        self.assertTrue(label._frame.hovering)
        label.draw()
        self.assertIs(label._rendered_attributes, hovered_style)

        GDK.mouse._pos = GDK.Vec2(10000, 10000)
        GDK.GUI.base.Frame._reset_g_flag()
        label.update()
        self.assertFalse(label._frame.hovering)
        label.draw()
        self.assertIs(label._rendered_attributes, normal_style)


if __name__ == "__main__":
    unittest.main()
