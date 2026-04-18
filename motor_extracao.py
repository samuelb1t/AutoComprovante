"""
Motor de Extração — Orquestra as estratégias.

Recebe o texto de um PDF e aplica cada estratégia registrada
até que uma retorne os dados com sucesso.
"""

from typing import Optional

from estrategias import ESTRATEGIAS_REGISTRADAS
from models import DadosComprovante


def aplicar_estrategias(texto: str) -> tuple[Optional[DadosComprovante], Optional[str]]:
    """
    Aplica as estratégias registradas ao texto do PDF, uma a uma.

    A primeira estratégia que retornar um DadosComprovante completo vence.

    Args:
        texto: Texto bruto extraído do PDF.

    Returns:
        Tupla (DadosComprovante, nome_estrategia) se sucesso,
        ou (None, None) se nenhuma estratégia conseguiu extrair os dados.
    """
    for estrategia in ESTRATEGIAS_REGISTRADAS:
        resultado = estrategia.extrair(texto)
        if resultado and resultado.esta_completo():
            return resultado, estrategia.nome_estrategia

    return None, None
