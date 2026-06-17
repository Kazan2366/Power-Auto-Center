class Peca:
    def __init__(self, connection):
        self.connection = connection

    def criar(self, nome, categoria_id, preco):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO pecas (nome, categoria_id, preco) VALUES (?, ?, ?)",
            (nome, categoria_id, preco),
        )
        self.connection.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM pecas ORDER BY id")
        return cur.fetchall()

    def buscar(self, peca_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM pecas WHERE id = ?", (peca_id,))
        return cur.fetchone()

    def atualizar(self, peca_id, nome, categoria_id, preco):
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE pecas SET nome = ?, categoria_id = ?, preco = ? WHERE id = ?",
            (nome, categoria_id, preco, peca_id),
        )
        self.connection.commit()

    def excluir(self, peca_id):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM pecas WHERE id = ?", (peca_id,))
        self.connection.commit()
