"""
Estratégias de Extração — Padrão Strategy.

Cada banco/operação tem uma classe de estratégia separada.
O script principal itera sobre todas e usa a primeira que extrair os 3 campos.

Para adicionar um NOVO banco:
  1. Crie uma classe herdando de EstrategiaExtracao
  2. Implemente extrair(texto)
  3. Registre na lista ESTRATEGIAS_REGISTRADAS
"""

import re
from abc import ABC, abstractmethod
from typing import Optional
from models import DadosComprovante


class EstrategiaExtracao(ABC):
    """Interface base para estratégias de extração."""

    @property
    @abstractmethod
    def nome_estrategia(self) -> str:
        ...

    @abstractmethod
    def extrair(self, texto: str) -> Optional[DadosComprovante]:
        ...


# ── Helpers de Regex ──

def buscar_valor(texto: str, padroes: list[str]) -> Optional[str]:
    """Tenta cada padrão regex na ordem, retorna o primeiro match."""
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    return None


def normalizar_valor(valor_str: str) -> str:
    """Normaliza valor monetário para 'R$ X.XXX,XX'."""
    limpo = re.sub(r'[Rr]\$\s*', '', valor_str).strip()
    if ',' in limpo:
        return f"R$ {limpo}"
    if '.' in limpo:
        partes = limpo.rsplit('.', 1)
        if len(partes) == 2 and len(partes[1]) == 2:
            inteiro = partes[0].replace('.', '')
            return f"R$ {inteiro},{partes[1]}"
    return f"R$ {limpo}"


def normalizar_data(data_str: str) -> str:
    """Normaliza data para DD/MM/AAAA."""
    return re.sub(r'[-.]', '/', data_str.strip())


def _extrair_campos(texto, padroes_nome, padroes_data, padroes_valor):
    """Extrai e normaliza os 3 campos usando listas de padrões regex."""
    dados = DadosComprovante()
    dados.nome = buscar_valor(texto, padroes_nome)
    dados.data = buscar_valor(texto, padroes_data)
    dados.valor = buscar_valor(texto, padroes_valor)
    if dados.data:
        dados.data = normalizar_data(dados.data)
    if dados.valor:
        dados.valor = normalizar_valor(dados.valor)
    return dados if dados.esta_completo() else None


# ═══════════════════════════════════════════
# ESTRATÉGIAS POR BANCO
# ═══════════════════════════════════════════

class ItauPixStrategy(EstrategiaExtracao):
    """Itaú — Pix. Labels: 'nome do destinatário', 'data da transferência', 'valor'."""

    @property
    def nome_estrategia(self): return "Itaú - Pix"

    def extrair(self, texto):
        if not re.search(r'ita[úu]', texto, re.IGNORECASE): return None
        if not re.search(r'pix', texto, re.IGNORECASE): return None
        return _extrair_campos(texto,
            [r'(?:nome\s+do\s+destinat[áa]rio|favorecido|recebedor|nome)\s*[:\-]?\s*(.+)',
             r'(?:para|destinat[áa]rio)\s*[:\-]?\s*([A-ZÀ-Ú][A-Za-zÀ-ú\s\.]+)'],
            [r'(?:data\s+da\s+transfer[êe]ncia|data\s+da\s+transa[çc][ãa]o|data)\s*[:\-]?\s*(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})',
             r'(\d{2}/\d{2}/\d{4})'],
            [r'(?:valor\s+da\s+transfer[êe]ncia|valor\s+pago|valor)\s*[:\-]?\s*R?\$?\s*([\d.,]+)',
             r'R\$\s*([\d.,]+)'])


class ItauBoletoStrategy(EstrategiaExtracao):
    """Itaú — Boleto. Labels: 'beneficiário', 'data do pagamento', 'valor pago'."""

    @property
    def nome_estrategia(self): return "Itaú - Boleto"

    def extrair(self, texto):
        if not re.search(r'ita[úu]', texto, re.IGNORECASE): return None
        if not re.search(r'boleto|pagamento\s+de\s+t[íi]tulo', texto, re.IGNORECASE): return None
        return _extrair_campos(texto,
            [r'(?:benefici[áa]rio|cedente|favorecido)\s*[:\-]?\s*(.+)',
             r'(?:raz[ãa]o\s+social|nome)\s*[:\-]?\s*(.+)'],
            [r'(?:data\s+do\s+pagamento|data\s+de\s+pagamento|data)\s*[:\-]?\s*(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})',
             r'(\d{2}/\d{2}/\d{4})'],
            [r'(?:valor\s+pago|valor\s+total\s+pago)\s*[:\-]?\s*R?\$?\s*([\d.,]+)',
             r'(?:valor\s+do\s+documento|valor)\s*[:\-]?\s*R?\$?\s*([\d.,]+)'])


class BradescoPixStrategy(EstrategiaExtracao):
    """Bradesco — Pix."""

    @property
    def nome_estrategia(self): return "Bradesco - Pix"

    def extrair(self, texto):
        if not re.search(r'bradesco', texto, re.IGNORECASE): return None
        if not re.search(r'pix', texto, re.IGNORECASE): return None
        return _extrair_campos(texto,
            [r'(?:nome\s+do\s+recebedor|recebedor|destinat[áa]rio|favorecido)\s*[:\-]?\s*(.+)',
             r'(?:nome)\s*[:\-]?\s*([A-ZÀ-Ú][A-Za-zÀ-ú\s\.]+)'],
            [r'(?:data\s+da\s+opera[çc][ãa]o|data\s+da\s+transfer[êe]ncia|data)\s*[:\-]?\s*(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})',
             r'(\d{2}/\d{2}/\d{4})'],
            [r'(?:valor\s+da\s+transfer[êe]ncia|valor\s+pago|valor)\s*[:\-]?\s*R?\$?\s*([\d.,]+)',
             r'R\$\s*([\d.,]+)'])


