"""Funções utilitárias puras (sem dependência de UI).

Usadas pela camada de backend e disponíveis para o time de frontend.
"""
import re

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def format_currency(value) -> str:
    """Formata um número como moeda brasileira: 1234.5 -> 'R$ 1.234,50'."""
    try:
        valor = float(value or 0)
    except (TypeError, ValueError):
        valor = 0.0
    inteiro = f"{valor:,.2f}"  # 1,234.50
    inteiro = inteiro.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {inteiro}"


def validate_email(email) -> bool:
    return bool(email) and _EMAIL_RE.match(email) is not None


def validate_cpf(cpf) -> bool:
    """Validação simples de formato (11 dígitos). Sem dígito verificador."""
    cpf = "".join(filter(str.isdigit, cpf or ""))
    return len(cpf) == 11


def calculate_total(prices) -> float:
    return sum(prices)
