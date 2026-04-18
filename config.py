"""
Configurações centralizadas do projeto.

Todas as constantes de caminhos, nomes de colunas e configurações
globais ficam aqui para facilitar manutenção.
"""

from pathlib import Path

# ─────────────────────────────────────────────
# Diretórios do sistema de triagem
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent

PASTA_NOVOS = BASE_DIR / "1_Novos_Comprovantes"
PASTA_SUCESSO = BASE_DIR / "2_Processados_com_Sucesso"
PASTA_REVISAO = BASE_DIR / "3_Revisao_Manual"

# ─────────────────────────────────────────────
# Planilha Excel
# ─────────────────────────────────────────────
PLANILHA_EXCEL = BASE_DIR / "comprovantes.xlsx"

# Nomes das colunas na planilha (devem corresponder ao cabeçalho existente)
COLUNAS = {
    "nome": "Nome",
    "data": "Data",
    "valor": "Valor",
}

# Nome da aba (sheet) dentro do Excel
NOME_ABA = "Sheet1"
