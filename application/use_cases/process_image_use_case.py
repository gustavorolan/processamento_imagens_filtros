from typing import List

import numpy as np

from domain.entities.filter_result import FilterResult
from domain.interfaces.filter_interface import FilterInterface
from domain.interfaces.metrics_interface import MetricsInterface


class ProcessImageUseCase:
    def __init__(
        self,
        filters: List[FilterInterface],
        metrics: MetricsInterface,
    ) -> None:
        self._filters = filters
        self._metrics = metrics

    def execute(self, image: np.ndarray) -> List[FilterResult]:
        return [self._apply_and_measure(f, image) for f in self._filters]

    def _apply_and_measure(
        self, filter_: FilterInterface, image: np.ndarray
    ) -> FilterResult:
        processed = filter_.apply(image)
        return FilterResult(
            name=filter_.name,
            image=processed,
            mse=self._metrics.calculate_mse(image, processed),
            psnr=self._metrics.calculate_psnr(image, processed),
            ssim=self._metrics.calculate_ssim(image, processed),
        )
