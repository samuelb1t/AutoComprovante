"""
╔══════════════════════════════════════════════════════════════╗
║  PROCESSADOR DE COMPROVANTES BANCÁRIOS                      ║
║  Extrai dados de PDFs e insere em planilha Excel             ║
╚══════════════════════════════════════════════════════════════╝

Script principal que orquestra todo o fluxo:
  1. Lê PDFs da pasta 1_Novos_Comprovantes
  2. Extrai texto de cada PDF (pdfplumber → PyMuPDF fallback)
  3. Aplica estratégias de extração (Strategy Pattern)
  4. Insere dados no Excel (próxima linha vazia)
  5. Move PDFs para pasta de sucesso ou revisão manual

Uso:
    python main.py
"""

import shutil
import sys
from pathlib import Path

from config import PASTA_NOVOS, PASTA_REVISAO, PASTA_SUCESSO, PLANILHA_EXCEL
from excel_writer import inserir_no_excel
from leitor_pdf import extrair_texto_pdf
from motor_extracao import aplicar_estrategias


# ─────────────────────────────────────────────
# Utilidades
# ─────────────────────────────────────────────

def garantir_pastas() -> None:
    """Cria as pastas de triagem se não existirem."""
    for pasta in [PASTA_NOVOS, PASTA_SUCESSO, PASTA_REVISAO]:
        pasta.mkdir(parents=True, exist_ok=True)


def mover_arquivo(origem: Path, pasta_destino: Path) -> Path:
    """
    Move um arquivo para a pasta de destino.
    Se já existir um arquivo com o mesmo nome, adiciona sufixo numérico.
    """
    destino = pasta_destino / origem.name

    # Evita sobrescrever: adiciona _1, _2, etc.
    contador = 1
    while destino.exists():
        destino = pasta_destino / f"{origem.stem}_{contador}{origem.suffix}"
        contador += 1

    shutil.move(str(origem), str(destino))
    return destino


def listar_pdfs(pasta: Path) -> list[Path]:
    """Lista todos os arquivos PDF na pasta (não-recursivo)."""
    return sorted(pasta.glob("*.pdf"))


# ─────────────────────────────────────────────
# Fluxo Principal
# ─────────────────────────────────────────────

def processar_comprovantes() -> None:
    """Fluxo principal de processamento."""

    print("\n" + "═" * 60)
    print("  📋 PROCESSADOR DE COMPROVANTES BANCÁRIOS")
    print("═" * 60)

    # 1. Garante que as pastas existam
    garantir_pastas()

    # 2. Lista PDFs na pasta de entrada
    pdfs = listar_pdfs(PASTA_NOVOS)

    if not pdfs:
        print(f"\n📂 Nenhum PDF encontrado em: {PASTA_NOVOS.name}/")
        print("   Coloque os comprovantes nesta pasta e execute novamente.\n")
        return

    print(f"\n📂 {len(pdfs)} PDF(s) encontrado(s) em: {PASTA_NOVOS.name}/\n")

    # Contadores para o resumo final
    sucesso = 0
    falha = 0
    erro_excel = 0

    # 3. Processa cada PDF
    for i, pdf in enumerate(pdfs, 1):
        print(f"─── [{i}/{len(pdfs)}] {pdf.name} ───")

        # 3a. Extrai texto do PDF
        try:
            texto = extrair_texto_pdf(pdf)
        except RuntimeError as e:
            print(f"  ❌ {e}")
            mover_arquivo(pdf, PASTA_REVISAO)
            falha += 1
            print(f"  📁 Movido para: {PASTA_REVISAO.name}/\n")
            continue

        # 3b. Aplica estratégias de extração
        dados, nome_estrategia = aplicar_estrategias(texto)

        if dados is None:
            print("  ❌ Nenhuma estratégia conseguiu extrair os 3 campos.")
            mover_arquivo(pdf, PASTA_REVISAO)
            falha += 1
            print(f"  📁 Movido para: {PASTA_REVISAO.name}/\n")
            continue

        # 3c. Exibe dados extraídos
        print(f"  ✅ Estratégia: {nome_estrategia}")
        print(dados)

        # 3d. Insere no Excel
        if inserir_no_excel(dados):
            mover_arquivo(pdf, PASTA_SUCESSO)
            sucesso += 1
            print(f"  📁 Movido para: {PASTA_SUCESSO.name}/\n")
        else:
            # Erro no Excel (PermissionError, etc) — não move o arquivo
            erro_excel += 1
            print(f"  ⚠️  PDF mantido em: {PASTA_NOVOS.name}/ (erro ao salvar)\n")

    # 4. Resumo final
    print("═" * 60)
    print("  📊 RESUMO")
    print("═" * 60)
    print(f"  ✅ Processados com sucesso : {sucesso}")
    print(f"  ❌ Enviados para revisão   : {falha}")
    if erro_excel:
        print(f"  ⚠️  Erros ao salvar no Excel: {erro_excel}")
    print(f"  📄 Planilha: {PLANILHA_EXCEL.name}")
    print("═" * 60 + "\n")


# ─────────────────────────────────────────────
# Ponto de entrada
# ─────────────────────────────────────────────

if __name__ == "__main__":
    try:
        processar_comprovantes()
    except KeyboardInterrupt:
        print("\n\n⏹️  Execução interrompida pelo usuário.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}\n")
        sys.exit(1)
