import asyncio
from typing import Any

from logging import getLogger
logger = getLogger(__name__)

class UDPProtocol(asyncio.DatagramProtocol):
    def __init__(self, recv_queue: asyncio.Queue) -> None:
        self.recv_queue = recv_queue
        self.transport: asyncio.DatagramTransport | None = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        self.recv_queue.put_nowait((data, addr))

    def error_received(self, exc: Exception) -> None:
        logger.error(f"UDP Error: {exc}")

    def connection_lost(self, exc: Exception | None) -> None:
        if exc: logger.error(f"Lost the connection: {exc}")
        self.transport = None