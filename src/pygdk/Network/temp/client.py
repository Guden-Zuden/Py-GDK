import asyncio

from logging import getLogger
logger = getLogger(__name__)

from .connection import UDPProtocol

class NetworkClient:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

        self.transport: asyncio.DatagramTransport | None = None
        self.recv_queue: asyncio.Queue[tuple[bytes, tuple[str, int]]] = asyncio.Queue()
        self._connected = False

    async def connect(self):
        if self._connected:
            return
        loop = asyncio.get_running_loop()

        self.transport, _ = await loop.create_datagram_endpoint(
            lambda: UDPProtocol(self.recv_queue),
            remote_addr=(self.host, self.port)
        )
        self._connected = True

    async def send(self, data: bytes):
        if self.transport is None:
            logger.error(f"Failed to send data: No connection.")
            return
        self.transport.sendto(data)

    async def receive(self):
        return await self.recv_queue.get()

    async def close(self):
        if self.transport is not None:
            self.transport.close()
            self.transport = None
        self._connected = False