from dataclasses import dataclass
from collections import deque

from .utils import get_current_ts

@dataclass
class WindowObservation:
    value: float
    ts: float

class DefaultRollingWindowContainerWithTimestams:

    def __init__(self, window_size):
        self._size = window_size
        self._deque = deque()

    def __remove_old_observaitions(self, cur_ts=None):
        if cur_ts is None:
            cur_ts = get_current_ts()
        while len(self._deque) > 0 and cur_ts - self._size > self._deque[0].ts:
            self._deque.popleft()

    def insert(self, value, time):
        self._deque.append(WindowObservation(value, time))
        self.__remove_old_observaitions()

    def size(self):
        self.__remove_old_observaitions()
        return len(self._deque)

    def get_first(self):
        self.__remove_old_observaitions()
        if not len(self._deque):
            return (0)
        return self._deque[0]

    def get_last(self):
        self.__remove_old_observaitions()
        if not len(self._deque):
            return (0)
        return self._deque[-1]
