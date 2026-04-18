"""
Leitor de PDFs.

Módulo responsável por extrair o texto bruto de um arquivo PDF.
Utiliza pdfplumber como biblioteca principal e PyMuPDF (fitz) como fallback,
garantindo maior compatibilidade com diferentes tipos de PDF.
"""

from pathlib import Path


def extrair_texto_pdf(caminho_pdf: Path) -> str:
    """
    Extrai todo o texto de um arquivo PDF.

    Tenta primeiro com pdfplumber (melhor para PDFs com layout tabular).
    Se falhar ou retornar vazio, tenta com PyMuPDF (fitz) como fallback.

    Args:
        caminho_pdf: Caminho absoluto para o arquivo PDF.

    Returns:
        String contendo todo o texto extraído do PDF.

    Raises:
        RuntimeError: Se ambas as bibliotecas falharem na extração.
    """
    texto = _extrair_com_pdfplumber(caminho_pdf)

    if not texto or not texto.strip():
        texto = _extrair_com_pymupdf(caminho_pdf)

    if not texto or not texto.strip():
        raise RuntimeError(
            f"Não foi possível extrair texto do PDF: {caminho_pdf.name}"
        )

    return texto


def _extrair_com_pdfplumber(caminho_pdf: Path) -> str:
    """Extrai texto usando pdfplumber (ideal para PDFs com tabelas/layouts)."""
    try:
        import pdfplumber

        paginas_texto = []
        with pdfplumber.open(str(caminho_pdf)) as pdf:
            for pagina in pdf.pages:
                texto = pagina.extract_text()
                if texto:
                    paginas_texto.append(texto)

        return "\n".join(paginas_texto)

    except Exception:
        return ""


def _extrair_com_pymupdf(caminho_pdf: Path) -> str:
    """Extrai texto usando PyMuPDF/fitz (fallback robusto)."""
    try:
        import fitz  # PyMuPDF

        paginas_texto = []
        with fitz.open(str(caminho_pdf)) as doc:
            for pagina in doc:
                texto = pagina.get_text()
                if texto:
                    paginas_texto.append(texto)

        return "\n".join(paginas_texto)

    except Exception:
        return ""
