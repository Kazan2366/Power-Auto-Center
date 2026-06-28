import logging
import sqlite3

from database.security import hash_password, is_password_hash, verify_password
from model.usuario import Usuario

logger = logging.getLogger(__name__)


class LoginController:
    def __init__(self, connection):
        self.connection = connection
        self.model = Usuario(connection)

    def authenticate(self, username: str, password: str) -> dict:
        """Autentica usuario e retorna role se bem-sucedido."""
        try:
            user = self.model.buscar_por_username(username)

            if user and self._senha_confere(user, password):
                return {
                    "success": True,
                    "role": user["role"],
                    "username": user["username"],
                }

            return {
                "success": False,
                "message": "Usuario ou senha invalidos!",
            }
        except sqlite3.Error:
            logger.exception("Erro de banco ao autenticar usuario")
            return {
                "success": False,
                "message": "Erro ao acessar o sistema. Tente novamente.",
            }

    def _senha_confere(self, user, password):
        stored = user["password"]
        if is_password_hash(stored):
            return verify_password(password, stored)
        if password == stored:
            self._rehash_senha_legada(user["id"], password)
            return True
        return False

    def _rehash_senha_legada(self, user_id, password):
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (hash_password(password), user_id),
        )
        self.connection.commit()
