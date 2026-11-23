from typing import Optional
from time import perf_counter

from logging import getLogger
logger = getLogger(__name__)

from pygdk import profile as _profile
from pygdk import time as _time
from ... import (
    scene as _scene,
    Scene as _Scene,
)
from . import server
from . import client

from ..protocol.gen import client_pb2
from ..protocol.gen import scene_pb2
from ..protocol.gen import common_pb2

SCENE_STATE_MAGIC = b"PGDK"

def pack_scene_state(state: scene_pb2.SceneState) -> bytes:
    return SCENE_STATE_MAGIC + state.SerializeToString()

def parse_scene_state(data: bytes) -> scene_pb2.SceneState:
    if not data.startswith(SCENE_STATE_MAGIC):
        raise ValueError("Invalid SceneState packet")
    state = scene_pb2.SceneState()
    state.ParseFromString(data[len(SCENE_STATE_MAGIC):])
    return state

class SceneHost:
    def __init__(self, host_ip: str, port: int) -> None:        
        self.target_scenes: list[_scene.Scene] = []

        self.clients_data: dict[tuple[str, int], client_pb2.ClientState] = {}
        self.server = server.NetworkServer(host_ip, port)

    def push_scene(self, scene: _scene.Scene):
        self.target_scenes.append(scene)

    async def receive_from_client(self):
        data, addr = await self.server.receive()
        logger.debug("Received %d bytes from %s:%d", len(data), addr[0], addr[1])

        parsed_data = client_pb2.ClientState()
        try:
            parsed_data.ParseFromString(data)
        except Exception as exc:
            logger.warning("Invalid ClientState from %s:%d: %s", addr[0], addr[1], exc)
            return None

        if not parsed_data.curr_scene_name:
            logger.warning("ClientState from %s:%d has no scene name", addr[0], addr[1])
            return None
        if parsed_data.curr_scene_name not in _scene.SceneManager.scene_stack:
            logger.warning(
                "Unknown scene %r requested by %s:%d",
                parsed_data.curr_scene_name,
                addr[0],
                addr[1],
            )
            return None

        address = (addr[0], addr[1])
        if address not in self.clients_data:
            logger.info("New client: %s:%d", addr[0], addr[1])
        self.clients_data[address] = parsed_data
        return address

    def send_to_client(self, addr):
        client_data = self.clients_data.get(addr)
        if client_data is None:
            return

        curr_scene = _scene.SceneManager.scene_stack.get(client_data.curr_scene_name)
        if curr_scene is None:
            logger.warning("Unknown scene %r for client %s:%d", client_data.curr_scene_name, addr[0], addr[1])
            return

        entity_states: list[scene_pb2.EntityState] = []

        for i, entity in enumerate(curr_scene._entity_stack):
            if not isinstance(entity, _Scene.EntityBase):
                continue

            current_anim = ""
            anim_index = 0
            if isinstance(entity, _Scene.Entity) and entity.animator is not None:
                if entity.animator.current_anim is not None:
                    current_anim = next(
                        (
                            name
                            for name, anim_data in entity.animator.anim_datas.items()
                            if anim_data is entity.animator.current_anim
                        ),
                        "",
                    )
                    anim_index = entity.animator.current_anim.current_index

            movement_velocity = getattr(
                getattr(entity, "movement_model", None),
                "velocity",
                entity.velocity,
            )

            logger.info(
                "SERVER send scene=%s entity=%d pos=(%s, %s) velocity=(%s, %s)",
                client_data.curr_scene_name,
                i,
                entity.pos.x,
                entity.pos.y,
                movement_velocity.x,
                movement_velocity.y,
            )

            entity_states.append(
                scene_pb2.EntityState(
                    type=entity.TYPE,
                    id=i,
                    position=common_pb2.Vec2f(
                        x=entity.pos.x,
                        y=entity.pos.y,
                    ),
                    velocity=common_pb2.Vec2f(
                        x=movement_velocity.x,
                        y=movement_velocity.y,
                    ),
                    current_anim=current_anim,
                    anim_index=anim_index,
                )
            )

        data = pack_scene_state(
            scene_pb2.SceneState(entitystates=entity_states)
        )
        logger.debug("Sending %d bytes to %s:%d", len(data), addr[0], addr[1])
        self.server.send(data, addr)

