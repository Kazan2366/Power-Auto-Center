class Modelo:
    def __init__(self, connection):
        self.connection = connection

    def criar(self, nome, numero_serie, marca_id=None):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO modelos (nome, numero_serie, marca_id) VALUES (?, ?, ?)",
            (nome, numero_serie, marca_id),
        )
        self.connection.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT m.*, mc.nome AS marca_nome FROM modelos m "
            "LEFT JOIN marcas mc ON mc.id = m.marca_id ORDER BY m.id"
        )
        return cur.fetchall()

    def listar_por_marca(self, marca_id):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT m.*, mc.nome AS marca_nome FROM modelos m "
            "LEFT JOIN marcas mc ON mc.id = m.marca_id "
            "WHERE m.marca_id = ? ORDER BY m.nome",
            (marca_id,),
        )
        return cur.fetchall()

    def buscar(self, modelo_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM modelos WHERE id = ?", (modelo_id,))
        return cur.fetchone()

    def atualizar(self, modelo_id, nome, numero_serie, marca_id=None):
        cur = self.connection.cursor()
        cur.execute(
            "UPDATE modelos SET nome = ?, numero_serie = ?, marca_id = ? WHERE id = ?",
            (nome, numero_serie, marca_id, modelo_id),
        )
        self.connection.commit()

    def excluir(self, modelo_id):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM modelos WHERE id = ?", (modelo_id,))
        self.connection.commit()
