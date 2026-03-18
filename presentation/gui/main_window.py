from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional

import cv2
import numpy as np
from PIL import Image, ImageTk

from application.use_cases.process_image_use_case import ProcessImageUseCase
from domain.entities.filter_result import FilterResult
from infrastructure.filters.high_pass_filter import HighPassFilter
from infrastructure.filters.laplacian_filter import LaplacianFilter
from infrastructure.filters.unsharp_masking_filter import UnsharpMaskingFilter

_INPUT_DIR        = os.path.join(os.path.dirname(__file__), "..", "..", "input")
_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}

_BG         = "#f0f2f5"
_BG_HEADER  = "#1a237e"
_BG_CARD    = "#ffffff"
_BG_SLIDER  = "#e8eaf6"
_ACCENT     = "#3949ab"
_BTN_BG     = "#3949ab"
_BTN_FG     = "#ffffff"
_BTN_HOVER  = "#283593"
_BTN_SEC    = "#eceff1"
_BTN_SEC_FG = "#37474f"
_TEXT       = "#1a1a2e"
_MUTED      = "#6c757d"
_BORDER     = "#dde1e7"
_FONT       = "Segoe UI"
_GREEN      = "#2e7d32"
_RED        = "#c62828"


def _flat_btn(parent, text, command, bg=_BTN_BG, fg=_BTN_FG, hover=_BTN_HOVER, **kw):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, activebackground=hover, activeforeground=fg,
        font=(_FONT, 10, "bold"), relief=tk.FLAT,
        padx=18, pady=8, cursor="hand2", bd=0, **kw,
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=hover))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


