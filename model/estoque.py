class Estoque:
    def __init__(self, connection):
        self.connection = connection

    def definir_veiculo(self, modelo_id, quantidade):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO estoque_veiculos (modelo_id, quantidade) VALUES (?, ?) "
            "ON CONFLICT(modelo_id) DO UPDATE SET quantidade = excluded.quantidade",
            (modelo_id, quantidade),
        )
        self.connection.commit()

    def definir_peca(self, peca_id, quantidade):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO estoque_pecas (peca_id, quantidade) VALUES (?, ?) "
            "ON CONFLICT(peca_id) DO UPDATE SET quantidade = excluded.quantidade",
            (peca_id, quantidade),
        )
        self.connection.commit()

    def buscar_veiculo(self, modelo_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM estoque_veiculos WHERE modelo_id = ?", (modelo_id,))
        return cur.fetchone()

    def buscar_peca(self, peca_id):
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM estoque_pecas WHERE peca_id = ?", (peca_id,))
        return cur.fetchone()

    def listar_veiculos(self):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT ev.modelo_id, ev.quantidade, mc.nome AS marca, m.nome AS modelo "
            "FROM estoque_veiculos ev JOIN modelos m ON m.id = ev.modelo_id "
            "LEFT JOIN marcas mc ON mc.id = m.marca_id "
            "ORDER BY ev.modelo_id"
        )
        return cur.fetchall()

    def listar_pecas(self):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT ep.peca_id, ep.quantidade, p.nome "
            "FROM estoque_pecas ep JOIN pecas p ON p.id = ep.peca_id "
            "ORDER BY ep.peca_id"
        )
        return cur.fetchall()

    def total_veiculos(self):
        cur = self.connection.cursor()
        cur.execute("SELECT COALESCE(SUM(quantidade), 0) AS total FROM estoque_veiculos")
        return cur.fetchone()["total"]

    def total_pecas(self):
        cur = self.connection.cursor()
        cur.execute("SELECT COALESCE(SUM(quantidade), 0) AS total FROM estoque_pecas")
        return cur.fetchone()["total"]
