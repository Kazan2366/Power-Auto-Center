class CategoriaPeca:
    def __init__(self, connection):
        self.connection = connection

    def criar(self, nome, descricao):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO categorias_peca (nome, descricao) VALUES (?, ?)",
            (nome, descricao),
        )
        self.connection.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM categorias_peca ORDER BY id")
        return cur.fetchall()

    def buscar(self, categoria_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM categorias_peca WHERE id = ?", (categoria_id,))
        return cur.fetchone()

    def atualizar(self, categoria_id, nome, descricao):
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE categorias_peca SET nome = ?, descricao = ? WHERE id = ?",
            (nome, descricao, categoria_id),
        )
        self.connection.commit()

    def excluir(self, categoria_id):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM categorias_peca WHERE id = ?", (categoria_id,))
        self.connection.commit()
