from time import perf_counter

def printTime(deltaTime: float):
    print(f"Time: {'{:.4f}'.format(deltaTime)} \t FPS: {'{:.4f}'.format(1/deltaTime)}")

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
        self.deltaTime = 0
        self.time = 0

    def update(self) -> None:
        self._last_time = self._current_time
        self._current_time = perf_counter()
        self.deltaTime = self._current_time - self._last_time
        self.time += self.deltaTime

    def reset(self):
        self.__init__()

    def info(self):
        printTime(self.deltaTime)