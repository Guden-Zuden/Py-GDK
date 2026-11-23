import asyncio
import threading

class NetworkThread:
    def __init__(self) -> None:
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="PyGDK-Network",
        )
        self._started = False
        self._stopped = False

    def _run(self):
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()

    def start(self):
        if self._started:
            return
        self.thread.start()
        self._started = True

    def submit(self, coro: asyncio._CoroutineLike):
        if not self._started or self._stopped:
            raise RuntimeError("NetworkThread is not running")
        return asyncio.run_coroutine_threadsafe(
            coro, self.loop
        )

    def stop(self):
        if not self._started or self._stopped:
            return
        self._stopped = True
        if threading.current_thread() is not self.thread:
            asyncio.run_coroutine_threadsafe(
                self._cancel_all_tasks(),
                self.loop,
            ).result(timeout=5)
        self.loop.call_soon_threadsafe(self.loop.stop)
        if threading.current_thread() is not self.thread:
            self.thread.join(timeout=5)

    async def _cancel_all_tasks(self):
        tasks = [
            task
            for task in asyncio.all_tasks(self.loop)
            if task is not asyncio.current_task()
        ]
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)