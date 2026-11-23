import asyncio
from typing import Optional

from logging import getLogger
logger = getLogger(__name__)

from .connection import UDPProtocol

class NetworkServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

        self.transport: Optional[asyncio.DatagramTransport] = None
        self.recv_queue: asyncio.Queue[tuple[bytes, tuple[str, int]]] = asyncio.Queue()
        self._started = False

    async def start(self):
        if self._started:
            return
        loop = asyncio.get_running_loop()

        self.transport, _ = await loop.create_datagram_endpoint(
            lambda: UDPProtocol(self.recv_queue),
            local_addr=(self.host, self.port)
        )
        self._started = True

    async def receive(self):
        return await self.recv_queue.get()

    def send(self, data: bytes, addr):
        if self.transport is None:
            logger.error(f"Failed to send data: No connection.")
            return
            
        self.transport.sendto(data, addr)

    def close(self):
        if self.transport is not None:
            self.transport.close()
            self.transport = None
        self._started = False