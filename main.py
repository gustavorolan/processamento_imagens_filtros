import tkinter as tk

from application.use_cases.process_image_use_case import ProcessImageUseCase
from infrastructure.filters.high_pass_filter import HighPassFilter
from infrastructure.filters.laplacian_filter import LaplacianFilter
from infrastructure.filters.unsharp_masking_filter import UnsharpMaskingFilter
from infrastructure.metrics.image_metrics import ImageMetrics
from presentation.gui.main_window import MainWindow


def main() -> None:
    laplacian = LaplacianFilter(alpha=2.0)
    high_pass = HighPassFilter(center=17)
    unsharp   = UnsharpMaskingFilter(amount=2.5)

    filters  = [laplacian, high_pass, unsharp]
    metrics  = ImageMetrics()
    use_case = ProcessImageUseCase(filters=filters, metrics=metrics)

    root = tk.Tk()
    MainWindow(root, use_case, laplacian=laplacian, high_pass=high_pass, unsharp=unsharp)
    root.mainloop()


if __name__ == "__main__":
    main()
