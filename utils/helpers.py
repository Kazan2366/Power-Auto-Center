"""Funções utilitárias puras, sem dependência de UI."""
import re

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
_PLACA_RE = re.compile(r"^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$")
_CHASSI_RE = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")


def format_currency(value) -> str:
    """Formata um número como moeda brasileira: 1234.5 -> 'R$ 1.234,50'."""
    try:
        valor = float(value or 0)
    except (TypeError, ValueError):
        valor = 0.0
    inteiro = f"{valor:,.2f}"
    inteiro = inteiro.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {inteiro}"


def validate_email(email) -> bool:
    return bool(email) and _EMAIL_RE.match(email) is not None


def validate_cpf(cpf) -> bool:
    """Validação simples de formato: 11 dígitos. Sem dígito verificador."""
    cpf = "".join(filter(str.isdigit, cpf or ""))
    return len(cpf) == 11


def validate_placa(placa) -> bool:
    normalizada = "".join(ch for ch in (placa or "").upper() if ch.isalnum())
    return _PLACA_RE.match(normalizada) is not None


def validate_chassi(chassi) -> bool:
    normalizado = "".join(ch for ch in (chassi or "").upper() if ch.isalnum())
    return _CHASSI_RE.match(normalizado) is not None
