from abc import ABC, abstractmethod

import numpy as np


class MetricsInterface(ABC):
    @abstractmethod
    def calculate_mse(self, original: np.ndarray, processed: np.ndarray) -> float:
        ...

    @abstractmethod
    def calculate_psnr(self, original: np.ndarray, processed: np.ndarray) -> float:
        ...

    @abstractmethod
    def calculate_ssim(self, original: np.ndarray, processed: np.ndarray) -> float:
        ...
