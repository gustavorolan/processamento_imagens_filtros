# Realce e Nitidez de Imagens - Grupo 1

📄 **Documentação completa:** [documentacao.html](documentacao.html) *(abrir no navegador)*

---

## Como executar

**Opção 1 — Executável Windows (sem instalar Python)**

[⬇ ProcessamentoImagens.exe — v1.0.0](https://github.com/gustavorolan/processamento_imagens_filtros/releases/download/v1.0.0/ProcessamentoImagens.exe)

---

**Opção 2 — Python direto**

```bash
pip install -r requirements.txt
python main.py
```

---

**Opção 3 — Ambiente virtual**

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

---

## Como compilar o executável

```powershell
py -m pip install pyinstaller
py -m PyInstaller --onefile --windowed --name "ProcessamentoImagens" --add-data "input;input" --collect-all cv2 --collect-all skimage main.py
```

O \.exe\ é gerado em \dist\ProcessamentoImagens.exe\.

**Publicar no GitHub Releases:**

```powershell
gh auth login
gh release create v1.0.0 "dist\ProcessamentoImagens.exe" --title "v1.0.0" --notes "Descrição."  
# ou atualizar existente:
gh release upload v1.0.0 "dist\ProcessamentoImagens.exe" --clobber
```
