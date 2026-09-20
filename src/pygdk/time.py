from time import perf_counter
from typing import Callable
from contextlib import contextmanager

from . import profile as _profile

__import__ = [
    "printTime",
    "FrameCounter",
    "ScopedTimer",
    "Timer"
]

def printTime(deltaTime: float):
    print(f"Time: {'{:.4f}'.format(deltaTime)} \t FPS: {'{:.4f}'.format(1/deltaTime)}")

now: Callable[[], float] = perf_counter

@contextmanager
def BenchMark(name):
    if not hasattr(BenchMark, "g_startTimes"):
        BenchMark.g_startTimes = {} # pyright: ignore

    if _profile.is_show_benchmark_log:
        if name not in BenchMark.g_startTimes: # pyright: ignore
            BenchMark.g_startTimes[name] = perf_counter() # pyright: ignore

        start = perf_counter()

    yield
    if _profile.is_show_benchmark_log:
        dt = perf_counter() - start

        if perf_counter() - BenchMark.g_startTimes[name] >= 1: # pyright: ignore
            print(f"{name:<15}: {dt*1000:.6f}ms")
            BenchMark.g_startTimes[name] = perf_counter() # pyright: ignore

class ScopedTimer:
    def __init__(self) -> None:
        self._start_time = perf_counter()

    def __del__(self) -> None:
        self._end_time = perf_counter()
        deltaTime = self._end_time - self._start_time
        printTime(deltaTime)

class Timer:
    def __init__(self) -> None:
        self._current_time = perf_counter()
        self._last_time = perf_counter()
        self.delta_time = 0
        self.time = 0

    def update(self) -> None:
        self._last_time = self._current_time
        self._current_time = perf_counter()
        self.delta_time = self._current_time - self._last_time
        self.time += self.delta_time

    def reset(self):
        self.__init__()

    def info(self):
        printTime(self.delta_time)