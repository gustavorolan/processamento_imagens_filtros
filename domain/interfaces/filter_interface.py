from abc import ABC, abstractmethod

import numpy as np


class FilterInterface(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def apply(self, image: np.ndarray) -> np.ndarray:
        ...
