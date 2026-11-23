import asyncio
import logging

from pygdk import time as _time
from .scene import SceneHost, SceneClient
from .thread import NetworkThread

from ..protocol.gen import scene_pb2

logger = logging.getLogger(__name__)

class ServerManager:
    def __init__(self, ip: str, port: int) -> None:
        self.scene_host = SceneHost(ip, port)

        self.thread = NetworkThread()

        self.stop_flag = False
        self._started = False

    def start(self):
        if self._started:
            return
        self.thread.start()
        self.thread.submit(self.scene_host.server.start()).result()
        self.thread.submit(self._loop())
        self._started = True

    def stop(self):
        if not self._started:
            return
        self.stop_flag = True
        self._started = False
        self.thread.loop.call_soon_threadsafe(self.scene_host.server.close)
        self.thread.stop()

    async def _loop(self):
        while not self.stop_flag:
            try:
                addr = await self.scene_host.receive_from_client()
                if addr is not None:
                    self.scene_host.send_to_client(addr)
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Server network loop failed")

class ClientManager:
    def __init__(self, host_ip: str, port: int) -> None:
        self.scene_client = SceneClient(host_ip, port)

        self.thread = NetworkThread()
        self.thread.start()
        self._connected = False
        self._closed = False
        self.pending_scene_state: scene_pb2.SceneState | None = None
        self._sync_future = None

    def connect(self): 
        if self._connected or self._closed:
            return
        self.thread.submit(self.scene_client.connect()).result()
        self._connected = True

    def request_scene_sync(self):
        if not self._connected or self._closed:
            logger.info("SYNC skipped connected=%s closed=%s", self._connected, self._closed)
            return
        if self._sync_future is not None:
            if not self._sync_future.done():
                return
            self._collect_scene_sync_result()
            if self.pending_scene_state is not None:
                return
        if self.pending_scene_state is not None:
            return
        self._sync_future = self.thread.submit(self.scene_client.request_scene_sync())
        logger.info("SYNC request submitted")

    def apply_pending_scene_state(self):
        if self._sync_future is not None and self._sync_future.done():
            self._collect_scene_sync_result()

        state = self.pending_scene_state
        if state is None:
            self.scene_client.update_interpolation(_time.dt)
            return
        self.pending_scene_state = None
        self.scene_client.apply_scene_state(state)
        self.scene_client.update_interpolation(_time.dt)

    def _collect_scene_sync_result(self):
        future = self._sync_future
        if future is None or not future.done():
            return
        self._sync_future = None
        try:
            self.pending_scene_state = future.result()
            logger.info(
                "SYNC response completed state=%s",
                self.pending_scene_state is not None,
            )
        except asyncio.CancelledError:
            logger.info("SYNC response cancelled")
        except Exception:
            logger.exception("Scene synchronization request failed")

    def close(self):
        if self._closed:
            return
        self.thread.submit(self.scene_client.close()).result()
        self.thread.stop()
        self._closed = True