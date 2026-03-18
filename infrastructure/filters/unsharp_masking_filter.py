import cv2
import numpy as np

from domain.interfaces.filter_interface import FilterInterface


class UnsharpMaskingFilter(FilterInterface):
    """
    Máscara de Nitidez (Unsharp Masking).

    Como funciona:
        1. Gera uma versão borrada da imagem com filtro Gaussiano (passa-baixa).
        2. Subtrai o borrado do original para obter a "máscara" de detalhes:
               mascara = original - borrado
        3. Soma a máscara de volta à imagem original com um peso (amount):
               resultado = original + amount * mascara
           Equivalente a: addWeighted(original, amount, blurred, -(amount-1), 0)

        É o método mais natural de nitidez — preserva tons suaves e apenas
        acentua transições, sem injetar ruído como o Laplaciano.

    Como ajustar:
        - kernel_size (padrão (9,9)): tamanho do desfoque Gaussiano. Deve ser
          ímpar. Valores menores como (3,3) ou (5,5) criam uma máscara mais fina
          (detalhes pequenos); valores maiores como (15,15) realçam contornos
          mais amplos.
        - sigma (padrão 15.0): desvio padrão do Gaussiano. Sigma alto = borrão
          mais suave. Diminua para (1.0–3.0) para máscaras mais localizadas.
        - amount (padrão 2.5): intensidade do realce aplicado.
          1.0 = sem efeito extra | 1.5 = suave | 2.5 = forte | 3.5+ = agressivo.
    """

    def __init__(
        self,
        # Tamanho do kernel Gaussiano (deve ser ímpar). Ex: (3,3), (5,5), (9,9), (15,15)
        kernel_size: tuple = (9, 9),
        # Desvio padrão do Gaussiano. Valores maiores = borrão mais uniforme.
        sigma: float = 15.0,
        # Intensidade do realce. 1.0 = neutro; aumente para efeito mais forte.
        amount: float = 2.5,
    ) -> None:
        self._kernel_size = kernel_size
        self._sigma = sigma
        self._amount = amount

    @property
    def amount(self) -> float:
        """Intensidade do realce. 1.0 = neutro | 2.5 = forte | 4.0 = extremo."""
        return self._amount

    @amount.setter
    def amount(self, value: float) -> None:
        self._amount = max(1.0, float(value))

    @property
    def name(self) -> str:
        return "Unsharp Masking"

    def apply(self, image: np.ndarray) -> np.ndarray:
        # Passo 1: gerar versão desfocada (remove altas frequências)
        blurred = cv2.GaussianBlur(image, self._kernel_size, self._sigma)
        # Passo 2: somar o original amplificado com o borrado subtraído
        # fórmula: resultado = amount*original - (amount-1)*blurred
        return cv2.addWeighted(image, self._amount, blurred, -(self._amount - 1.0), 0)
