"""
Modelos de dados do projeto.

Define a dataclass que representa os dados extraídos de um comprovante.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DadosComprovante:
    """
    Representa os três campos obrigatórios extraídos de um comprovante bancário.

    Attributes:
        nome: Nome do pagador ou recebedor.
        data: Data da transação (string formatada, ex: '18/04/2026').
        valor: Valor da transação (string formatada, ex: 'R$ 1.234,56').
    """
    nome: Optional[str] = None
    data: Optional[str] = None
    valor: Optional[str] = None

    def esta_completo(self) -> bool:
        """Retorna True se todos os 3 campos foram preenchidos."""
        return all([self.nome, self.data, self.valor])

    def __str__(self) -> str:
        return (
            f"  Nome:  {self.nome or '—'}\n"
            f"  Data:  {self.data or '—'}\n"
            f"  Valor: {self.valor or '—'}"
        )
