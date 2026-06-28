import sqlite3
from contextlib import contextmanager


@contextmanager
def duplicidade_amigavel(campo, valor):
    try:
        yield
    except sqlite3.IntegrityError:
        if campo == "usuário":
            raise ValueError(f"Já existe um usuário com o nome '{valor}'.") from None
        raise ValueError(f"Já existe um registro com este {campo}: {valor}.") from None
