class Marca:
    def __init__(self, connection):
        self.connection = connection

    def criar(self, nome):
        cur = self.connection.cursor()
        cur.execute("INSERT INTO marcas (nome) VALUES (?)", (nome,))
        self.connection.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM marcas ORDER BY nome")
        return cur.fetchall()

    def buscar(self, marca_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM marcas WHERE id = ?", (marca_id,))
        return cur.fetchone()

    def atualizar(self, marca_id, nome):
        cur = self.connection.cursor()
        cur.execute("UPDATE marcas SET nome = ? WHERE id = ?", (nome, marca_id))
        self.connection.commit()

    def excluir(self, marca_id):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM marcas WHERE id = ?", (marca_id,))
        self.connection.commit()