class MainWindow:
    _THUMB_HOME   = (140, 140)
    _THUMB_GRID   = (200, 200)
    _THUMB_DETAIL = (320, 320)
    _WINDOW_W     = "1280x860"

    # ── init ──────────────────────────────────────────────────────────────────
    def __init__(self, root, use_case, laplacian, high_pass, unsharp):
        self._root      = root
        self._use_case  = use_case
        self._laplacian = laplacian
        self._high_pass = high_pass
        self._unsharp   = unsharp

        self._photo_refs:    list = []
        self._thumb_refs:    list = []
        self._current_image: Optional[np.ndarray] = None
        self._current_name:  str  = ""
        self._last_results:  List[FilterResult] = []
        self._debounce_id        = None

        self._root.configure(bg=_BG)
        self._apply_styles()
        self._root.title("Realce e Nitidez de Imagens - Grupo 1")
        self._root.geometry(self._WINDOW_W)
        self._root.resizable(True, True)

        self._build_header()
        self._build_pages()
        self._show_home()

    # ── styles ────────────────────────────────────────────────────────────────
    def _apply_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("M.Treeview",
            background=_BG_CARD, fieldbackground=_BG_CARD,
            foreground=_TEXT, font=(_FONT, 11), rowheight=40, borderwidth=0)
        s.configure("M.Treeview.Heading",
            background=_BG_SLIDER, foreground=_ACCENT,
            font=(_FONT, 10, "bold"), relief="flat")
        s.map("M.Treeview", background=[("selected", _BG_SLIDER)])

    # ── header ────────────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self._root, bg=_BG_HEADER, pady=14, padx=24)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="Realce e Nitidez de Imagens",
                 bg=_BG_HEADER, fg="#ffffff", font=(_FONT, 15, "bold")).pack(side=tk.LEFT)
        self._crumb = tk.StringVar(value="")
        tk.Label(hdr, textvariable=self._crumb,
                 bg=_BG_HEADER, fg="#9fa8da", font=(_FONT, 9)).pack(side=tk.RIGHT)

    # ── pages ─────────────────────────────────────────────────────────────────
    def _build_pages(self):
        self._pg_home   = tk.Frame(self._root, bg=_BG)
        self._pg_filter = tk.Frame(self._root, bg=_BG)
        self._pg_detail = tk.Frame(self._root, bg=_BG)
        self._build_home_page()
        self._build_filter_page()
        self._build_detail_page()

    def _show(self, page, crumb):
        for p in (self._pg_home, self._pg_filter, self._pg_detail):
            p.pack_forget()
        page.pack(fill=tk.BOTH, expand=True)
        self._crumb.set(crumb)

    def _show_home(self):
        self._show(self._pg_home, "Inicio  >  Selecionar Imagem")

    def _show_filter(self):
        self._show(self._pg_filter, "Inicio  >  " + self._current_name)
        self._reprocess()

    def _show_detail(self, result: FilterResult):
        self._current_result = result
        self._show(self._pg_detail,
                   "Inicio  >  " + self._current_name + "  >  " + result.name)
        self._render_detail()

    # ══════════════════════════════════════════════════════════════════════════
    # SCREEN 1 — select image
    # ══════════════════════════════════════════════════════════════════════════
    def _build_home_page(self):
        p = self._pg_home
        bar = tk.Frame(p, bg=_BG, padx=24, pady=16)
        bar.pack(fill=tk.X)
        tk.Label(bar, text="Escolha uma imagem para analisar",
                 bg=_BG, fg=_TEXT, font=(_FONT, 13, "bold")).pack(side=tk.LEFT)
        _flat_btn(bar, "+  Carregar do Computador",
                  command=self._on_load_from_disk).pack(side=tk.RIGHT)
        tk.Frame(p, bg=_BORDER, height=1).pack(fill=tk.X, padx=20)
        tk.Label(p, text="IMAGENS DISPONIVEIS EM /input",
                 bg=_BG, fg=_MUTED, font=(_FONT, 8, "bold")).pack(anchor="w", padx=24, pady=(14, 8))
        self._home_grid = tk.Frame(p, bg=_BG)
        self._home_grid.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 16))
        self._populate_home_thumbs()

    def _populate_home_thumbs(self):
        for w in self._home_grid.winfo_children():
            w.destroy()
        self._thumb_refs.clear()
        d = os.path.normpath(_INPUT_DIR)
        files = (sorted(f for f in os.listdir(d)
                        if os.path.splitext(f)[1].lower() in _IMAGE_EXTENSIONS)
                 if os.path.isdir(d) else [])
        if not files:
            tk.Label(self._home_grid,
                     text="Nenhuma imagem encontrada em /input.\nUse o botao acima.",
                     bg=_BG, fg=_MUTED, font=(_FONT, 11), justify=tk.CENTER).pack(expand=True)
            return
        for idx, fn in enumerate(files):
            path = os.path.join(d, fn)
            row, col = divmod(idx, 5)
            self._home_grid.grid_columnconfigure(col, weight=1)
            self._home_card(self._home_grid, fn, path, row, col)

    def _home_card(self, parent, filename, path, row, col):
        try:
            pil = Image.open(path).convert("L").resize(self._THUMB_HOME, Image.LANCZOS)
        except Exception:
            return
        photo = ImageTk.PhotoImage(pil)
        self._thumb_refs.append(photo)
        card = tk.Frame(parent, bg=_BG_CARD,
                        highlightbackground=_BORDER, highlightthickness=2,
                        padx=10, pady=10, cursor="hand2")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        il = tk.Label(card, image=photo, bg=_BG_CARD)
        il.pack(pady=(0, 6))
        nl = tk.Label(card, text=filename, bg=_BG_CARD, fg=_TEXT,
                      font=(_FONT, 9, "bold"), wraplength=150)
        nl.pack()
        _flat_btn(card, "Analisar ->",
                  command=lambda p=path, n=filename: self._select_image(p, n)
                  ).pack(pady=(8, 0), fill=tk.X)
        def oe(e, c=card): c.config(highlightbackground=_ACCENT)
        def ol(e, c=card): c.config(highlightbackground=_BORDER)
        for w in (card, il, nl):
            w.bind("<Enter>", oe); w.bind("<Leave>", ol)
            w.bind("<Button-1>", lambda e, p=path, n=filename: self._select_image(p, n))

    def _on_load_from_disk(self):
        path = filedialog.askopenfilename(
            title="Selecionar Imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.tiff *.tif"),
                       ("Todos os arquivos", "*.*")])
        if path:
            self._select_image(path, path.replace("\\", "/").rsplit("/", 1)[-1])

    def _select_image(self, path, name):
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            messagebox.showerror("Erro", "Nao foi possivel carregar:\n" + path)
            return
        self._current_image = img
        self._current_name  = name
        self._show_filter()

    # ══════════════════════════════════════════════════════════════════════════
    # SCREEN 2 — sliders + clickable filter grid
    # ══════════════════════════════════════════════════════════════════════════
    def _build_filter_page(self):
        p = self._pg_filter

        # top bar
        bar = tk.Frame(p, bg=_BG, padx=24, pady=12)
        bar.pack(fill=tk.X)
        _flat_btn(bar, "<- Voltar", command=self._show_home,
                  bg=_BTN_SEC, fg=_BTN_SEC_FG, hover="#cfd8dc").pack(side=tk.LEFT)
        self._filter_title = tk.Label(bar, text="", bg=_BG, fg=_TEXT, font=(_FONT, 12, "bold"))
        self._filter_title.pack(side=tk.LEFT, padx=14)
        tk.Frame(p, bg=_BORDER, height=1).pack(fill=tk.X, padx=20)

        # sliders
        so = tk.Frame(p, bg=_BG, pady=12, padx=24)
        so.pack(fill=tk.X)
        tk.Label(so, text="AJUSTE DOS FILTROS",
                 bg=_BG, fg=_MUTED, font=(_FONT, 8, "bold")).pack(anchor="w", pady=(0, 8))
        sr = tk.Frame(so, bg=_BG)
        sr.pack(fill=tk.X)
        for c in range(3):
            sr.grid_columnconfigure(c, weight=1)
        self._alpha_var  = tk.DoubleVar(value=self._laplacian.alpha)
        self._center_var = tk.DoubleVar(value=self._high_pass.center)
        self._amount_var = tk.DoubleVar(value=self._unsharp.amount)
        self._slider_card(sr, 0, "Laplaciano - Intensidade (a)",
            "Peso do mapa de bordas. Maior = realce mais forte.",
            self._alpha_var, 0.5, 4.0, "{:.1f}")
        self._slider_card(sr, 1, "Passa-Alta - Centro do Kernel",
            "Valor central do kernel 3x3. Maior = bordas mais pronunciadas.",
            self._center_var, 5, 33, "{:.0f}")
        self._slider_card(sr, 2, "Unsharp Masking - Forca (amount)",
            "Intensidade do realce. 1.0 = neutro / 2.5 = forte / 4.0 = extremo.",
            self._amount_var, 1.0, 4.0, "{:.1f}")

        tk.Frame(p, bg=_BORDER, height=1).pack(fill=tk.X, padx=20, pady=(4, 0))
        tk.Label(p, text="CLIQUE EM UMA IMAGEM FILTRADA PARA VER AS METRICAS",
                 bg=_BG, fg=_MUTED, font=(_FONT, 8, "bold")).pack(anchor="w", padx=24, pady=(10, 4))

        # 2x2 image grid (non-scrollable, fixed size cards)
        self._grid_frame = tk.Frame(p, bg=_BG)
        self._grid_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 16))
        for c in range(2):
            self._grid_frame.grid_columnconfigure(c, weight=1)
        for r in range(2):
            self._grid_frame.grid_rowconfigure(r, weight=1)

    def _slider_card(self, parent, col, label, tooltip, var, from_, to, fmt):
        card = tk.Frame(parent, bg=_BG_CARD,
                        highlightbackground=_BORDER, highlightthickness=1,
                        padx=14, pady=12)
        card.grid(row=0, column=col, padx=6, sticky="ew")
        top = tk.Frame(card, bg=_BG_CARD)
        top.pack(fill=tk.X, pady=(0, 4))
        tk.Label(top, text=label, bg=_BG_CARD, fg=_TEXT,
                 font=(_FONT, 9, "bold")).pack(side=tk.LEFT)
        vl = tk.Label(top, text=fmt.format(var.get()),
                      bg=_ACCENT, fg="#ffffff", font=(_FONT, 9, "bold"), padx=10, pady=2)
        vl.pack(side=tk.RIGHT)
        tk.Label(card, text=tooltip, bg=_BG_CARD, fg=_MUTED,
                 font=(_FONT, 8), wraplength=280, justify=tk.LEFT).pack(anchor="w", pady=(0, 8))
        def on_change(v, vl=vl, f=fmt):
            vl.config(text=f.format(float(v)))
            self._schedule_reprocess()
        tk.Scale(card, from_=from_, to=to, variable=var,
                 orient=tk.HORIZONTAL, resolution=0.1,
                 bg=_BG_CARD, fg=_TEXT, troughcolor=_BG_SLIDER,
                 highlightthickness=0, bd=0, showvalue=False,
                 command=on_change).pack(fill=tk.X)

    def _schedule_reprocess(self):
        if self._debounce_id:
            self._root.after_cancel(self._debounce_id)
        self._debounce_id = self._root.after(150, self._reprocess)

    def _reprocess(self):
        self._laplacian.alpha  = self._alpha_var.get()
        self._high_pass.center = int(self._center_var.get())
        self._unsharp.amount   = self._amount_var.get()
        if self._current_image is not None:
            self._filter_title.config(text=self._current_name)
            self._last_results = self._use_case.execute(self._current_image)
            self._render_grid(self._current_image, self._last_results)

    def _render_grid(self, original, results):
        for w in self._grid_frame.winfo_children():
            w.destroy()
        self._photo_refs.clear()
        all_items = [("Imagem Original", original, None)] + \
                    [(r.name, r.image, r) for r in results]
        for idx, (title, img, result) in enumerate(all_items):
            row, col = divmod(idx, 2)
            self._grid_card(self._grid_frame, title, img, row, col, result)

    def _grid_card(self, parent, title, img, row, col, result):
        is_clickable = result is not None
        border_col   = _ACCENT if is_clickable else _BORDER
        card = tk.Frame(parent, bg=_BG_CARD,
                        highlightbackground=border_col,
                        highlightthickness=2 if is_clickable else 1,
                        padx=10, pady=10,
                        cursor="hand2" if is_clickable else "arrow")
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        hint = "  (clique para metricas)" if is_clickable else ""
        color = _ACCENT if is_clickable else _TEXT
        tk.Label(card, text=title + hint, bg=_BG_CARD, fg=color,
                 font=(_FONT, 10, "bold")).pack(pady=(0, 6))

        pil_img = Image.fromarray(img).resize(self._THUMB_GRID, Image.LANCZOS)
        photo   = ImageTk.PhotoImage(pil_img)
        self._photo_refs.append(photo)
        img_lbl = tk.Label(card, image=photo, bg=_BG_CARD)
        img_lbl.pack()

        if is_clickable:
            def on_click(e=None, r=result): self._show_detail(r)
            def oe(e, c=card): c.config(highlightbackground="#1a237e")
            def ol(e, c=card): c.config(highlightbackground=_ACCENT)
            for w in (card, img_lbl):
                w.bind("<Button-1>", on_click)
                w.bind("<Enter>", oe)
                w.bind("<Leave>", ol)

    # ══════════════════════════════════════════════════════════════════════════
    # SCREEN 3 — detail: original vs filter + metrics
    # ══════════════════════════════════════════════════════════════════════════
    def _build_detail_page(self):
        p = self._pg_detail

        # top bar
        bar = tk.Frame(p, bg=_BG, padx=24, pady=12)
        bar.pack(fill=tk.X)
        _flat_btn(bar, "<- Voltar aos Filtros", command=self._show_filter,
                  bg=_BTN_SEC, fg=_BTN_SEC_FG, hover="#cfd8dc").pack(side=tk.LEFT)
        self._detail_title = tk.Label(bar, text="", bg=_BG, fg=_TEXT, font=(_FONT, 12, "bold"))
        self._detail_title.pack(side=tk.LEFT, padx=14)
        tk.Frame(p, bg=_BORDER, height=1).pack(fill=tk.X, padx=20)

        # side-by-side image area
        img_row = tk.Frame(p, bg=_BG, padx=24, pady=16)
        img_row.pack(fill=tk.X)
        img_row.grid_columnconfigure(0, weight=1)
        img_row.grid_columnconfigure(1, weight=1)

        # original card placeholder
        self._detail_orig_card = tk.Frame(img_row, bg=_BG_CARD,
                                          highlightbackground=_BORDER, highlightthickness=1,
                                          padx=16, pady=16)
        self._detail_orig_card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        # filtered card placeholder
        self._detail_filt_card = tk.Frame(img_row, bg=_BG_CARD,
                                          highlightbackground=_ACCENT, highlightthickness=2,
                                          padx=16, pady=16)
        self._detail_filt_card.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        tk.Frame(p, bg=_BORDER, height=1).pack(fill=tk.X, padx=20)

        # metrics section
        m_outer = tk.Frame(p, bg=_BG, padx=24, pady=16)
        m_outer.pack(fill=tk.BOTH, expand=True)
        tk.Label(m_outer, text="METRICAS DE QUALIDADE",
                 bg=_BG, fg=_MUTED, font=(_FONT, 8, "bold")).pack(anchor="w", pady=(0, 8))
        self._detail_metrics_frame = tk.Frame(m_outer, bg=_BG)
        self._detail_metrics_frame.pack(fill=tk.BOTH, expand=True)

    def _render_detail(self):
        result = self._current_result

        # title
        self._detail_title.config(text=result.name)

        # clear cards
        for w in self._detail_orig_card.winfo_children():
            w.destroy()
        for w in self._detail_filt_card.winfo_children():
            w.destroy()
        for w in self._detail_metrics_frame.winfo_children():
            w.destroy()
        self._photo_refs.clear()

        # original image
        tk.Label(self._detail_orig_card, text="Imagem Original",
                 bg=_BG_CARD, fg=_TEXT, font=(_FONT, 11, "bold")).pack(pady=(0, 10))
        orig_pil   = Image.fromarray(self._current_image).resize(self._THUMB_DETAIL, Image.LANCZOS)
        orig_photo = ImageTk.PhotoImage(orig_pil)
        self._photo_refs.append(orig_photo)
        tk.Label(self._detail_orig_card, image=orig_photo, bg=_BG_CARD).pack()

        # filtered image
        tk.Label(self._detail_filt_card, text=result.name,
                 bg=_BG_CARD, fg=_ACCENT, font=(_FONT, 11, "bold")).pack(pady=(0, 10))
        filt_pil   = Image.fromarray(result.image).resize(self._THUMB_DETAIL, Image.LANCZOS)
        filt_photo = ImageTk.PhotoImage(filt_pil)
        self._photo_refs.append(filt_photo)
        tk.Label(self._detail_filt_card, image=filt_photo, bg=_BG_CARD).pack()

        # metrics cards row
        metrics = [
            ("MSE", f"{result.mse:.4f}", "Erro quadratico medio\nMenor = mais proximo do original", result.mse < 500),
            ("PSNR", f"{result.psnr:.2f} dB" if result.psnr != float("inf") else "inf dB",
             "Relacao sinal-ruido de pico\nMaior = melhor qualidade (>40 dB = excelente)", result.psnr > 30),
            ("SSIM", f"{result.ssim:.4f}",
             "Similaridade estrutural (0-1)\nMais proximo de 1 = mais similar ao original", result.ssim > 0.8),
        ]
        for label, value, desc, good in metrics:
            card = tk.Frame(self._detail_metrics_frame, bg=_BG_CARD,
                            highlightbackground=_BORDER, highlightthickness=1,
                            padx=20, pady=18)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
            tk.Label(card, text=label, bg=_BG_CARD, fg=_MUTED,
                     font=(_FONT, 9, "bold")).pack(anchor="w")
            val_color = _GREEN if good else _RED
            tk.Label(card, text=value, bg=_BG_CARD, fg=val_color,
                     font=(_FONT, 22, "bold")).pack(anchor="w", pady=(4, 6))
            tk.Label(card, text=desc, bg=_BG_CARD, fg=_MUTED,
                     font=(_FONT, 8), justify=tk.LEFT).pack(anchor="w")

        # comparison table showing all filters for reference
        tk.Frame(self._detail_metrics_frame, bg=_BORDER, width=1
                 ).pack(side=tk.LEFT, fill=tk.Y, padx=4)

        if self._last_results:
            tbl_frame = tk.Frame(self._detail_metrics_frame, bg=_BG_CARD,
                                 highlightbackground=_BORDER, highlightthickness=1,
                                 padx=14, pady=14)
            tbl_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
            tk.Label(tbl_frame, text="COMPARACAO COM DEMAIS FILTROS",
                     bg=_BG_CARD, fg=_MUTED, font=(_FONT, 8, "bold")).pack(anchor="w", pady=(0, 6))
            cols = ("Filtro", "MSE", "PSNR (dB)", "SSIM")
            tree = ttk.Treeview(tbl_frame, columns=cols, show="headings",
                                height=len(self._last_results), style="M.Treeview")
            for c, w in zip(cols, (200, 100, 110, 100)):
                tree.heading(c, text=c)
                tree.column(c, width=w, anchor=tk.CENTER)
            for r in self._last_results:
                psnr_s = f"{r.psnr:.2f}" if r.psnr != float("inf") else "inf"
                tag = "sel" if r.name == result.name else ""
                tree.insert("", tk.END, values=(r.name, f"{r.mse:.2f}", psnr_s, f"{r.ssim:.4f}"), tags=(tag,))
            tree.tag_configure("sel", background=_BG_SLIDER)
            tree.pack(fill=tk.X)
