from dataclasses import dataclass
from typing import Tuple, List


@dataclass
class Location:
    x: int
    y: int
    height: int = 127
    index: int = 0

    @property
    def position(self):
        return self.x, self.y + self.index

    def scroll(self, distance: int = 1, cc: int = None) -> Tuple[int, int]:
        if cc is not None:
            # TODO: this is specific to my controller
            if cc > 65:
                distance = -1
            else:
                distance = 1
            self._prev_cc = cc
        self.index = (self.index + distance) % self.height
        return self.x, self.y + self.index

    def reset_index(self):
        self.index = 0


@dataclass
class LocationManager:
    locations: List[Location]
    _index: int = 0
    _should_reset_indices: bool = False
    _should_carry_over_indices: bool = True

    @property
    def current(self) -> Location:
        return self.locations[self._index]

    def next(self) -> Location:
        prev = self.current
        self._index = (self._index + 1) % len(self.locations)
        if self._should_reset_indices:
            prev.reset_index()
        elif self._should_carry_over_indices:
            self.current.index = prev.index % self.current.height
        return self.current

    def previous(self) -> Location:
        if self._should_reset_indices:
            self.current.reset_index()
        self._index = (self._index - 1) % len(self.locations)
        return self.current