class BradescoBoletoStrategy(EstrategiaExtracao):
    """Bradesco — Boleto."""

    @property
    def nome_estrategia(self): return "Bradesco - Boleto"

    def extrair(self, texto):
        if not re.search(r'bradesco', texto, re.IGNORECASE): return None
        if not re.search(r'boleto|pagamento\s+de\s+t[íi]tulo', texto, re.IGNORECASE): return None
        return _extrair_campos(texto,
            [r'(?:benefici[áa]rio|cedente|favorecido)\s*[:\-]?\s*(.+)',
             r'(?:raz[ãa]o\s+social|nome)\s*[:\-]?\s*(.+)'],
            [r'(?:data\s+do\s+pagamento|data\s+de\s+pagamento|data)\s*[:\-]?\s*(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})',
             r'(\d{2}/\d{2}/\d{4})'],
            [r'(?:valor\s+pago|valor\s+total)\s*[:\-]?\s*R?\$?\s*([\d.,]+)',
             r'(?:valor\s+do\s+documento|valor)\s*[:\-]?\s*R?\$?\s*([\d.,]+)'])


class NubankPixStrategy(EstrategiaExtracao):
    """Nubank — Pix."""

    @property
    def nome_estrategia(self): return "Nubank - Pix"

    def extrair(self, texto):
        if not re.search(r'nubank|nu\s+pagamentos', texto, re.IGNORECASE): return None
        if not re.search(r'pix|transfer[êe]ncia', texto, re.IGNORECASE): return None
        return _extrair_campos(texto,
            [r'(?:nome\s+do\s+destinat[áa]rio|destinat[áa]rio|recebedor|nome)\s*[:\-]?\s*(.+)',
             r'(?:para)\s*[:\-]?\s*([A-ZÀ-Ú][A-Za-zÀ-ú\s\.]+)'],
            [r'(?:data\s+da\s+transfer[êe]ncia|data\s+da\s+transa[çc][ãa]o|data)\s*[:\-]?\s*(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})',
             r'(\d{2}/\d{2}/\d{4})'],
            [r'(?:valor\s+da\s+transfer[êe]ncia|valor\s+enviado|valor)\s*[:\-]?\s*R?\$?\s*([\d.,]+)',
             r'R\$\s*([\d.,]+)'])


class NubankBoletoStrategy(EstrategiaExtracao):
    """Nubank — Boleto."""

    @property
    def nome_estrategia(self): return "Nubank - Boleto"

    def extrair(self, texto):
        if not re.search(r'nubank|nu\s+pagamentos', texto, re.IGNORECASE): return None
        if not re.search(r'boleto|pagamento\s+de\s+conta', texto, re.IGNORECASE): return None
        return _extrair_campos(texto,
            [r'(?:benefici[áa]rio|cedente|favorecido)\s*[:\-]?\s*(.+)',
             r'(?:nome|raz[ãa]o\s+social)\s*[:\-]?\s*(.+)'],
            [r'(?:data\s+do\s+pagamento|pago\s+em|data)\s*[:\-]?\s*(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})',
             r'(\d{2}/\d{2}/\d{4})'],
            [r'(?:valor\s+pago|valor\s+total)\s*[:\-]?\s*R?\$?\s*([\d.,]+)',
             r'(?:valor)\s*[:\-]?\s*R?\$?\s*([\d.,]+)'])


class GenericaStrategy(EstrategiaExtracao):
    """Fallback genérico — tenta padrões comuns a qualquer comprovante brasileiro."""

    @property
    def nome_estrategia(self): return "Genérica (Fallback)"

    def extrair(self, texto):
        return _extrair_campos(texto,
            [r'(?:nome\s+do\s+destinat[áa]rio|destinat[áa]rio|recebedor)\s*[:\-]?\s*(.+)',
             r'(?:benefici[áa]rio|cedente|favorecido)\s*[:\-]?\s*(.+)',
             r'(?:nome|pagador|sacado)\s*[:\-]?\s*([A-ZÀ-Ú][A-Za-zÀ-ú\s\.]{2,})'],
            [r'(?:data\s+(?:da|do|de)\s+\w+)\s*[:\-]?\s*(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})',
             r'(\d{2}/\d{2}/\d{4})'],
            [r'(?:valor\s+(?:pago|da|do|total)\s*\w*)\s*[:\-]?\s*R?\$?\s*([\d.,]+)',
             r'R\$\s*([\d.,]+)'])


# ═══════════════════════════════════════════
# REGISTRO — ordem importa! Específicas primeiro, genérica por último.
# ═══════════════════════════════════════════
ESTRATEGIAS_REGISTRADAS: list[EstrategiaExtracao] = [
    ItauPixStrategy(),
    ItauBoletoStrategy(),
    BradescoPixStrategy(),
    BradescoBoletoStrategy(),
    NubankPixStrategy(),
    NubankBoletoStrategy(),
    GenericaStrategy(),
]
