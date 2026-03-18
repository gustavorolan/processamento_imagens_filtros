from dataclasses import dataclass

import numpy as np


@dataclass
class FilterResult:
    name: str
    image: np.ndarray
    mse: float
    psnr: float
    ssim: float
