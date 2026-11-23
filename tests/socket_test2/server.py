# import socketserver

# class MyTCPHandler(socketserver.BaseRequestHandler):
#     def handle(self):
#         self.data = self.request.recv(1024).strip()
#         print("{} wrote:".format(self.client_address[0]))
#         print(self.data)
#         self.request.sendall(self.data.upper())

# if __name__ == "__main__":
#     HOST, PORT = "localhost", 9999

#     with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
#         server.serve_forever()

import asyncio
import time
from pygdk.Network.temp.utils import ServerManager

server_manager = ServerManager("127.0.0.1", 50000)
server_manager.start()

import pygdk as GDK

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

GDK.init(title="Server", fps=20)
scene = GDK.createScene("main")

sprite = GDK.Sprite()
surf = GDK.pygame.Surface((50,50))
surf.fill((255,0,0))
sprite.sprites.append(surf)

col_layer = GDK.Scene.CollisionLayer()

entity = GDK.Scene.Entity(
    80, 80, 50, 50, 
    GDK.Scene.attachments.MovementModelPhysic(
        400, 50, 400), 
    sprite)
col_layer.attach(entity.make_collision(GDK.ColliderType.SOLID))

camera = GDK.Scene.Camera("main", 0, 0, 0.7)
camera.follow(entity)
scene.attach(camera)
scene.set_camera("main")

scene.attach(entity)
scene.col_manager.push("main", col_layer)

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

GDK.run()