# Realce e Nitidez de Imagens — Grupo 1

Trabalho prático de Processamento de Imagens. Aplica e compara três técnicas de realce de nitidez em imagens digitais em tons de cinza, calculando métricas de qualidade para análise no artigo IEEE.

---

## Técnicas implementadas

| Técnica | Arquivo | O que faz |
|---|---|---|
| **Filtro Laplaciano** | `infrastructure/filters/laplacian_filter.py` | Realça bordas via segunda derivada da imagem |
| **Filtro Passa-Alta** | `infrastructure/filters/high_pass_filter.py` | Remove baixas frequências, preserva detalhes e bordas |
| **Unsharp Masking** | `infrastructure/filters/unsharp_masking_filter.py` | Nitidez controlada via subtração de versão borrada |

**Métricas calculadas:** MSE · PSNR · SSIM

---

## Requisitos

- Python 3.8+
- Pacotes listados em `requirements.txt`

---

## Instalação

```bash
pip install -r requirements.txt
```

---

## Execução com Python

```bash
python main.py
```

> Se `python` não for reconhecido, use:
> ```powershell
> py main.py
> ```

---

## Download — Executável Windows (.exe)

Baixe e execute diretamente, sem precisar instalar Python:

**[ProcessamentoImagens.exe — v1.0.0](https://github.com/gustavorolan/processamento_imagens_filtros/releases/download/v1.0.0/ProcessamentoImagens.exe)**

---

## Compilar nova versão e publicar no GitHub Releases

### 1. Instalar dependências (apenas uma vez)

```powershell
py -m pip install -r requirements.txt
py -m pip install pyinstaller
```

### 2. Gerar o `.exe`

```powershell
py -m PyInstaller --onefile --windowed --name "ProcessamentoImagens" --add-data "input;input" --collect-all cv2 --collect-all skimage main.py
```

O executável será gerado em `dist\ProcessamentoImagens.exe`.

### 3. Publicar no GitHub Releases

Instale o [GitHub CLI](https://cli.github.com) e autentique-se (apenas uma vez):

```powershell
gh auth login
```

Crie a release e faça o upload do `.exe` (troque `v1.0.0` pela versão desejada):

```powershell
gh release create v1.0.0 "dist\ProcessamentoImagens.exe" --title "v1.0.0 — Windows Executable" --notes "Descrição das mudanças desta versão."
```

Para atualizar uma release já existente com um novo `.exe`:

```powershell
gh release upload v1.0.0 "dist\ProcessamentoImagens.exe" --clobber
```

> O link de download segue sempre o padrão:  
> `https://github.com/<usuario>/<repositorio>/releases/download/<versao>/ProcessamentoImagens.exe`

---

## Como usar

1. Execute `main.py` — a janela abre automaticamente.
2. No painel **"Imagens disponíveis em /input"**, clique em qualquer miniatura para aplicar os filtros.
3. Ou use **"Carregar do Computador"** para selecionar qualquer imagem do seu sistema.
4. Visualize as **4 imagens** (original + 3 filtros) e a **tabela de métricas** (MSE, PSNR, SSIM).

---

## Estrutura do projeto

```
trabalho_processamento_imagens/
│
├── main.py                          # Entry point — monta as dependências e abre a janela
├── requirements.txt
├── README.md
│
├── input/                           # Imagens de teste (Standard Test Images)
│   ├── cameraman.png                # Clássica do MIT — a mais usada em artigos
│   ├── coins.png                    # Moedas — bom contraste de bordas
│   ├── moon.png                     # Superfície lunar — textura rica
│   ├── horse.png                    # Silhueta binária
│   └── clock.png                    # Relógio — bordas marcadas
│
├── domain/                          # Regras de negócio puras (sem dependências externas)
│   ├── entities/
│   │   └── filter_result.py         # Dataclass: name, image, mse, psnr, ssim
│   └── interfaces/
│       ├── filter_interface.py      # ABC com name + apply()
│       └── metrics_interface.py     # ABC com calculate_mse/psnr/ssim()
│
├── application/                     # Casos de uso (orquestra o domínio)
│   └── use_cases/
│       └── process_image_use_case.py # Recebe lista de filtros + métricas, retorna resultados
│
├── infrastructure/                  # Implementações concretas (OpenCV, scikit-image)
│   ├── filters/
│   │   ├── laplacian_filter.py      # Laplaciano com ksize e alpha configuráveis
│   │   ├── high_pass_filter.py      # Kernel passa-alta 3x3 configurável
│   │   └── unsharp_masking_filter.py # Gaussian blur + subtração com amount e sigma
│   └── metrics/
│       └── image_metrics.py         # MSE (manual), PSNR (manual), SSIM (skimage)
│
└── presentation/
    └── gui/
        └── main_window.py           # Interface Tkinter: painel de input + grid + tabela
```

---

## Ajuste interativo dos filtros (sliders na tela)

A interface possui **3 sliders** — um por filtro — que permitem ajustar a intensidade em tempo real sem editar código. Ao soltar o slider, a imagem e a tabela de métricas são atualizadas automaticamente.

| Slider | Parâmetro | Faixa | Efeito |
|---|---|---|---|
| **Laplaciano — Intensidade (α)** | `alpha` | 0.5 → 4.0 | Peso do mapa de bordas. Maior = bordas mais fortes, mais ruído |
| **Passa-Alta — Centro do Kernel** | `center` | 5 → 33 | Valor central do kernel 3×3. Maior = realce mais agressivo |
| **Unsharp Masking — Força (amount)** | `amount` | 1.0 → 4.0 | Intensidade do realce. 1.0 = neutro, 2.5 = forte, 4.0 = extremo |

### Como os sliders funcionam internamente

Cada filtro expõe uma **property com setter** em `infrastructure/filters/`. Quando o slider muda, o `MainWindow` chama o setter do filtro e reenvia a imagem atual pelo `ProcessImageUseCase`:

```
Slider move → setter do filtro atualizado → use_case.execute(imagem_atual) → UI re-renderizada
```

Um **debounce de 120 ms** evita reprocessamentos excessivos enquanto o slider ainda está em movimento.

---

## Métricas — guia de interpretação

| Métrica | Melhor valor | Interpretação |
|---|---|---|
| **MSE** | Menor | Diferença quadrática média dos pixels. 0 = idêntico à original |
| **PSNR** | Maior (dB) | > 40 dB excelente · 30–40 dB bom · < 30 dB perda visível |
| **SSIM** | Próximo de 1 | Similaridade estrutural. 1 = idêntico · correlaciona com percepção humana |

---

## Referências

- Gonzalez, R. C.; Woods, R. E. *Digital Image Processing*, 4ª ed. Pearson, 2018.
- OpenCV Documentation: https://docs.opencv.org
- scikit-image Documentation: https://scikit-image.org/docs/stable/
