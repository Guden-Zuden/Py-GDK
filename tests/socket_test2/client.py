# import socket
# import sys

# HOST, PORT = "localhost", 9999
# data = " ".join(sys.argv[1:])

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
#     sock.connect((HOST, PORT))
#     sock.sendall(bytes(data + "\n", "utf-8"))
#     received = str(sock.recv(1024), "utf-8")

# print("Sent:     {}".format(data))
# print("Received: {}".format(received))

import asyncio
from pygdk.Network.temp.utils import ClientManager
import pygdk as GDK

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

client_manager = ClientManager("127.0.0.1", 50000)

GDK.init(title="Client")
scene = GDK.createScene("main")

sprite = GDK.Sprite()
surf = GDK.pygame.Surface((50,50))
surf.fill((255,0,0))
sprite.sprites.append(surf)

entity = GDK.Scene.Entity(
    80, 80, 50, 50, 
    GDK.Scene.attachments.MovementModelPhysic(
        400, 50, 400), 
    sprite)

scene.attach(entity)

client_manager.connect()

scene = GDK.createScene("sub")

sprite = GDK.Sprite()
surf = GDK.pygame.Surface((50,50))
surf.fill((255,0,0))
sprite.sprites.append(surf)

entity = GDK.Scene.Entity(
    80, 80, 50, 50, 
    GDK.Scene.attachments.MovementModelPhysic(
        400, 300, 400), 
    sprite)

scene.attach(entity)


@GDK.event.OnUpdate()
def on_update():
    client_manager.request_scene_sync()
    client_manager.apply_pending_scene_state()

@GDK.event.OnKeydown(GDK.key.F1)
def on_keydown(e):
    GDK.scene.SceneManager.change_scene("sub")

@GDK.event.OnKeydown(GDK.key.F2)
def on_keydown(e):
    GDK.scene.SceneManager.change_scene("main")

GDK.run()
client_manager.close()