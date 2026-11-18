from pathlib import Path

import pygdk as GDK


ROOT = Path(__file__).resolve().parents[3]
IMAGE_PATH = ROOT / "res" / "image" / "test.png"

GDK.profile.resizable = True
GDK.profile.surface_fill_screen = True
GDK.init("Py-GDK GUI gallery", fps=60, width=1200, height=900)

layer = GDK.createLayer("gui-gallery")
title_style = GDK.TextAttributes("consolas", 24, GDK.colors.WHITE)
text_style = GDK.TextAttributes("consolas", 16, GDK.colors.WHITE)
hover_style = GDK.TextAttributes("consolas", 16, (0, 255, 255))

toolbar = GDK.GUI.ToolBar(
    0,
    -1,
    text_style,
    GDK.Background(GDK.Color(55, 65, 80)),
    GDK.Background(GDK.Color(75, 85, 100)),
    space=8,
)
toolbar.push_item(
    GDK.ToolBarItemProperty(
        "File",
        [
            ("New", lambda: print("File / New")),
            ("Open", lambda: print("File / Open")),
        ],
    )
)
toolbar.push_item(
    GDK.ToolBarItemProperty(
        "Help",
        [("Print help", lambda: print("GUI gallery: click controls to test them"))],
    )
)
layer.attach(toolbar)

layer.attach(GDK.GUI.Label(0, -0.86, "Py-GDK GUI gallery", title_style))

layer.attach(GDK.GUI.Label(-0.82, -0.68, "Label", text_style))
layer.attach(
    GDK.GUI.LinkLabel(
        -0.48,
        -0.68,
        "LinkLabel (hover me)",
        text_style,
        hovered_textAttributes=hover_style,
    )
)
layer.attach(GDK.GUI.Box(-0.78, -0.48, 100, 54, GDK.colors.RED))
layer.attach(
    GDK.GUI.Button(
        -0.42,
        -0.48,
        150,
        54,
        "Button",
        text_style,
        color=(60, 110, 190),
        callback_clicked=lambda: print("Button clicked"),
    )
)
layer.attach(
    GDK.GUI.Image(
        -0.05,
        -0.48,
        IMAGE_PATH,
        110,
    )
)
layer.attach(
    GDK.GUI.ImageButton(
        0.35,
        -0.48,
        140,
        "ImageButton",
        text_style,
        image=GDK.GUI.Image(0, 0, IMAGE_PATH, 140),
        callback_clicked=lambda: print("ImageButton clicked"),
    )
)

vertical_items = [
    GDK.GUI.Button(
        0,
        0,
        170,
        34,
        f"Vertical item {index + 1}",
        text_style,
        color=(50 + index * 8, 75, 105),
    )
    for index in range(8)
]
vertical_container = GDK.GUI.VerticalAlignContainer(
    -0.66,
    0.12,
    250,
    300,
    background=GDK.Background(GDK.Color(35, 40, 50)),
    items=vertical_items,
    space=6,
    padding=GDK.Padding(8),
    border=GDK.Border(1, GDK.colors.WHITE),
)
layer.attach(vertical_container)

horizontal_container = GDK.GUI.HorizontalAlignContainer(
    0,
    0.12,
    350,
    100,
    background=GDK.Background(GDK.Color(35, 40, 50)),
    items=[
        GDK.GUI.Button(
            0,
            0,
            105,
            40,
            f"Item {index + 1}",
            text_style,
            color=(55, 95, 140),
        )
        for index in range(5)
    ],
    space=8,
    padding=GDK.Padding(8),
    border=GDK.Border(1, GDK.colors.WHITE),
)
layer.attach(horizontal_container)

grid_container = GDK.GUI.GridContainer(
    0.68,
    0.12,
    270,
    300,
    background=GDK.Background(GDK.Color(35, 40, 50)),
    grid_col=3,
    grid_row=3,
    items=[
        GDK.GUI.Button(
            0,
            0,
            72,
            40,
            f"{index + 1}",
            text_style,
            color=(65, 85 + index * 5, 120),
        )
        for index in range(9)
    ],
    space=8,
    padding=GDK.Padding(8),
    border=GDK.Border(1, GDK.colors.WHITE),
)
layer.attach(grid_container)

tabs = GDK.GUI.TabContainer(
    -0.48,
    0.72,
    400,
    190,
    tab_background=GDK.Background(GDK.Color(55, 65, 80)),
    selected_tab_background=GDK.Background(GDK.Color(75, 105, 150)),
    tabitems_background=GDK.Background(GDK.Color(35, 40, 50)),
    tab_textAttributes=text_style,
    tab_properties=[
        GDK.TabProperty(
            "First",
            [GDK.GUI.Label(0, 0, f"First tab content {index + 1}", text_style) for index in range(4)],
        ),
        GDK.TabProperty(
            "Second",
            [GDK.GUI.Button(0, 0, 180, 36, "Second tab button", text_style, color=(70, 100, 140))],
        ),
    ],
    padding=GDK.Padding(8),
    border=GDK.Border(1, GDK.colors.WHITE),
)
layer.attach(tabs)

bar_style = GDK.ScrollBarStyle(width=10, color=(0, 255, 255), rounded=True)
layer.attach(
    GDK.GUI.HorizontalScrollBar(
        0.52,
        0.58,
        GDK.Vec2(600, 18),
        GDK.Vec2(280, 18),
        bar_style,
    )
)
layer.attach(
    GDK.GUI.VerticalScrollBar(
        0.93,
        0.58,
        GDK.Vec2(18, 600),
        GDK.Vec2(18, 180),
        bar_style,
    )
)

GDK.run()
