
import numpy as np
from enum import Enum, auto
from typing import Optional, Tuple


class FilterState(Enum):
    INCOMPLETE = auto()
    INVALID = auto()
    VALID = auto()


class Filter:

    def __init__(self, width):
        self.width = width
        self.distances = np.zeros(width)
        self.angles = np.zeros(width)
        self.valid = 0
        self.invalid = 0

    def enqueue(self, distance: float, angle: float) -> Tuple[FilterState, Optional[float], Optional[float]]:
        if distance:
            self.distances[self.valid] = distance
            self.angles[self.valid] = angle
            self.valid += 1
            if self.valid >= self.width:
                self.valid = self.invalid = 0
                idx = np.argmin(self.distances)
                return FilterState.VALID, self.distances[idx], self.angles[idx]
        else:
            self.invalid += 1
            if self.invalid >= self.width:
                self.valid = self.invalid = 0
                return FilterState.INVALID, None, None

        return FilterState.INCOMPLETE, None, None
