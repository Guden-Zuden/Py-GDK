# PyGDK (Game Developer Kits in Python)
Japanese(日本語)
## 概要
PyGDKは、pygameを使用し、ゲームを作成する際のツールです。
このプロジェクトはPygame (LGPL license) を使用しています。
srcフォルダに入っているものがPyGDK本体です。

## 簡単な説明 (2026/08/21更新)
```py
import src as GDK # お好きなようにインポート

GDK.init() # 初期化

layer = GDK.createLayer() # まず、レイヤーの作成を行います。

# GUIオブジェクトなどの作成
box = GDK.GUI.Box(0.0, 0.0, 80, 80, (255, 70, 70))
layer.attach(box) # GUIオブジェクトをレイヤーにアタッチ。

# イベントの作成
@GDK.event.OnKeydown(GDK.key.d) # OnUpdate以外は引数にpygame.event.Eventが必要です。
def on_keydown(e):
    global box
    box.pos.x += 1

GDK.run() # 実行
```

---

English(英語)
## About
PyGDK is a library for creating games using Pygame.
This project uses Pygame, which is licensed under the LGPL.
The PyGDK itself is contained in the src folder.

## Brief description (Updated on August 21, 2026)
```py
import src as GDK # Import the package however you like.

GDK.init() # Initialization

layer = GDK.createLayer() # First of all, create the layer.

# Create GUI Objects.
box = GDK.GUI.Box(0.0, 0.0, 80, 80, (255, 70, 70))
layer.attach(box) # Attach the GUI object to the layer.

# Register an event handler
@GDK.event.OnKeydown(GDK.key.d) # An argument of the type `pygame.event.Event` is required for all event handlers except `OnUpdate`.
def on_keydown(e):
    global box
    box.pos.x += 1

GDK.run() # Run the application
```