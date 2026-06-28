from database.security import hash_password, is_password_hash


class Usuario:
    """DAO da tabela `users` (autenticação / perfis de acesso).

    `listar`/`buscar` omitem a coluna `password` (não expõe credenciais para a
    camada de apresentação). Use `buscar_por_username` no fluxo de login.
    """

    def __init__(self, connection):
        self.connection = connection

    def criar(self, username, password, role):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, self._normalizar_senha(password), role),
        )
        self.connection.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.connection.cursor()
        cur.execute("SELECT id, username, role FROM users ORDER BY id")
        return cur.fetchall()

    def buscar(self, user_id):
        cur = self.connection.cursor()
        cur.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,))
        return cur.fetchone()

    def buscar_por_username(self, username):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cur.fetchone()

    def atualizar(self, user_id, username, password, role):
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE users SET username = ?, password = ?, role = ? WHERE id = ?",
            (username, self._normalizar_senha(password), role, user_id),
        )
        self.connection.commit()

    def excluir(self, user_id):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.connection.commit()

    @staticmethod
    def _normalizar_senha(password):
        return password if is_password_hash(password) else hash_password(password)
