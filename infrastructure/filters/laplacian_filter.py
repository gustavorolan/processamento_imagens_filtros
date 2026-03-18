import cv2
import numpy as np

from domain.interfaces.filter_interface import FilterInterface


class LaplacianFilter(FilterInterface):
    """
    Realce de bordas via segunda derivada (Filtro Laplaciano).

    Como funciona:
        1. cv2.Laplacian calcula a segunda derivada da imagem, realçando regiões
           onde a intensidade muda bruscamente (bordas e detalhes).
        2. O resultado é somado à imagem original com um peso (alpha abaixo),
           produzindo o realce final.

    Como ajustar:
        - ksize (padrão 5): tamanho do kernel Laplaciano. Valores válidos: 1, 3, 5, 7.
          Kernels maiores capturam bordas mais grossas, mas ampliam mais o ruído.
          Para efeito mais suave use ksize=1 ou ksize=3.
        - alpha em addWeighted (padrão 2.0): peso do Laplaciano somado à original.
          Aumente para bordas mais pronunciadas; diminua para efeito mais sutil.
          Exemplo mais forte: alpha=3.0 | Mais suave: alpha=0.8
    """

    def __init__(self, alpha: float = 2.0, ksize: int = 5) -> None:
        self._alpha = alpha
        # ksize deve ser 1, 3, 5 ou 7 — valores pares são inválidos para o Laplaciano
        self._ksize = ksize

    @property
    def alpha(self) -> float:
        """Peso do mapa de bordas somado à imagem original. Aumente para realce mais forte."""
        return self._alpha

    @alpha.setter
    def alpha(self, value: float) -> None:
        self._alpha = max(0.1, float(value))

    @property
    def name(self) -> str:
        return "Filtro Laplaciano"

    def apply(self, image: np.ndarray) -> np.ndarray:
        # CV_64F permite valores negativos na derivada, preservando bordas escuras
        laplacian = cv2.Laplacian(image, cv2.CV_64F, ksize=self._ksize)
        # Converte de volta para uint8: valores negativos viram positivos (abs)
        laplacian_abs = cv2.convertScaleAbs(laplacian)
        # Soma a imagem original (peso 1.0) com o mapa de bordas (peso alpha)
        return cv2.addWeighted(image, 1.0, laplacian_abs, self._alpha, 0)