class SceneClient:
    def __init__(self, host_ip: str, port: int) -> None:
        self.scenes: list[_scene.Scene] = []
        self.current_scene: Optional[_scene.Scene] = None
        self.client_manager = client.NetworkClient(host_ip, port)
        self._remote_scene: Optional[_scene.Scene] = None
        self._remote_states: dict[int, tuple[float, float, float, float, float]] = {}

    async def receive_from_host(self) -> scene_pb2.SceneState | None:
        data, addr = await self.client_manager.receive()
        logger.info("CLIENT received %d bytes from host %s:%d", len(data), addr[0], addr[1])
        try:
            parsed_data = parse_scene_state(data)
        except Exception as exc:
            logger.warning("Invalid SceneState from %s:%d: %s", addr[0], addr[1], exc)
            return None
        return parsed_data

    async def send_to_host(self):
        if _scene.SceneManager.current_scene is None:
            logger.warning(f"current scene is None.")
            return
        data = client_pb2.ClientState(
            curr_scene_name=next((k for k, v in _scene.SceneManager.scene_stack.items() if v == _scene.SceneManager.current_scene), ""),
            view_position=common_pb2.Vec2f(
                x=_scene.SceneManager.current_scene.view_position.x, 
                y=_scene.SceneManager.current_scene.view_position.y
            ),
            view_size=common_pb2.Vec2i(
                x=_profile.width, 
                y=_profile.height
            )
        ).SerializeToString()

        await self.client_manager.send(data)

    async def request_scene_sync(self) -> scene_pb2.SceneState | None:
        await self.send_to_host()
        return await self.receive_from_host()

    def apply_scene_state(self, parsed_data: scene_pb2.SceneState) -> None:
        current_scene = _scene.SceneManager.current_scene
        if current_scene is None:
            logger.info("CLIENT apply skipped: no current scene")
            return
        if current_scene is not self._remote_scene:
            self._remote_scene = current_scene
            self._remote_states.clear()

        remote_entities = list(parsed_data.entitystates)
        logger.info(
            "CLIENT apply scene=%s remote_entities=%d local_entities=%d",
            next(
                (
                    name
                    for name, scene in _scene.SceneManager.scene_stack.items()
                    if scene is current_scene
                ),
                "",
            ),
            len(remote_entities),
            len(current_scene._entity_stack),
        )
        while len(current_scene._entity_stack) < len(remote_entities):
            from pygdk import Sprite
            sprite = Sprite()
            surf = _Scene.entity._pg.Surface((50, 50))
            surf.fill((0, 0, 50))
            sprite.sprites.append(surf)
            current_scene._entity_stack.append(
                _Scene.Entity(
                    0,
                    0,
                    50,
                    50,
                    _Scene.attachments.MovementModelMob(0, 0, 0),
                    sprite,
                )
            )
        del current_scene._entity_stack[len(remote_entities):]

        for entity, entity_data in zip(current_scene._entity_stack, remote_entities):
            entity.velocity.x = entity_data.velocity.x
            entity.velocity.y = entity_data.velocity.y
            self._remote_states[entity_data.id] = (
                entity_data.position.x,
                entity_data.position.y,
                entity_data.velocity.x,
                entity_data.velocity.y,
                perf_counter(),
            )

    def update_interpolation(self, delta_time: float) -> None:
        current_scene = _scene.SceneManager.current_scene
        if current_scene is None or current_scene is not self._remote_scene:
            return

        delta_time = max(0.0, min(delta_time, 0.1))
        if delta_time == 0:
            return

        blend = min(1.0, delta_time * 12.0)
        now = perf_counter()
        for entity_id, state in self._remote_states.items():
            if entity_id >= len(current_scene._entity_stack):
                continue

            entity = current_scene._entity_stack[entity_id]
            x, y, velocity_x, velocity_y, received_at = state
            elapsed = min(now - received_at, 0.25)
            target_x = x + velocity_x * elapsed
            target_y = y + velocity_y * elapsed
            entity.pos.x += (target_x - entity.pos.x) * blend
            entity.pos.y += (target_y - entity.pos.y) * blend

    async def connect(self): await self.client_manager.connect()
    async def close(self): await self.client_manager.close()
