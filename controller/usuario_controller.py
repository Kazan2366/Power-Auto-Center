import sqlite3
from contextlib import contextmanager

from model.usuario import Usuario

PAPEIS_VALIDOS = ("cadastro", "vendas", "mecanico", "admin")


@contextmanager
def _duplicidade_amigavel(username):
    """Converte IntegrityError (username único) numa mensagem clara de validação."""
    try:
        yield
    except sqlite3.IntegrityError:
        raise ValueError(f"Já existe um usuário com o nome '{username}'.") from None


class UsuarioController:
    def __init__(self, connection):
        self.model = Usuario(connection)

    def _validar(self, username, password, role):
        if not (username or "").strip():
            raise ValueError("Usuário é obrigatório.")
        if not (password or "").strip():
            raise ValueError("Senha é obrigatória.")
        if role not in PAPEIS_VALIDOS:
            raise ValueError(f"Perfil inválido. Use um de: {', '.join(PAPEIS_VALIDOS)}.")

    def cadastrar(self, username, password, role):
        self._validar(username, password, role)
        username = username.strip()
        with _duplicidade_amigavel(username):
            return self.model.criar(username, password, role)

    def listar(self):
        return [dict(r) for r in self.model.listar()]

    def buscar(self, user_id):
        row = self.model.buscar(user_id)
        return dict(row) if row else None

    def atualizar(self, user_id, username, password, role):
        self._validar(username, password, role)
        username = username.strip()
        with _duplicidade_amigavel(username):
            self.model.atualizar(user_id, username, password, role)

    def excluir(self, user_id):
        self.model.excluir(user_id)
