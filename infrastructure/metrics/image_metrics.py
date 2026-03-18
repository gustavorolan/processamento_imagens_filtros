import numpy as np
from skimage.metrics import structural_similarity

from domain.interfaces.metrics_interface import MetricsInterface


class ImageMetrics(MetricsInterface):
    """
    Calcula as três métricas de qualidade usadas no artigo.

    Métricas implementadas:
        MSE  — Mean Squared Error (Erro Quadrático Médio)
               Mede a diferença pixel a pixel entre a imagem original e a
               processada. Quanto MENOR, mais próxima da original.
               MSE = 0 significa imagens idênticas.

        PSNR — Peak Signal-to-Noise Ratio (Relação Sinal-Ruído de Pico)
               Derivado do MSE, expresso em decibéis (dB).
               Quanto MAIOR, melhor a qualidade da imagem processada.
               > 40 dB = excelente | 30–40 dB = bom | < 30 dB = perda visível.

        SSIM — Structural Similarity Index (Índice de Similaridade Estrutural)
               Compara luminância, contraste e estrutura. Varia de 0 a 1.
               Quanto mais PRÓXIMO de 1, maior a similaridade com a original.
               É mais correlacionado com a percepção humana que MSE/PSNR.

    Como ajustar:
        - _MAX_PIXEL_VALUE (padrão 255.0): mude para 1.0 se trabalhar com
          imagens normalizadas no intervalo [0, 1].
        - Para adicionar uma nova métrica: implemente o método aqui e declare
          o método abstrato correspondente em MetricsInterface.
    """

    # Valor máximo do pixel. Para imagens uint8 = 255. Para float [0,1] = 1.0.
    _MAX_PIXEL_VALUE: float = 255.0

    def calculate_mse(self, original: np.ndarray, processed: np.ndarray) -> float:
        # Converte para float64 antes de subtrair para evitar overflow em uint8
        diff = original.astype(np.float64) - processed.astype(np.float64)
        return float(np.mean(diff ** 2))

    def calculate_psnr(self, original: np.ndarray, processed: np.ndarray) -> float:
        mse = self.calculate_mse(original, processed)
        if mse == 0.0:
            return float("inf")  # imagens idênticas
        # Fórmula: 10 * log10(MAX² / MSE)
        return float(10.0 * np.log10(self._MAX_PIXEL_VALUE ** 2 / mse))

    def calculate_ssim(self, original: np.ndarray, processed: np.ndarray) -> float:
        # data_range informa ao skimage o intervalo dinâmico da imagem (0–255)
        return float(
            structural_similarity(
                original, processed, data_range=int(self._MAX_PIXEL_VALUE)
            )
        )
