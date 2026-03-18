import cv2
import numpy as np

from domain.interfaces.filter_interface import FilterInterface


class HighPassFilter(FilterInterface):
    """
    Realce de detalhes via kernel Passa-Alta (High-Pass Filter).

    Como funciona:
        O kernel subtrai os pixels vizinhos do pixel central, eliminando
        informações de baixa frequência (áreas homogêneas) e preservando
        apenas as altas frequências (bordas, textura, detalhes finos).

        Kernel padrão (3x3):
            [[-2, -2, -2],
             [-2, 17, -2],
             [-2, -2, -2]]
        A soma dos elementos é 1, o que mantém o brilho médio da imagem.

    Como ajustar:
        - Valor central (padrão 17): controla a intensidade do realce.
          Aumente (ex: 25) para efeito mais agressivo; diminua (ex: 9) para mais suave.
          ATENÇÃO: a soma do kernel deve ser >= 1 para não escurecer a imagem.
          Regra: centro = 1 + (abs(vizinhos) * quantidade_de_vizinhos).
        - Vizinhos (padrão -2): quanto cada pixel ao redor é subtraído.
          Vizinhos mais negativos = mais contraste nas bordas.
        - Para um kernel 5x5 mais forte, substitua _KERNEL por um array 5x5.
    """

    def __init__(self, center: int = 17) -> None:
        # center é o valor do pixel central do kernel 3x3
        self._center = center
        self._kernel = self._build_kernel(center)

    @staticmethod
    def _build_kernel(center: int) -> np.ndarray:
        """Constrói kernel 3x3 onde vizinhos = -(center-1)/8 para soma = 1."""
        neighbor = -(center - 1) / 8
        return np.array(
            [[neighbor, neighbor, neighbor],
             [neighbor, center,   neighbor],
             [neighbor, neighbor, neighbor]],
            dtype=np.float32,
        )

    @property
    def center(self) -> int:
        """Valor central do kernel. Maior = bordas mais fortes. Sugerido: 5–33."""
        return self._center

    @center.setter
    def center(self, value: int) -> None:
        self._center = max(3, int(value))
        self._kernel = self._build_kernel(self._center)

    @property
    def name(self) -> str:
        return "Filtro Passa-Alta"

    def apply(self, image: np.ndarray) -> np.ndarray:
        # filter2D aplica a convolução do kernel sobre cada pixel da imagem.
        # O parâmetro -1 mantém o mesmo tipo de dado da imagem de entrada.
        return cv2.filter2D(image, -1, self._kernel)
